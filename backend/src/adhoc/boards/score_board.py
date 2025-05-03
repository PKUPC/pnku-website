from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src import utils
from src.store import SubmissionEvent

from .base import Board


if TYPE_CHECKING:
    from src.state import Game, Team, TeamEvent

    ScoreBoardItemType = tuple[Team, int]


class ScoreBoard(Board):
    MAX_DISPLAY_USERS = 9999999

    def __init__(self, key: str, name: str, desc: str | None, game: Game):
        super().__init__('full', key, name, desc, game)

        self.board: list[ScoreBoardItemType] = []
        self.team_id_to_rank: dict[int, int] = {}

    def _update_board(self) -> None:
        def is_valid(x: ScoreBoardItemType) -> bool:
            team, score = x
            return team.gaming and score >= 0

        def sorter(x: ScoreBoardItemType) -> tuple[Any, ...]:
            team, score = x
            # 小的在前面
            return (
                team.game_status.finished_timestamp_s if team.game_status.finished else 90000000000,
                -score,
                -1 if team.last_success_submission is None else team.last_success_submission.store.id,
                team.model.created_at,
            )

        def is_on_board(team: Team) -> bool:
            if team.is_banned or team.is_hidden or team.is_dissolved:
                return False
            return True

        board = [(team, team.total_score) for team in self._game.teams.list if is_on_board(team)]

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
        return {'detail_url': f'/staff/team-detail?tid={team.model.id}'}

    def _render(self, is_admin: bool) -> dict[str, Any]:
        self._game.worker.log('debug', 'board.render', f'rendering score board {self.name}')

        if is_admin:
            self.etag_admin = utils.gen_random_str(24)
        else:
            self.etag_normal = utils.gen_random_str(24)

        board_begin_ts = self._game.policy.board_setting['begin_ts']
        board_end_ts = self._game.policy.board_setting['end_ts']
        top_star_n = self._game.policy.board_setting['top_star_n']

        return {
            'list': [
                {
                    'r': idx + 1,
                    'id': team.model.id,
                    'n': team.model.team_name or '--',
                    'in': team.model.team_info,
                    'ms': team.leader_and_members,
                    'f': team.game_status.finished,
                    'fts': team.game_status.finished_timestamp_s,
                    's': score,
                    'lts': int(team.last_success_submission.store.created_at / 1000)
                    if team.last_success_submission
                    else None,
                    'g': team.gaming,
                    'bs': team.get_board_badges() + (self._admin_knowledge_badges(team) if is_admin else []),
                    **(self._admin_knowledge_item(team) if is_admin else {}),
                }
                for idx, (team, score) in enumerate(self.board[: self.MAX_DISPLAY_USERS])
            ],
            'topstars': [
                {
                    'n': team.model.team_name,
                    'ss': [
                        [
                            sub.store.created_at,
                            sub.gained_score(),
                        ]
                        for sub in team.success_submissions
                        if sub.store.created_at <= board_end_ts * 1000
                    ],
                }
                for team, score in self.board[:top_star_n]
                if team.gaming and score > 0
            ],
            'time_range': [
                board_begin_ts,
                board_end_ts,
            ],
        }

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.board = []
                self.clear_render_cache()

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent(submission_id=sub_id):
                submission = self._game.submissions_by_id[sub_id]
                if submission.result.type == 'pass' and not is_reloading:
                    self._update_board()
                    self.clear_render_cache()

    def on_team_event_reload_done(self) -> None:
        self._update_board()
        self.clear_render_cache()
