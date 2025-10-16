from __future__ import annotations

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
        # puzzle_key 到标题和花费时间
        self.fast_teams: dict[str, list[tuple[str, int]]] = {}

    def _render(self, is_admin: bool) -> dict[str, Any]:
        self._game.worker.log('debug', 'board.render', f'rendering speed run board {self.name}')

        if is_admin:
            self.etag_admin = utils.gen_random_str(24)
        else:
            self.etag_normal = utils.gen_random_str(24)

        def _get_by_idx(key: str, idx: int) -> dict[str, Any] | None:
            if idx + 1 > len(self.fast_teams.get(key, [])):
                return None
            return {
                'team_name': self.fast_teams[key][idx][0],
                'time_cost': self.fast_teams[key][idx][1],
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
                self.fast_teams = {}
                self.clear_render_cache()

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent():
                submission = self._game.submissions_by_id[event.model.id]
                if submission.result.type != 'pass':
                    return
                puzzle = submission.puzzle
                team = submission.team

                # 队伍已经被封禁了，爬爬爬
                if team.is_hidden or team.is_banned:
                    return

                assert puzzle.model.key in team.game_state.unlock_puzzle_keys, '答案正确时肯定已经通过了！'
                time_cost = (
                    int(submission.model.created_at / 1000) - team.game_state.unlock_puzzle_keys[puzzle.model.key]
                )
                self.fast_teams.setdefault(puzzle.model.key, [])
                record_list = self.fast_teams[puzzle.model.key]
                record_list.append((team.model.team_name, time_cost))
                record_list = sorted(record_list, key=lambda x: x[1])
                if len(record_list) > 3:
                    record_list = record_list[:3]
                self.fast_teams[puzzle.model.key] = record_list

                # TODO: 推送速通榜更新
                # if not is_reloading and updated:
                #     assert submission.user.team is not None
                #     self._game.worker.emit_ws_message({
                #         "type": "speed_run_updated",
                #         "payload": {
                #             "type": "speed_run_updated",
                #             "team_name": submission.user.team.model.team_name,
                #             "puzzle": submission.puzzle.model.title,
                #             "time_cost": time_cost,
                #         },
                #     })

                self.clear_render_cache()

    def on_team_event_reload_done(self) -> None:
        self.clear_render_cache()
