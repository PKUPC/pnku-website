from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src import utils
from src.adhoc.constants import AREA_NAME
from src.store import SubmissionEvent

from .base import Board


if TYPE_CHECKING:
    from src.state import Game, Puzzle, Submission, Team, TeamEvent

    ScoreBoardItemType = tuple[Team, int]


class FirstBloodBoard(Board):
    def __init__(self, key: str, name: str, desc: str | None, game: Game):
        super().__init__('firstblood', key, name, desc, game)

        self.puzzle_board: dict[Puzzle, Submission] = {}

    def _render(self, is_admin: bool) -> dict[str, Any]:
        self._game.worker.log('debug', 'board.render', f'rendering first blood board {self.name}')

        if is_admin:
            self.etag_admin = utils.gen_random_str(24)
        else:
            self.etag_normal = utils.gen_random_str(24)

        return {
            'list': [
                {
                    'name': AREA_NAME.get(area, 'NONE'),
                    'list': [
                        {
                            'title': puzzle.model.title,
                            'key': puzzle.model.key,
                            # submission 中的 user 一定有 team
                            'team_name': submission.user.team.model.team_name  # type: ignore[union-attr]
                            if submission is not None
                            else None,
                            'timestamp': int(submission.model.created_at / 1000) if submission is not None else None,
                        }
                        for puzzle in self._game.puzzles.puzzle_by_area.get(area, [])
                        for submission in [self.puzzle_board.get(puzzle, None)]
                    ],
                }
                for area in AREA_NAME.keys()
            ]
        }

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.puzzle_board = {}
                self.clear_render_cache()

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent():
                submission = self._game.submissions_by_id[event.model.id]
                if submission.result.type != 'pass':
                    return

                assert submission.puzzle is not None, 'correct submission to no puzzle'
                # 已经不是一血了！
                if submission.puzzle in self.puzzle_board:
                    return
                # 队伍已经被封禁了，爬爬爬
                if submission.team.is_banned or submission.team.is_hidden:
                    return

                self.puzzle_board[submission.puzzle] = submission
                # 批量更新时不推送一血消息
                if not is_reloading:
                    assert submission.user.team is not None
                    self._game.worker.emit_ws_message(
                        {
                            'type': 'first_blood',
                            'payload': {
                                'type': 'puzzle_first_blood',
                                'board_name': self.name,
                                'team_name': submission.user.team.model.team_name,
                                'puzzle_key': submission.puzzle.model.key,
                                'puzzle': submission.puzzle.model.title,
                            },
                        }
                    )

                self.clear_render_cache()

    def on_team_event_reload_done(self) -> None:
        self.clear_render_cache()
