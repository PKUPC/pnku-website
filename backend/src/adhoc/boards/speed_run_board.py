from __future__ import annotations

import heapq

from typing import TYPE_CHECKING, Any

from src import utils
from src.adhoc.constants import AREA_NAME
from src.store import SubmissionEvent

from .base import Board


if TYPE_CHECKING:
    from src.state import Game, Team, TeamEvent

    ScoreBoardItemType = tuple[Team, int]


class SpeedRunBoard(Board):
    def __init__(self, key: str, name: str, desc: str | None, game: Game):
        super().__init__('speed_run', key, name, desc, game)
        # puzzle_key: [time_cost, created_at, team_id]
        self.time_cost: dict[str, list[tuple[int, int, int]]] = {}

    def _render(self, is_admin: bool) -> dict[str, Any]:
        self._game.worker.log('debug', 'board.render', f'rendering speed run board {self.name}')

        if is_admin:
            self.etag_admin = utils.gen_random_str(24)
        else:
            self.etag_normal = utils.gen_random_str(24)

        def _filter(item: tuple[int, int, int]) -> bool:
            team_id = item[2]
            team = self._game.teams.team_by_id[team_id]
            return not team.is_banned and not team.is_hidden

        fast_teams: dict[str, list[tuple[str, int]]] = {}
        for puzzle_key, time_cost_list in self.time_cost.items():
            filtered_list = [x for x in time_cost_list if _filter(x)]
            result = heapq.nsmallest(3, filtered_list)
            fast_teams[puzzle_key] = [(self._game.teams.team_by_id[x[2]].model.team_name, x[0]) for x in result]

        def _get_by_idx(key: str, idx: int) -> dict[str, Any] | None:
            if idx + 1 > len(fast_teams.get(key, [])):
                return None
            return {
                'team_name': fast_teams[key][idx][0],
                'time_cost': fast_teams[key][idx][1],
            }

        return {
            'areas': [
                {
                    'name': AREA_NAME.get(area, 'NONE'),
                    'puzzles': [
                        {
                            'title': puzzle.model.title,
                            'key': puzzle.model.key,
                            'first': _get_by_idx(puzzle.model.key, 0),
                            'second': _get_by_idx(puzzle.model.key, 1),
                            'third': _get_by_idx(puzzle.model.key, 2),
                        }
                        for puzzle in self._game.puzzles.puzzle_by_area.get(area, [])
                    ],
                }
                for area in AREA_NAME.keys()
            ]
        }

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.clear_render_cache()

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent():
                submission = self._game.submissions_by_id[event.model.id]
                if submission.result.type != 'pass':
                    return
                puzzle = submission.puzzle
                team = submission.team

                assert puzzle.model.key in team.game_state.unlock_puzzle_keys, '答案正确时肯定已经通过了！'
                time_cost = (
                    int(submission.model.created_at / 1000) - team.game_state.unlock_puzzle_keys[puzzle.model.key]
                )

                self.time_cost.setdefault(puzzle.model.key, [])
                self.time_cost[puzzle.model.key].append((time_cost, submission.model.created_at, team.model.id))

                # TODO: 推送速通榜更新
                # TODO: 目前每次都是全量计算的，但是计算量也不算大，问题应该不是很大

                self.clear_render_cache()

    def on_team_event_reload_done(self) -> None:
        self.clear_render_cache()
