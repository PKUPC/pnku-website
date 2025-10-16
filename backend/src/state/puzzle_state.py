from __future__ import annotations

from collections.abc import Hashable
from functools import lru_cache
from typing import TYPE_CHECKING, Literal

from src import utils
from src.adhoc.puzzle import gen_puzzles_by_structure
from src.store import SubmissionEvent

from .base import WithGameLifecycle


if TYPE_CHECKING:
    from src.store import PuzzleStore

    from . import Game, Submission, Team, TeamEvent, User


class Puzzles(WithGameLifecycle):
    constructed: bool = False

    def __init__(self, game: Game, stores: list[PuzzleStore]):
        assert not Puzzles.constructed
        Puzzles.constructed = True
        self.game: Game = game
        self.stores: list[PuzzleStore] = []

        self.list: list[Puzzle] = []
        self.puzzle_by_id: dict[int, Puzzle] = {}
        self.puzzle_by_key: dict[str, Puzzle] = {}
        self.puzzle_by_area: dict[str, list[Puzzle]] = {}
        self.puzzles_by_structure: dict[str, dict[str, list[Puzzle]]] = {}

        self.on_store_reload(stores)

    def _after_puzzle_changed(self) -> None:
        self.list = sorted(self.list, key=lambda x: x.model.sorting_index)
        self.puzzle_by_id = {p.model.id: p for p in self.list}
        self.puzzle_by_key = {p.model.key: p for p in self.list}
        self.puzzles_by_structure = gen_puzzles_by_structure(self.list)
        self.puzzle_by_area = {}
        for puzzle in self.list:
            self.puzzle_by_area.setdefault(puzzle.model.category, [])
            self.puzzle_by_area[puzzle.model.category].append(puzzle)

    def on_store_reload(self, stores: list[PuzzleStore]) -> None:
        self.stores = stores
        self.list = [Puzzle(self.game, store) for store in stores]
        self._after_puzzle_changed()
        # 更改了题目内容，由于可能修改了题目答案或者里程碑，因此需要重新计算 team event
        # TODO: 可以有更细致的检查，在某些情况下可以不用全部更新
        self.game.need_reload_team_event = True

    def on_store_update(self, puzzle_id: int, new_store: PuzzleStore | None) -> None:
        old_puzzle: Puzzle | None = ([x for x in self.list if x.model.id == puzzle_id] + [None])[0]
        other_puzzles = [x for x in self.list if x.model.id != puzzle_id]

        if new_store is None:  # remove
            self.list = other_puzzles
            self.game.need_reload_team_event = True
        elif old_puzzle is None:  # add
            self.list = other_puzzles + [Puzzle(self.game, new_store)]
            self.game.need_reload_team_event = True
        else:  # modify
            old_puzzle.on_store_reload(new_store)

        self._after_puzzle_changed()

        self.game.clear_boards_render_cache()  # if puzzle name or metadata changed

    def on_tick_change(self) -> None:
        for ch in self.list:
            ch.on_tick_change()

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        for puzzle in self.list:
            puzzle.on_preparing_to_reload_team_event(reloading_type)

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent():
                submission = self.game.submissions_by_id[event.model.id]
                submission.puzzle.on_team_event(event, is_reloading)
            case _:
                for puzzle in self.list:
                    puzzle.on_team_event(event, is_reloading)


class Puzzle(WithGameLifecycle):
    constructed_ids: set[int] = set()

    def __init__(self, game: Game, store: PuzzleStore):
        assert store.id not in Puzzle.constructed_ids
        Puzzle.constructed_ids.add(store.id)

        self.game: Game = game
        self._store: PuzzleStore = store
        self.model = self._store.validated_model()

        self.passed_teams: set[Team] = set()
        self.attempted_teams: set[Team] = set()

        self.passed_submissions: set[Submission] = set()

        self.on_store_reload(store)

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.passed_teams = set()
                self.attempted_teams = set()
                self.passed_submissions = set()

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent():
                submission = self.game.submissions_by_id[event.model.id]
                assert submission.puzzle is self

                if not submission.team.is_staff_team:
                    if submission.result.type == 'pass':
                        self.passed_teams.add(submission.team)
                        self.attempted_teams.add(submission.team)
                        self.passed_submissions.add(submission)
                    else:
                        self.attempted_teams.add(submission.team)

    def on_store_reload(self, store: PuzzleStore) -> None:
        # 目前的设计中暂时不允许在线上修改 puzzle key（因为没必要），这里的检查暂时没用。
        if store.key != self._store.key:
            self.game.need_reload_team_event = True
        if str(store.triggers) != str(self._store.triggers):
            self.game.need_reload_team_event = True

        # 勘误部分修改后会向玩家发送一条实时通知
        if store.errata_template != self._store.errata_template:
            self.game.worker.emit_ws_message(
                {
                    'type': 'puzzle_errata',
                    'puzzle_key': self.model.key,
                }
            )

        self._store = store
        self.model = self._store.validated_model()

        self._render_template.cache_clear()
        self.on_tick_change()

    # ADHOC!
    def on_simple_board(self, board_key: str) -> bool:
        match board_key:
            case _:
                return False

    def status_by_team(self, team: Team) -> Literal['passed', 'partial', 'untouched']:
        if team in self.passed_teams:
            return 'passed'
        elif team in self.attempted_teams:
            return 'partial'
        else:
            return 'untouched'

    def difficulty_status(self) -> dict[str, int]:
        display_setting = self.game.policy.puzzle_passed_display
        total_num = len(display_setting)
        green_num = 0
        red_num = 0

        # 只要下一档有人，就算下一个档 touched
        if len(self.attempted_teams) > 0:
            for x in display_setting:
                red_num += 1
                if len(self.attempted_teams) <= x:
                    break

        # 必须当前档全部通过才算 passed
        for x in display_setting:
            if len(self.passed_teams) < x:
                break
            green_num += 1

        # 如果所有尝试数量和正确数量相等，则 green_num 应该等于 red_num
        # 在上面的写法中，如果已经进入了某一档，但是没有塞满这个挡位，即使全对也会有一个红色
        if len(self.passed_teams) == len(self.attempted_teams):
            green_num = red_num

        return {
            'total_num': total_num,
            'green_num': green_num,
            'red_num': red_num - green_num,
        }

    def render_desc(self, user: User) -> str:
        extra: tuple[tuple[str, str | int | tuple[Hashable, ...]], ...] = tuple()
        is_finished = False
        if user.team is not None:
            extra = user.team.game_state.get_render_info(self.model.key)
            is_finished = user.team.game_state.finished
        return self._render_template(
            tick=self.game.cur_tick,
            passed=user.team in self.passed_teams or user.model.group == 'staff',
            is_staff=user.is_staff,
            is_finished=is_finished,
            is_archived=False,
            extra=extra,
        )

    def render_desc_for_archive(self, extra: tuple[tuple[str, str | int | tuple[Hashable, ...]], ...] = tuple()) -> str:
        return self._render_template(
            tick=self.game.cur_tick, passed=False, is_staff=False, is_finished=False, is_archived=True, extra=extra
        )

    @lru_cache(32)
    def _render_template(
        self,
        tick: int = 0,
        passed: bool = False,
        is_staff: bool = False,
        is_finished: bool = False,
        is_archived: bool = False,
        extra: tuple[tuple[str, str | int], ...] | None = None,
    ) -> str:
        render_dict: dict[str, str | int] = {
            'tick': tick,
            'passed': passed,
            'is_staff': is_staff,
            'is_finished': is_finished,
            'is_archived': is_archived,
        }
        if extra is not None:
            for item in extra:
                render_dict[item[0]] = item[1]
        print('rendering', self.model.title, render_dict)
        try:
            return utils.render_template(self.model.errata_template + self.model.content_template, render_dict)
        except Exception as e:
            self.game.worker.log(
                'error',
                'announcement.render_template',
                f'template render failed: {self.model.key} ({self.model.title}): {utils.get_traceback(e)}',
            )
            return '<i>（模板渲染失败）</i>'

    def __repr__(self) -> str:
        return f'[Puzzle#{self.model.key}: {self.model.title}]'
