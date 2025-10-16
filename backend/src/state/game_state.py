from __future__ import annotations

from typing import TYPE_CHECKING

from src import secret
from src.adhoc.boards import get_boards
from src.store import GameStartEvent, PuzzleActionEvent, SubmissionEvent

from .announcement_state import Announcements
from .base import WithGameLifecycle
from .game_policy_state import GamePolicy
from .hint_state import Hints
from .message_state import Messages
from .puzzle_state import Puzzles
from .submission_state import Submission
from .team_event_state import TeamEvent
from .team_state import Teams
from .ticket_state import Tickets
from .trigger_state import Trigger
from .user_state import Users


if TYPE_CHECKING:
    from src.adhoc.boards import Board
    from src.logic.base import StateContainerBase
    from src.store import (
        AnnouncementStore,
        GamePolicyStore,
        HintStore,
        MessageStore,
        PuzzleStore,
        TeamEventStore,
        TeamStore,
        TicketMessageStore,
        TicketStore,
        TriggerStore,
        UserStore,
    )


class Game(WithGameLifecycle):
    def __init__(
        self,
        worker: StateContainerBase,
        cur_tick: int,
        game_policy_stores: list[GamePolicyStore],
        trigger_stores: list[TriggerStore],
        announcement_stores: list[AnnouncementStore],
        user_stores: list[UserStore],
        team_stores: list[TeamStore],
        message_stores: list[MessageStore],
        puzzle_stores: list[PuzzleStore],
        hint_stores: list[HintStore],
        team_event_stores: list[TeamEventStore],
        ticket_stores: list[TicketStore],
        ticket_message_stores: list[TicketMessageStore],
        use_boards: bool,
    ):
        self.worker: StateContainerBase = worker
        self.log = self.worker.log
        self.cur_tick: int = cur_tick
        self.need_updating_scoreboard: bool = False
        self.need_reload_team_event: bool = True
        # puzzle key hash
        self.team_and_key_to_hash: dict[tuple[int, str], str] = {}
        self.hash_to_team_and_key: dict[str, tuple[int, str]] = {}
        self.puzzle_key_to_hash: dict[str, str] = {}
        self.hash_to_puzzle_key: dict[str, str] = {}
        # hint id hash
        self.hint_id_to_hash: dict[int, int] = {}
        self.hash_to_hint_id: dict[int, int] = {}
        # submission 是一个特殊的状态
        # submission 应该是 team event 中的一种，但是合并进去又会让处理变得很麻烦
        # 这里的 submission 相当于是 SubmissionEvent 附带的一个状态对象，在 on_team_event 时更新
        self.submission_list: list[Submission] = []
        self.submissions_by_id: dict[int, Submission] = {}
        self.submissions_by_puzzle_key: dict[str, list[Submission]] = {}
        # 以下是独立的 State，不需要考虑构造顺序
        self.trigger: Trigger = Trigger(self, trigger_stores)
        self.policy: GamePolicy = GamePolicy(self, game_policy_stores)
        self.announcements: Announcements = Announcements(self, announcement_stores)
        self.puzzles: Puzzles = Puzzles(self, puzzle_stores)
        # user 表中存了 team_id，而 team 表中没有存 user 信息
        # 因此在恢复时，需要先创建出队伍的 State，然后在创建 UserState 时查找对应的队伍并建立二者之间的联系
        self.teams: Teams = Teams(self, team_stores)
        self.users: Users = Users(self, user_stores)
        # TODO: 还需要再考虑不同状态之间的解耦
        self.messages: Messages = Messages(self, message_stores)
        self.tickets: Tickets = Tickets(self, ticket_stores, ticket_message_stores)
        self.hints: Hints = Hints(self, hint_stores)
        self.team_events: list[TeamEvent] = [TeamEvent(self, x) for x in team_event_stores]

        self.boards: dict[str, Board] = {}
        if use_boards and not secret.PLAYGROUND_MODE:
            self.boards = get_boards(self)

        self.n_corr_submission: int = 0

    def on_tick_change(self) -> None:
        self.policy.on_tick_change()
        self.puzzles.on_tick_change()
        self.users.on_tick_change()
        self.teams.on_tick_change()
        for b in self.boards.values():
            b.on_tick_change()

    def on_preparing_to_reload_team_event(self, reloading_type: str = 'all') -> None:
        match reloading_type:
            case 'all':
                Submission.constructed_ids = set()
                self.submission_list = []
                self.submissions_by_id = {}
                self.submissions_by_puzzle_key = {}
                self.n_corr_submission = 0

                # 游戏核心状态和独立的 user 都无关
                # 需要 reload 的都是保存了过程中状态的类
                # puzzles 保存了通过的队伍等
                # hints 中暂未保存信息
                self.puzzles.on_preparing_to_reload_team_event(reloading_type)
                self.hints.on_preparing_to_reload_team_event(reloading_type)
                self.teams.on_preparing_to_reload_team_event(reloading_type)

                for board in self.boards.values():
                    board.on_preparing_to_reload_team_event(reloading_type)

    def on_team_event(self, event: TeamEvent, is_reloading: bool = False) -> None:
        match event.model.info:
            case SubmissionEvent():
                sub_id = event.model.id
                puzzle_key = event.model.info.puzzle_key
                # 这里不应该有重复的 submission id
                if sub_id in self.submissions_by_id:
                    self.log('error', 'game.on_team_event', f'dropping processed submission #{sub_id}')
                    return

                if not is_reloading:
                    self.log('debug', 'game.on_team_event', f'received submission #{sub_id}')

                submission = Submission(self, event.model)

                self.submission_list.append(submission)
                self.submissions_by_id[sub_id] = submission
                self.submissions_by_puzzle_key.setdefault(puzzle_key, [])
                self.submissions_by_puzzle_key[puzzle_key].append(submission)

                self.puzzles.on_team_event(event, is_reloading)
                self.teams.on_team_event(event, is_reloading)
                for b in self.boards.values():
                    b.on_team_event(event, is_reloading)

                if submission.result.type == 'pass':
                    self.n_corr_submission += 1

            case GameStartEvent():
                if event.team.gaming:
                    self.log('debug', 'game.on_team_event', f'dirty event! game start! Event#{event.model.id}')
                else:
                    event.team.on_team_event(event, is_reloading)
            case PuzzleActionEvent():
                event.team.game_state.on_puzzle_action(event.model.info)
            case _:
                self.puzzles.on_team_event(event, is_reloading)
                self.hints.on_team_event(event, is_reloading)
                self.teams.on_team_event(event, is_reloading)
                for b in self.boards.values():
                    b.on_team_event(event, is_reloading)

    def on_team_event_reload_done(self) -> None:
        self.log(
            'debug', 'game.on_team_event_reload_done', f'batch update received {len(self.team_events)} team events'
        )

        self.teams.on_team_event_reload_done()
        self.hints.on_team_event_reload_done()
        self.puzzles.on_team_event_reload_done()
        for b in self.boards.values():
            b.on_team_event_reload_done()

    def clear_boards_render_cache(self) -> None:
        for b in self.boards.values():
            b.clear_render_cache()

    def is_game_begin(self) -> bool:
        # 游戏开始时间即为排行榜开始时间，硬编码为 1000
        return self.cur_tick >= Trigger.TICK_GAME_START

    def is_game_end(self) -> bool:
        return self.cur_tick >= Trigger.TICK_GAME_END

    def is_intro_unlock(self) -> bool:
        return self.cur_tick >= Trigger.TICK_UNLOCK_INTRO

    @property
    def game_end_ts(self) -> int:
        if self.trigger.TICK_GAME_END in self.trigger.trigger_by_tick:
            return self.trigger.trigger_by_tick[self.trigger.TICK_GAME_END].timestamp_s
        else:
            return Trigger.TS_INF_S

    @property
    def status_id(self) -> int:
        result = 10
        if self.is_game_end():
            result = 40
        elif self.is_game_begin():
            result = 30
        elif self.is_intro_unlock():
            result = 20
        return result

    @property
    def game_begin_timestamp_s(self) -> int:
        return self.trigger.trigger_by_tick[Trigger.TICK_GAME_START].timestamp_s

    def hash_puzzle_key(self, team_id: int, puzzle_key: str) -> str:
        assert puzzle_key in self.puzzles.puzzle_by_key
        assert team_id in self.teams.team_by_id
        if team_id == 0:  # staff 队伍
            return puzzle_key
        if secret.HASH_PUZZLE_KEY == 'none':
            return puzzle_key
        elif secret.HASH_PUZZLE_KEY == 'key_only':
            assert puzzle_key in self.puzzle_key_to_hash
            return self.puzzle_key_to_hash[puzzle_key]
        elif secret.HASH_PUZZLE_KEY == 'key_and_team':
            assert (team_id, puzzle_key) in self.team_and_key_to_hash
            return self.team_and_key_to_hash[(team_id, puzzle_key)]

    def unhash_puzzle_key(self, team_id: int, hashed_key: str) -> tuple[int, str] | tuple[int, None]:
        if team_id == 0:
            if hashed_key in self.puzzles.puzzle_by_key:
                return team_id, hashed_key
            else:
                return -1, None
        # 这里顺带一起判断是否存在
        if secret.HASH_PUZZLE_KEY == 'none':
            if hashed_key not in self.puzzles.puzzle_by_key:
                return -1, None
            return team_id, hashed_key
        elif secret.HASH_PUZZLE_KEY == 'key_only':
            puzzle_key = self.hash_to_puzzle_key.get(hashed_key, None)
            if puzzle_key is None:
                return -1, None
            return team_id, puzzle_key
        elif secret.HASH_PUZZLE_KEY == 'key_and_team':
            rst = self.hash_to_team_and_key.get(hashed_key, None)
            if rst is None:
                return -1, None
            return rst
