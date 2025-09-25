import asyncio
import sys
import time
import traceback


# noinspection PyUnresolvedReferences
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, TypeVar

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from zmq.asyncio import Context

from src import secret, utils
from src.state import (
    Game,
    Hint,
    Hints,
    Puzzle,
    Puzzles,
    Submission,
    Team,
    TeamEvent,
    Teams,
    Ticket,
    Tickets,
    User,
    Users,
)
from src.store import (
    AnnouncementStore,
    GamePolicyStore,
    HintStore,
    LogStore,
    MessageStore,
    PuzzleStore,
    SubmissionEvent,
    SubmissionStore,
    Table,
    TeamEventStore,
    TeamStore,
    TicketMessageStore,
    TicketStore,
    TriggerStore,
    UserStore,
)

from . import glitter, pusher
from .checker import Checker
from .utils import make_callback_decorator


T = TypeVar('T', bound=Table)


class StateContainerBase(ABC):
    RECOVER_THROTTLE_S = 1
    MAX_KEEPING_MESSAGES = 32

    on_event, event_listeners = make_callback_decorator('StateContainerBase')

    def __init__(self, process_name: str, receiving_messages: bool = False, use_boards: bool = True):
        self.process_name: str = process_name
        self.listening_ws_messages: bool = receiving_messages
        self.use_boards = use_boards

        self.push_message = pusher.Pusher().push_message

        # https://docs.sqlalchemy.org/en/20/core/pooling.html#using-fifo-vs-lifo
        self.SqlSession = sessionmaker(
            create_engine(secret.DB_CONNECTOR, future=True, pool_size=2, pool_use_lifo=True, pool_pre_ping=True),
            expire_on_commit=False,
            future=True,
        )

        self.log('debug', 'base.__init__', f'{self.process_name} started')

        self.glitter_ctx: Context = Context()

        # initialized later in self.init_game
        self._game: Game = None  # type: ignore[assignment]
        self.checker: Checker = None  # type: ignore[assignment]
        self.game_dirty: bool = True
        self.debug_reinit = False

        self._submission_stores: dict[int, SubmissionStore] = {}

        self.ws_messages: dict[int, dict[str, Any]] = {}
        self.next_message_id: int = 1
        self.message_cond: asyncio.Condition = None  # type: ignore[assignment]

        self.state_counter: int = 1
        self.custom_telemetry_data: dict[str, Any] = {}

    @property
    def game(self) -> Game | None:
        if self.game_dirty:
            return None
        return self._game

    @property
    def game_nocheck(self) -> Game:
        return self._game

    @property
    def submission_stores(self) -> dict[int, SubmissionStore]:
        return self._submission_stores

    async def init_game(self, tick: int) -> None:
        failed_cnt = 0
        while True:
            # 重新初始化状态
            Teams.constructed = False
            Team.constructed_ids = set()
            Users.constructed = False
            User.constructed_ids = set()
            Hints.constructed = False
            Hint.constructed_ids = set()
            Puzzles.constructed = False
            Puzzle.constructed_ids = set()
            TeamEvent.constructed_ids = set()
            Tickets.constructed = False
            Ticket.constructed_ids = set()
            Submission.constructed_ids = set()
            try:
                self._game = Game(
                    worker=self,
                    cur_tick=tick,
                    game_policy_stores=self.load_all_data(GamePolicyStore),
                    trigger_stores=self.load_all_data(TriggerStore),
                    announcement_stores=self.load_all_data(AnnouncementStore),
                    user_stores=self.load_all_data(UserStore),
                    team_stores=self.load_all_data(TeamStore),
                    message_stores=self.load_all_data(MessageStore),
                    puzzle_stores=self.load_all_data(PuzzleStore),
                    hint_stores=self.load_all_data(HintStore),
                    team_event_stores=self.load_all_data(TeamEventStore),
                    ticket_stores=self.load_all_data(TicketStore),
                    ticket_message_stores=self.load_all_data(TicketMessageStore),
                    use_boards=self.use_boards,
                )
                self._game.on_tick_change()
                self.checker = Checker(self._game)

                self._submission_stores = {sub.id: sub for sub in self.load_all_data(SubmissionStore)}
                self.reload_or_update_if_needed()
                failed_cnt = 0
            except Exception as e:
                self.log(
                    'error',
                    'base.init_game',
                    f'exception during initialization, will try again: {utils.get_traceback(e)}',
                )
                failed_cnt += 1
                if failed_cnt == 3:
                    self.log('error', 'base.init_game', 'dead!')
                    break
                await asyncio.sleep(self.RECOVER_THROTTLE_S)
            else:
                break

    async def _before_run(self) -> None:
        self.message_cond = asyncio.Condition()

    @abstractmethod
    async def _mainloop(self) -> None:
        raise NotImplementedError()

    async def run_forever(self) -> None:
        await self._before_run()

        # _before_run should call init_game to initialize `self.game` field
        assert self._game is not None, 'game state not initialized in _before_run'
        assert not self.game_dirty, 'game state should be set to not dirty after _before_run'

        await self._mainloop()

    @on_event(glitter.EventType.SYNC)
    def on_sync(self, event: glitter.Event) -> None:
        if self._game.cur_tick != event.data:
            self.log('error', 'base.on_sync', f'tick is inconsistent: ours {self._game.cur_tick}, synced {event.data}')
            self._game.cur_tick = event.data
            self._game.on_tick_change()

    @on_event(glitter.EventType.REINIT_GAME)
    def on_reinit(self, _event: glitter.Event) -> None:
        self.debug_reinit = True

    @on_event(glitter.EventType.RELOAD_GAME_POLICY)
    def on_reload_game_policy(self, _event: glitter.Event) -> None:
        self._game.policy.on_store_reload(self.load_all_data(GamePolicyStore))

    @on_event(glitter.EventType.RELOAD_TRIGGER)
    def on_reload_trigger(self, _event: glitter.Event) -> None:
        self._game.trigger.on_store_reload(self.load_all_data(TriggerStore))

    @on_event(glitter.EventType.UPDATE_ANNOUNCEMENT)
    def on_update_announcement(self, event: glitter.Event) -> None:
        self._game.announcements.on_store_update(event.data, self.load_one_data(AnnouncementStore, event.data))

    @on_event(glitter.EventType.UPDATE_PUZZLE)
    def on_update_puzzle(self, event: glitter.Event) -> None:
        self._game.puzzles.on_store_update(event.data, self.load_one_data(PuzzleStore, event.data))

    @on_event(glitter.EventType.UPDATE_HINT)
    def on_update_hint(self, event: glitter.Event) -> None:
        self._game.hints.on_store_update(event.data, self.load_one_data(HintStore, event.data))

    @on_event(glitter.EventType.UPDATE_USER)
    def on_update_user(self, event: glitter.Event) -> None:
        self._game.users.on_store_update(event.data, self.load_one_data(UserStore, event.data))

    @on_event(glitter.EventType.CREATE_TEAM)
    def on_user_create_team(self, event: glitter.Event) -> None:
        assert self.game is not None
        # 先创建一个新的 Team 对象，然后要更新 User 的 store
        team_store = self.load_one_data(TeamStore, event.data)
        assert team_store is not None
        self.game.teams.on_create_team(event.data, team_store)
        user_id = team_store.leader_id
        self.game.users.on_create_team(user_id, self.load_one_data(UserStore, user_id))

    @on_event(glitter.EventType.UPDATE_TEAM_INFO)
    def on_update_team_info(self, event: glitter.Event) -> None:
        assert self.game is not None
        self.game.teams.on_update_team_info(event.data, self.load_one_data(TeamStore, event.data))

    @on_event(glitter.EventType.TEAM_GAME_BEGIN)
    def on_team_game_begin(self, event: glitter.Event) -> None:
        event_id = event.data
        event_store = self.load_one_data(TeamEventStore, event_id)
        assert event_store is not None, f'event#{event_id} not exists.'
        team_event = TeamEvent(self._game, event_store)
        self._game.team_events.append(team_event)
        self._game.on_team_event(team_event)

    @on_event(glitter.EventType.JOIN_TEAM)
    def on_user_join_team(self, event: glitter.Event) -> None:
        assert self.game is not None
        self.game.users.on_join_team(event.data, self.load_one_data(UserStore, event.data))

    @on_event(glitter.EventType.LEAVE_TEAM)
    def on_user_leave_team(self, event: glitter.Event) -> None:
        assert self.game is not None
        self.game.users.on_leave_team(event.data, self.load_one_data(UserStore, event.data))

    @on_event(glitter.EventType.DISSOLVE_TEAM)
    def on_dissolve_team(self, event: glitter.Event) -> None:
        assert self.game is not None
        # 先让每个 user 都离队，都要重新加载 store，然后再处理 team
        team_id = event.data
        assert team_id in self.game.teams.team_by_id
        # 这里需要注意，不能直接遍历 members 列表，因为 users.on_leave_team 中会删除 members 的成员，应该先保留一个 id 列表
        member_ids = [member.model.id for member in self.game.teams.team_by_id[team_id].members]
        for member_id in member_ids:
            self.game.users.on_leave_team(member_id, self.load_one_data(UserStore, member_id))
        # 这里应该删除完了
        assert len(self.game.teams.team_by_id[team_id].members) == 0, '解散队伍时，members 没有如期清空'
        self.game.teams.on_dissolve_team(team_id, self.load_one_data(TeamStore, team_id))

    @on_event(glitter.EventType.CHANGE_TEAM_LEADER)
    def on_change_team_leader(self, event: glitter.Event) -> None:
        assert self.game is not None
        self.game.teams.on_change_team_leader(event.data, self.load_one_data(TeamStore, event.data))

    @on_event(glitter.EventType.NEW_SUBMISSION)
    def on_new_submission(self, event: glitter.Event) -> None:
        event_id = event.data
        event_store = self.load_one_data(TeamEventStore, event_id)
        assert event_store is not None, 'event store is None'
        team_event = TeamEvent(self._game, event_store)
        assert isinstance(team_event.model.info, SubmissionEvent), f'submission_id error: {event_store.info}'
        # 添加 submission store
        sub_store = self.load_one_data(SubmissionStore, team_event.model.info.submission_id)
        assert sub_store is not None, 'submission not found'
        self._submission_stores[sub_store.id] = sub_store
        self._game.team_events.append(team_event)
        self._game.on_team_event(team_event)
        assert sub_store.id in self._game.submissions_by_id

    def internal_on_new_message(self, msg_id: int) -> None:
        msg_store = self.load_one_data(MessageStore, msg_id)
        assert msg_store is not None, 'message not found'
        self._game.messages.on_new_message(msg_store)

        # 不管是从哪个方向来的信息，都需要发给能参与这个对话的每个人
        to_list = list(self._game.users.staff_ids) + [
            x.model.id for x in self._game.teams.team_by_id[msg_store.team_id].members
        ]

        self.emit_ws_message(
            {
                'type': 'normal',
                'to_users': to_list,
                'payload': {
                    'type': 'new_message',
                    'direction': 'to_staff' if msg_store.direction == MessageStore.DIRECTION.TO_STAFF else 'to_user',
                    'team_id': msg_store.team_id,
                    'team_name': self._game.teams.team_by_id[msg_store.team_id].model.team_name,
                    'sender_id': None if msg_store.direction == MessageStore.DIRECTION.TO_USER else msg_store.user_id,
                },
            }
        )

    @on_event(glitter.EventType.NEW_MSG)
    def on_new_message(self, event: glitter.Event) -> None:
        self.internal_on_new_message(event.data)

    @on_event(glitter.EventType.UPDATE_MESSAGE)
    def on_update_message(self, event: glitter.Event) -> None:
        msg_store = self.load_one_data(MessageStore, event.data)
        assert msg_store is not None, 'message not found'
        self._game.messages.on_update_message(msg_store)

    @on_event(glitter.EventType.TEAM_EVENT_RECEIVED)
    def on_team_event_received(self, event: glitter.Event) -> None:
        event_store = self.load_one_data(TeamEventStore, event.data)
        assert event_store is not None
        team_event = TeamEvent(self._game, event_store)
        self._game.team_events.append(team_event)
        self._game.on_team_event(team_event)

    @on_event(glitter.EventType.STAFF_READ_MSG)
    def on_staff_read_message(self, event: glitter.Event) -> None:
        msg_store = self.load_one_data(MessageStore, event.data)
        assert msg_store is not None, 'message not found'
        self._game.messages.on_staff_read_message(msg_store.team_id, msg_store.id)

    @on_event(glitter.EventType.PLAYER_READ_MSG)
    def on_player_read_message(self, event: glitter.Event) -> None:
        msg_store = self.load_one_data(MessageStore, event.data)
        assert msg_store is not None, 'message not found'
        self._game.messages.on_player_read_message(msg_store.team_id, msg_store.id)

    # TODO: 这个之后要清理了
    @on_event(glitter.EventType.UPDATE_SUBMISSION)
    def on_update_submission(self, event: glitter.Event) -> None:
        sub_store = self.load_one_data(SubmissionStore, event.data)
        if sub_store is None:  # remove sub, not likely, but possible
            self._submission_stores.pop(event.data, None)
        else:
            self._submission_stores[event.data] = sub_store

        self._game.need_reload_team_event = True

    @on_event(glitter.EventType.TEAM_CREATE_TICKET)
    def on_team_create_ticket(self, event: glitter.Event) -> None:
        first_message = self.load_one_data(TicketMessageStore, event.data)
        assert first_message is not None
        ticket = self.load_one_data(TicketStore, first_message.ticket_id)
        assert ticket is not None
        self._game.tickets.on_create_ticket(ticket, first_message)

        user = self._game.users.user_by_id[ticket.user_id]
        assert user.team is not None
        # 不管是从哪个方向来的信息，都需要发给能参与这个对话的每个人， 虽然不一定要给所有人发通知，但是需要让他们更新 message
        to_list = list(self._game.users.staff_ids) + [x for x in user.team.member_ids if x != user.model.id]

        extra_info: str | None = None
        if ticket.type == TicketStore.TicketType.MANUAL_HINT.name:
            extra_info = (
                '题目标题为：' + self._game.puzzles.puzzle_by_key[ticket.extra['puzzle_key']].model.title + '。'
            )

        self.emit_ws_message(
            {
                'type': 'normal',
                'to_users': to_list,
                'payload': {
                    'type': 'new_ticket',
                    'team_id': user.team.model.id,
                    'team_name': user.team.model.team_name,
                    'ticket_type': TicketStore.TicketType.dict().get(ticket.type, '未知'),
                    'extra_info': extra_info,
                },
            }
        )

    @on_event(glitter.EventType.TICKET_MESSAGE)
    def on_ticket_message(self, event: glitter.Event) -> None:
        message = self.load_one_data(TicketMessageStore, event.data)
        assert message is not None
        self._game.tickets.on_ticket_message(message)

        user = self._game.users.user_by_id[message.user_id]
        assert user.team is not None
        # 不管是从哪个方向来的信息，都需要发给能参与这个对话的每个人， 虽然不一定要给所有人发通知，但是需要让他们更新 message
        ticket = self._game.tickets.ticket_by_id[message.ticket_id]
        to_list = list(self._game.users.staff_ids) + ticket.team.member_ids
        extra_info: str | None = None
        if ticket.model.type == TicketStore.TicketType.MANUAL_HINT.name:
            extra_info = (
                '题目标题为：' + self._game.puzzles.puzzle_by_key[ticket.model.extra.puzzle_key].model.title + '。'
            )

        self.emit_ws_message(
            {
                'type': 'normal',
                'to_users': to_list,
                'payload': {
                    'type': 'new_ticket_message',
                    'ticket_type': TicketStore.TicketType.dict().get(ticket.model.type, '未知'),
                    'extra_info': extra_info,
                    'direction': message.direction,
                    'team_id': user.team.model.id,
                    'team_name': user.team.model.team_name,
                    'sender_id': None
                    if message.direction == TicketMessageStore.Direction.TO_PLAYER.name
                    else message.user_id,
                },
            }
        )

    @on_event(glitter.EventType.UPDATE_TICKET_MESSAGE)
    def on_update_ticket_message(self, event: glitter.Event) -> None:
        msg_store = self.load_one_data(TicketMessageStore, event.data)
        assert msg_store is not None, 'ticket message not found'
        self._game.tickets.on_update_ticket_message(msg_store)

    @on_event(glitter.EventType.TICKET_UPDATE)
    def on_ticket_update(self, event: glitter.Event) -> None:
        ticket = self.load_one_data(TicketStore, event.data)
        assert ticket is not None
        old_state = self._game.tickets.ticket_by_id[ticket.id]
        user = self._game.users.user_by_id[ticket.user_id]
        assert user.team is not None
        # 对于队伍来说，如果工单变成了
        to_list = list(self._game.users.staff_ids) + user.team.member_ids
        if old_state.model.status != ticket.status:
            # ADHOC
            self.emit_ws_message(
                {
                    'type': 'normal',
                    'to_users': to_list,
                    'payload': {
                        'type': 'ticket_status_update',
                        'status': ticket.status,
                    },
                }
            )
        old_state.on_store_update(ticket)

    @on_event(glitter.EventType.TICK_UPDATE)
    def on_tick_update(self, event: glitter.Event) -> None:
        old_tick = self._game.cur_tick
        if old_tick != event.data:
            self._game.cur_tick = event.data
            self._game.on_tick_change()

            if event.data in self._game.trigger.trigger_by_tick:
                self.emit_ws_message(
                    {
                        'type': 'normal',
                        'payload': {
                            'type': 'tick_update',
                            'new_tick_name': self._game.trigger.trigger_by_tick[event.data].name,
                        },
                    }
                )

    @on_event(glitter.EventType.ANNOUNCEMENT_PUBLISH)
    def on_announcement_publish(self, _event: glitter.Event) -> None:
        now_time = int(time.time())
        self.log(
            'debug',
            'base.on_announcement_publish',
            f'now: {utils.format_timestamp(now_time)}, next: {utils.format_timestamp(self._game.announcements.next_announcement_ts)}',
        )
        while now_time >= self._game.announcements.next_announcement_ts:
            next_announcement = self._game.announcements.next_announcement
            assert next_announcement is not None
            self.emit_ws_message(
                {
                    'type': 'new_announcement',
                    'category': next_announcement.store.category,
                    'payload': {
                        'type': 'new_announcement',
                        'title': next_announcement.store.title,
                    },
                }
            )
            self._game.announcements.last_push_time = next_announcement.timestamp_s
            self.log('info', 'base.on_announcement_publish', f'publish announcement: {next_announcement}')

        self._game.announcements.last_push_time = now_time

    def reload_or_update_if_needed(self) -> None:
        if self._game.need_reload_team_event:
            self.log('debug', 'base.reload_scoreboard_if_needed', 'need_reload_team_event')
            with utils.log_slow(self.log, 'base.reload_scoreboard_if_needed', 'need_reload_team_event'):
                self._game.on_preparing_to_reload_team_event()
                for team_event in self._game.team_events:
                    self._game.on_team_event(team_event, is_reloading=True)
                self._game.on_team_event_reload_done()
            self._game.need_reload_team_event = False
            self._game.need_updating_scoreboard = False
        elif self._game.need_updating_scoreboard:
            self.log('debug', 'base.reload_scoreboard_if_needed', 'need update')
            with utils.log_slow(self.log, 'base.update_scoreboard_if_needed', 'update scoreboard'):
                self._game.on_team_event_reload_done()
            self._game.need_updating_scoreboard = False

    def log(self, level: utils.LogLevel, module: str, message: str) -> None:
        log_str = '[' + datetime.now(UTC).astimezone().strftime('%Y-%m-%d %H:%M:%S %z') + '] '
        log_str += f'[{self.process_name}] [{level.upper()}] [{module}]'
        log_str += f' {message}'
        if level in secret.STDOUT_LOG_LEVEL:
            print(log_str)
        if level in secret.STDERR_LOG_LEVEL:
            print(log_str, file=sys.stderr)

        if level in secret.DB_LOG_LEVEL:
            with self.SqlSession() as session:
                log = LogStore(level=level, process=self.process_name, module=module, message=message)
                session.add(log)
                session.commit()

        if level in secret.PUSH_LOG_LEVEL:
            asyncio.get_event_loop().create_task(
                self.push_message(f'[{self.process_name}] [{level.upper()} {module}]\n{message}', f'log-{level}')
            )

    def load_all_data(self, cls: type[T]) -> list[T]:
        """
        给定一个 Store 类，重新载入所有的数据
        """
        with self.SqlSession() as session:
            return list(session.execute(select(cls).order_by(cls.id)).scalars().all())

    def load_one_data(self, cls: type[T], data_id: int) -> T | None:
        """
        给定一个 Store 类和数据库中的主键 id，更新这个数据
        """
        with self.SqlSession() as session:
            return session.execute(select(cls).where(cls.id == data_id)).scalar()

    async def process_event(self, event: glitter.Event) -> None:
        def default(_self: Any, ev: glitter.Event) -> None:
            self.log('warning', 'base.process_event', f'unknown event: {ev.type!r}')

        listener: Callable[[StateContainerBase, glitter.Event], None] = self.event_listeners.get(event.type, default)

        try:
            with utils.log_slow(self.log, 'base.process_event', f'handle event {event.type}'):
                listener(self, event)
            self.reload_or_update_if_needed()
            if self.debug_reinit:
                self.debug_reinit = False
                self.game_dirty = True
                await self.init_game(self._game.cur_tick)
                self.game_dirty = False
                await asyncio.sleep(self.RECOVER_THROTTLE_S)

        except Exception as e:
            self.log(
                'critical', 'base.process_event', f'exception during handling event {event.type}, will recover: {e!r}'
            )
            traceback.print_exc()
            self.game_dirty = True
            await self.init_game(self._game.cur_tick)
            self.game_dirty = False
            await asyncio.sleep(self.RECOVER_THROTTLE_S)

    def emit_ws_message(self, msg: dict[str, Any]) -> None:
        if not self.listening_ws_messages:
            return

        if msg.get('type', None) != 'heartbeat_sent':
            self.log('debug', 'base.emit_ws_message', f'emit message {msg.get("type", None)}')

        self.ws_messages[self.next_message_id] = msg

        deleted_message = self.next_message_id - self.MAX_KEEPING_MESSAGES
        if deleted_message in self.ws_messages:
            del self.ws_messages[deleted_message]

        self.next_message_id += 1

        async def notify_waiters() -> None:
            async with self.message_cond:
                self.message_cond.notify_all()

        asyncio.get_event_loop().create_task(notify_waiters())

    def collect_telemetry(self) -> dict[str, Any]:
        return {
            'state_counter': self.state_counter,
            'game_available': not self.game_dirty,
            **(
                {
                    'cur_tick': self._game.cur_tick,
                    'n_users': len(self._game.users.list),
                    'n_submissions': len(self._game.submissions_by_id),
                }
                if not self.game_dirty
                else {}
            ),
            **self.custom_telemetry_data,
        }

    def collect_game_stat(self) -> tuple[dict[str, dict[str, int]], dict[str, int], dict[str, int]]:
        USER_STATUS = {
            'total': '总数',
            'disabled': '已禁用',
            'have_team': '已组队',
            'not_have_team': '未组队',
        }
        TEAM_STATUS = {
            'total': '总数',
            'dissolved': '已解散',
            'disabled': '已禁用',
            'hide': '已隐藏',
            'preparing': '准备中',
            'gaming': '游戏中',
        }

        TEAM_STATISTICS = {
            'count_1': '1 人',
            'count_2': '2 人',
            'count_3': '3 人',
            'count_4': '4 人',
            'count_5': '5 人',
            'average': '平均人数',
        }

        users_cnt_by_group: dict[str, dict[str, int]] = {}
        for key in USER_STATUS:
            users_cnt_by_group.setdefault('staff', {}).setdefault(key, 0)
            users_cnt_by_group.setdefault('player', {}).setdefault(key, 0)
        for u in self._game.users.list:
            u_group = u.model.group
            if u_group not in ['staff', 'player']:
                continue
            users_cnt_by_group[u_group]['total'] += 1
            if not u.model.enabled:
                users_cnt_by_group[u_group]['disabled'] += 1
            if u.team is not None:
                users_cnt_by_group[u_group]['have_team'] += 1
            else:
                users_cnt_by_group[u_group]['not_have_team'] += 1

        users_cnt_by_group['staff']['have_team'] = '---'  # type: ignore[assignment]
        users_cnt_by_group['staff']['not_have_team'] = '---'  # type: ignore[assignment]

        teams_cnt: dict[str, int] = {}
        teams_statistic_cnt: dict[str, int] = {}
        for key in TEAM_STATUS:
            teams_cnt.setdefault(key, 0)
        for key in TEAM_STATISTICS:
            teams_statistic_cnt.setdefault(key, 0)

        for team in self._game.teams.list:
            teams_cnt['total'] += 1
            if team.is_banned:
                teams_cnt['disabled'] += 1
            elif team.is_hidden:
                teams_cnt['hide'] += 1
            if team.preparing:
                teams_cnt['preparing'] += 1
            elif team.gaming:
                teams_cnt['gaming'] += 1

            if len(team.members) == 1:
                teams_statistic_cnt['count_1'] += 1
            elif len(team.members) == 2:
                teams_statistic_cnt['count_2'] += 1
            elif len(team.members) == 3:
                teams_statistic_cnt['count_3'] += 1
            elif len(team.members) == 4:
                teams_statistic_cnt['count_4'] += 1
            elif len(team.members) == 5:
                teams_statistic_cnt['count_5'] += 1

        teams_cnt['dissolved'] = len(self._game.teams.dissolved_list)
        if teams_cnt['total'] > 0:
            average = users_cnt_by_group['player']['have_team'] / teams_cnt['total']
            teams_statistic_cnt['average'] = f'{average:.2}'  # type: ignore[assignment]
        else:
            teams_statistic_cnt['average'] = '---'  # type: ignore[assignment]
        # 先算平均，再把解散的加进来
        teams_cnt['total'] = teams_cnt['total'] + teams_cnt['dissolved']

        return users_cnt_by_group, teams_cnt, teams_statistic_cnt
