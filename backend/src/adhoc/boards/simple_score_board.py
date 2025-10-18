from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src import utils
from src.store import SubmissionEvent

from .base import Board


if TYPE_CHECKING:
    from src.state import Game, Team, TeamEvent

    ScoreBoardItemType = tuple[Team, int]


class SimpleScoreBoard(Board):
    """
    一种简单的只按照分数排名的排行榜（MiaoHunt 2023 中使用，现在没有维护）
    """

    def __init__(self, key: str, name: str, desc: str | None, game: Game):
        super().__init__('simple', key, name, desc, game)

        self.board: list[ScoreBoardItemType] = []
        self.team_id_to_rank: dict[int, int] = {}

    def _update_board(self) -> None:
        def is_valid(x: ScoreBoardItemType) -> bool:
            team, score = x
            return team.gaming and score > 0

        def sorter(x: ScoreBoardItemType) -> tuple[Any, ...]:
            team, score = x
            # 小的在前面
            return (
                -score,
                (
                    -1
                    if team.last_success_submission_by_board.get(self.key, None) is None
                    else team.last_success_submission_by_board[self.key].store.id  # type:ignore[union-attr]
                ),
                team.model.created_at,
            )

        def is_on_board(team: Team) -> bool:
            if team.is_banned or team.is_hidden or team.is_dissolved:
                return False
            return True

        board = [(team, team.score_by_board.get(self.key, 0)) for team in self._game.teams.list if is_on_board(team)]

        self.board = sorted([x for x in board if is_valid(x)], key=sorter)
        self.team_id_to_rank = {team.model.id: idx + 1 for idx, (team, score) in enumerate(self.board)}

    @staticmethod
    def _admin_knowledge_badges(team: Team) -> list[dict[str, str]]:
        return [
            {
                'text': '#' + str(team.model.id),
                'color': 'default',
            }
        ]

    @staticmethod
    def _admin_knowledge_item(team: Team) -> dict[str, str]:
        return {'detail_url': f'/staff/team-detail/{team.model.id}'}

    def _render(self, is_admin: bool) -> dict[str, Any]:
        self._game.worker.log('debug', 'board.render', f'rendering simple score board {self.key}')

        if is_admin:
            self.etag_admin = utils.gen_random_str(24)
        else:
            self.etag_normal = utils.gen_random_str(24)

        def _format_last_success_submission(team: Team) -> int | None:
            sub = team.last_success_submission_by_board.get(self.key, None)
            if sub is None:
                return None
            return sub.model.created_at // 1000

        return {
            'list': [
                {
                    'r': idx + 1,
                    'n': team.model.team_name or '--',
                    'in': team.model.team_info,
                    'ms': team.leader_and_members,
                    's': score,
                    'lts': _format_last_success_submission(team),
                    'bs': team.get_board_badges() + (self._admin_knowledge_badges(team) if is_admin else []),
                    **(self._admin_knowledge_item(team) if is_admin else {}),
                }
                for idx, (team, score) in enumerate(self.board)
            ],
        }

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.board = []
                self.clear_render_cache()

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent():
                submission = self._game.submissions_by_id[event.model.id]
                if submission.result.type == 'pass' and not is_reloading:
                    if submission.puzzle.on_simple_board(self.key):
                        self._update_board()
                        self.clear_render_cache()

    def on_team_event_reload_done(self) -> None:
        self._update_board()
        self.clear_render_cache()
