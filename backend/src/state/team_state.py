from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from src import secret
from src.adhoc.constants.enums import CurrencyType
from src.adhoc.state import StaffTeamGameState, TeamGameState
from src.adhoc.state.currency import CurrencyEvent
from src.store import (
    BuyNormalHintEvent,
    GameStartEvent,
    StaffModifyCurrencyEvent,
    SubmissionEvent,
    TeamStore,
)
from src.store.puzzle_store import PuzzleType

from .. import utils
from .base import WithGameLifecycle


if TYPE_CHECKING:
    from . import Game, Submission, TeamEvent, User


class Teams(WithGameLifecycle):
    constructed: bool = False

    def __init__(self, game: Game, stores: list[TeamStore]):
        #
        assert not Teams.constructed
        Teams.constructed = True
        #
        self.game: Game = game
        self._stores: list[TeamStore] = []
        self.list: list[Team] = []
        self.dissolved_list: list[Team] = []
        #
        self.team_by_id: dict[int, Team] = {}
        self.team_name_set: set[str] = set()

        self._stores = stores
        self.team_name_set = set()
        self.list = [(StaffTeam(self.game, STAFF_TEAM_STORE))]
        self.list.extend([Team(self.game, x) for x in self._stores if x.status != TeamStore.Status.DISSOLVED.name])
        self.dissolved_list = [Team(self.game, x) for x in self._stores if x.status == TeamStore.Status.DISSOLVED.name]
        self.team_by_id = {t.model.id: t for t in self.list}
        for team in self.list:
            self._add_team_name_and_key_hash(team)

    def _add_team_name_and_key_hash(self, team: Team) -> None:
        self.team_name_set.add(team.model.team_name)
        for puzzle_key in self.game.puzzles.puzzle_by_key:
            puzzle = self.game.puzzles.puzzle_by_key[puzzle_key]
            # 对于 PUBLIC 类型的题目，没有必要进行 key hash

            if secret.HASH_PUZZLE_KEY == 'key_and_team':
                if puzzle.model.puzzle_metadata.type == PuzzleType.PUBLIC:
                    key_hash = puzzle_key
                else:
                    key_hash = utils.calc_sha1(secret.PUZZLE_KEY_HASH_SALT + str((team.model.id, puzzle_key)))
                    while key_hash in self.game.hash_to_team_and_key:
                        key_hash = utils.calc_sha1(key_hash)

                self.game.team_and_key_to_hash[(team.model.id, puzzle_key)] = key_hash
                self.game.hash_to_team_and_key[key_hash] = (team.model.id, puzzle_key)
            elif secret.HASH_PUZZLE_KEY == 'key_only':
                if puzzle.model.puzzle_metadata.type == PuzzleType.PUBLIC:
                    key_hash = puzzle_key
                else:
                    key_hash = utils.calc_sha1(secret.PUZZLE_KEY_HASH_SALT + puzzle_key)
                    while key_hash in self.game.hash_to_puzzle_key:
                        key_hash = utils.calc_sha1(key_hash)

                self.game.puzzle_key_to_hash[puzzle_key] = key_hash
                self.game.hash_to_puzzle_key[key_hash] = puzzle_key

    def on_create_team(self, team_id: int, store: TeamStore | None) -> None:
        assert store is not None and team_id == store.id and team_id not in self.team_by_id
        new_team = Team(self.game, store)
        # 和用户绑定
        team_leader = self.game.users.user_by_id[store.leader_id]
        new_team.leader = team_leader
        team_leader.team = new_team
        new_team.members.append(team_leader)
        self.list.append(new_team)
        self.team_by_id[team_id] = new_team
        self._add_team_name_and_key_hash(new_team)

        self.game.need_updating_scoreboard = True

    def on_update_team_info(self, team_id: int, store: TeamStore | None) -> None:
        assert store is not None
        # 只需要更换对应 Team 对象的 store 即可
        assert team_id in self.team_by_id
        if self.team_by_id[team_id].model.team_name in self.team_name_set:
            self.team_name_set.remove(self.team_by_id[team_id].model.team_name)
        self.team_name_set.add(store.team_name)
        self.team_by_id[team_id].on_store_update(store)
        self.game.need_updating_scoreboard = True

    def on_dissolve_team(self, team_id: int, store: TeamStore | None) -> None:
        assert store is not None
        assert team_id in self.team_by_id
        # 这个时候应该对象已经被清空了
        assert len(self.team_by_id[team_id].members) == 0
        # self.team_by_id[team_id].on_store_update(store)  # 没有用
        # 添加到解散队伍中
        self.dissolved_list.append(self.team_by_id[team_id])
        # 删除掉此队伍
        self.team_name_set.remove(self.team_by_id[team_id].model.team_name)
        self.list.remove(self.team_by_id[team_id])
        del self.team_by_id[team_id]

        self.game.need_updating_scoreboard = True

    def on_change_team_leader(self, team_id: int, store: TeamStore | None) -> None:
        assert store is not None
        assert team_id in self.team_by_id
        self.team_by_id[team_id].on_store_update(store)
        self.team_by_id[team_id].leader = self.game.users.user_by_id[store.leader_id]
        self.game.clear_boards_render_cache()

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        for team in self.list:
            team.on_preparing_to_reload_team_event(reloading_type)

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        event.team.on_team_event(event, is_reloading)

    def on_team_event_reload_done(self) -> None:
        for team in self.list:
            team.on_team_event_reload_done()


class Team(WithGameLifecycle):
    constructed_ids: set[int] = set()

    def __init__(self, game: Game, store: TeamStore):
        assert store.id not in Team.constructed_ids
        Team.constructed_ids.add(store.id)
        #
        self.game: Game = game
        self._store: TeamStore = store
        self.model = self._store.validated_model()
        # staff 权限
        self.is_staff_team = False
        # 在恢复 User 状态时设置
        self.members: list[User] = []
        # 对于没有被解散的队伍，leader 一定存在，会在用户创建后设置
        self.leader: User = None  # type: ignore[assignment]

        # 以下是游戏相关的信息
        self.last_success_submission_by_board: dict[str, Submission | None] = {}

        # 我们这里先简单的把分数设置为过的题目的数量
        self.total_score: int = 0
        self.score_by_board: dict[str, int] = {}

        self.team_events: list[TeamEvent] = []

        # 货币的变化量，按货币种类分
        self.currency_change_event: dict[CurrencyType, list[TeamEvent]] = defaultdict(list)

        # 购买过的提示
        self.bought_hint_ids: set[int] = set()

        # 游戏解锁状态
        self.game_state: TeamGameState = TeamGameState(self, self.game.puzzles.list)

    # 以前是 gaming 和 gaming_timestamp_s 是在这里，现在挪到了 TeamGameState 中
    # 这里添加一些 property 兼容以前的代码逻辑

    @property
    def preparing(self) -> bool:
        return self.game_state.preparing

    @property
    def gaming(self) -> bool:
        return self.game_state.gaming

    @property
    def game_start_time(self) -> int:
        return self.game_state.gaming_timestamp_s

    @property
    def creat_time(self) -> int:
        return self.model.created_at // 1000

    @property
    def is_banned(self) -> int:
        return self.model.ban_status == TeamStore.BanStatus.BANNED.name

    @property
    def is_hidden(self) -> int:
        return self.model.ban_status == TeamStore.BanStatus.HIDDEN.name

    @property
    def is_dissolved(self) -> int:
        return self.model.status == TeamStore.Status.DISSOLVED.name

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.last_success_submission_by_board = {}
                self.total_score = 0
                self.score_by_board = {}
                self.team_events = []
                self.currency_change_event = defaultdict(list)
                self.bought_hint_ids = set()
                self.game_state = TeamGameState(self, self.game.puzzles.list)
                # self.game.log("debug", "team.on_preparing_to_reload_team_event", f"T#{self.model.id} done!")

    def on_team_event(self, event: TeamEvent, is_reloading: bool = False) -> None:
        if not is_reloading:
            self.game.log('info', 'team.on_team_event', f'team#{self.model.id} got {event.model.info.type} event.')

        match event.model.info:
            case SubmissionEvent():
                submission = self.game.submissions_by_id[event.model.id]
                self.game_state.on_submission(submission, is_reloading)
                if submission.result.type == 'pass':
                    for _, board in self.game.boards.items():
                        if submission.puzzle.on_simple_board(board.key):
                            self.last_success_submission_by_board[board.key] = submission

                    if not is_reloading:
                        self._update_single_score(submission)

                # 不管是否通过都发推送
                if not is_reloading:
                    origin_key = submission.puzzle.model.key
                    hash_key = self.game.hash_puzzle_key(self.model.id, origin_key)
                    event_user = self.game.users.user_by_id[event.model.user_id]
                    self.game.worker.emit_ws_message(
                        {
                            'type': 'normal',
                            'to_users': [x for x in self.member_ids if x != event.model.user_id],
                            'payload': {
                                'type': 'teammate_action',
                                'action': 'submission',
                                'puzzle_key': hash_key,
                                'message': (
                                    f'你的队友 {event_user.model.user_info.nickname} 在题目 {submission.puzzle.model.title}'
                                    f'中提交了答案。提交结果：{submission.result.describe_status()}。'
                                ),
                            },
                        }
                    )

            case GameStartEvent():
                # gaming 是一个根据 team event 决定的状态
                assert not self.game_state.gaming
                self.game.need_updating_scoreboard = True
                self.game_state.on_game_start(event.model.created_at // 1000, is_reloading)
                if not is_reloading:
                    self.game.worker.emit_ws_message(
                        {'type': 'normal', 'to_users': self.member_ids, 'payload': {'type': 'game_start'}}
                    )
            case StaffModifyCurrencyEvent():
                info = event.model.info
                if info.delta == 0:
                    return
                self.game_state.on_currency_event(CurrencyEvent(event), is_reloading)

            case BuyNormalHintEvent(hint_id=hint_id):
                # 可能出现在 hind 被删除的时候
                if hint_id not in self.game.hints.hint_by_id:
                    return
                if hint_id in self.bought_hint_ids:
                    self.game.log(
                        'warning',
                        'team.on_team_event.BuyNormalHintEvent',
                        f'[event#{event.model.id}][team#{self.model.id}] hint_id {hint_id} already bought',
                    )
                    return
                self.bought_hint_ids.add(hint_id)
                self.game_state.on_currency_event(CurrencyEvent(event), is_reloading)

        self.team_events.append(event)

    def on_team_event_reload_done(self) -> None:
        self._update_total_score()

    @property
    def status(self) -> str:
        # 注意！ 不应当用 team.store.status 了，之后会被移除
        if self.game_state.gaming:
            return 'gaming'
        if self.game_state.preparing:
            return 'preparing'
        return self.model.status  # TODO: 未来会被移除

    def on_store_reload(self, store: TeamStore) -> None:
        # 这个方法感觉有点没用，暂时先放在这里
        self.on_store_update(store)

    def on_store_update(self, store: TeamStore) -> None:
        self.game.worker.log('debug', 'TeamState', f'team#{self.model.id} on_store_update')
        # 从 normal 切换到其他状态
        # 需要更新排行榜
        if self.model.ban_status != store.ban_status:
            self.game.need_updating_scoreboard = True
        self._store = store
        self.model = store.validated_model()

    def _update_total_score(self) -> None:
        self.total_score = 0
        self.score_by_board = {}

        for puzzle, submission in self.game_state.passed_puzzles:
            score = submission.gained_score()
            for board in self.game.boards:
                board_key = self.game.boards[board].key
                # TODO: 之后需要将这部分逻辑挪出去
                if puzzle.on_simple_board(board_key):
                    self.score_by_board.setdefault(board_key, 0)
                    self.score_by_board[board_key] += score
            self.total_score += score

    def _update_single_score(self, submission: Submission) -> None:
        score = submission.gained_score()
        for board in self.game.boards:
            board_key = self.game.boards[board].key
            if submission.puzzle.on_simple_board(board_key):
                self.score_by_board.setdefault(board_key, 0)
                self.score_by_board[board_key] += score
        self.total_score += score

    def get_submissions_by_puzzle_key(self, puzzle_key: str) -> list[Submission]:
        return [x for x in self.game_state.submissions if x.info.puzzle_key == puzzle_key]

    def get_currency_change_list_by_type(self, currency_type: CurrencyType) -> list[dict[str, str | int]]:
        return self.game_state.get_currency_history(currency_type)

    @property
    def cur_currency(self) -> dict[CurrencyType, int]:
        return {currency_type: self.game_state.get_current_balance(currency_type) for currency_type in CurrencyType}

    def cur_currency_by_type(self, currency_type: CurrencyType) -> int:
        return self.game_state.get_current_balance(currency_type)

    @property
    def last_success_submission(self) -> Submission | None:
        return self.game_state.success_submissions[-1] if len(self.game_state.success_submissions) > 0 else None

    @property
    def last_submission(self) -> Submission | None:
        return self.game_state.submissions[-1] if len(self.game_state.submissions) > 0 else None

    @property
    def leader_and_members(self) -> list[str]:
        nickname = self.leader.model.user_info.nickname
        rst = [nickname]
        for member in self.members:
            if member != self.leader:
                rst.append(member.model.user_info.nickname)
        return rst

    @property
    def leader_and_members_modal(self) -> list[User]:
        rst = [self.leader]
        for member in self.members:
            if member != self.leader:
                rst.append(member)
        return rst

    @property
    def member_info_list(self) -> list[dict[str, str]]:
        leader_email = self.leader.model.user_info.email
        rst = [
            {
                'nickname': self.leader.model.user_info.nickname,
                'avatar_url': f'https://cravatar.cn/avatar/{utils.calc_md5(leader_email)}?d=mp',
                'type': 'leader',
            }
        ]
        for member in self.members:
            if member != self.leader:
                member_email = member.model.user_info.email
                rst.append(
                    {
                        'nickname': member.model.user_info.nickname,
                        'avatar_url': f'https://cravatar.cn/avatar/{utils.calc_md5(member_email)}?d=mp',
                        'type': 'member',
                    }
                )

        return rst

    @property
    def member_ids(self) -> list[int]:
        return [t.model.id for t in self.members]

    def get_disp_list(self) -> list[dict[str, str]]:
        rst = []
        if self.preparing:
            rst.append({'text': '未开始游戏', 'color': 'blue'})
        elif self.gaming:
            rst.append({'text': '已开始游戏', 'color': 'blue'})
        # 是否完赛
        if self.game_state.finished:
            rst.append({'text': '已完赛', 'color': 'green'})
        # 是否封禁
        if self.model.ban_status == TeamStore.BanStatus.BANNED.name:
            rst.append({'text': '已封禁', 'color': 'red'})
        elif self.model.ban_status == TeamStore.BanStatus.HIDDEN.name:
            rst.append({'text': '在排行榜隐藏', 'color': 'orange'})
        else:
            pass
        # 额外的状态
        rst.extend([x.to_dict() for x in self.model.extra_info.special_status])

        return rst

    def get_board_badges(self) -> list[dict[str, str]]:
        rst = []
        rst.extend([x.to_dict() for x in self.model.extra_info.special_status])
        return rst

    def __repr__(self) -> str:
        return repr(self._store)


class StaffTeam(Team):
    def __init__(self, game: Game, store: TeamStore):
        super().__init__(game, store)
        self.is_staff_team = True
        self.game_state = StaffTeamGameState(self, self.game.puzzles.list)

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.last_success_submission_by_board = {}
                self.total_score = 0
                self.score_by_board = {}
                self.team_events = []
                self.currency_change_event = defaultdict(list)
                self.bought_hint_ids = set()
                self.game_state = StaffTeamGameState(self, self.game.puzzles.list)
                self.is_staff_team = True
                # self.game.log("debug", "team.on_preparing_to_reload_team_event", f"T#{self.model.id} done!")

    def on_team_event(self, event: TeamEvent, is_reloading: bool = False) -> None:
        if not is_reloading:
            self.game.log('info', 'team.on_team_event', f'team#{self.model.id} got {event.model.info.type} event.')

        match event.model.info:
            case SubmissionEvent():
                submission = self.game.submissions_by_id[event.model.id]
                self.game_state.on_submission(submission, is_reloading)

        self.team_events.append(event)

    def on_team_event_reload_done(self) -> None:
        self._update_total_score()

    def get_disp_list(self) -> list[dict[str, str]]:
        super_rst = super().get_disp_list()
        return [{'text': '不存在的队伍！', 'color': 'magenta'}] + super_rst


STAFF_TEAM_STORE = TeamStore(
    id=0,
    created_at=0,
    updated_at=0,
    team_name='工作人员',
    team_info='kinami 问这里该写点什么，JC 建议是直接把能想到的关键词都堆上去，Winfrid 说要来点名人名言，所以：\n鸣谢榆木华！',
    leader_id=1,
    team_secret='Winfrid saikou!',
    status='NORMAL',
    ban_status='HIDDEN',
    extra_info={},
)
