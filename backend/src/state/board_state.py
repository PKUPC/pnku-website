from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from src.store import SubmissionEvent

from .base import WithGameLifecycle
from .team_event_state import TeamEvent


if TYPE_CHECKING:
    from . import Game, Puzzle, Submission, Team, User

    ScoreBoardItemType = Tuple[Team, int]

from .. import utils


class Board(WithGameLifecycle, ABC):
    def __init__(self, board_type: str, key: str, name: str, desc: Optional[str], game: Game):
        self.board_type = board_type
        self.key = key
        self.name = name
        self.desc = desc
        self._game = game
        self._rendered_admin: Optional[Dict[str, Any]] = None
        self._rendered_normal: Optional[Dict[str, Any]] = None

        self.etag_admin = utils.gen_random_str(24)
        self.etag_normal = utils.gen_random_str(24)

    def get_rendered(self, is_admin: bool) -> Dict[str, Any]:
        if is_admin:
            if self._rendered_admin is None:
                with utils.log_slow(
                    self._game.worker.log, 'board.render', f'render {self.board_type} board (admin) {self.name}'
                ):
                    self._rendered_admin = self._render(is_admin=True)

            return self._rendered_admin
        else:
            if self._rendered_normal is None:
                with utils.log_slow(
                    self._game.worker.log, 'board.render', f'render {self.board_type} board {self.name}'
                ):
                    self._rendered_normal = self._render(is_admin=False)

            return self._rendered_normal

    def get_more_info(self, user: User) -> dict[str, Any]:
        return {}

    def clear_render_cache(self) -> None:
        self._rendered_admin = None
        self._rendered_normal = None

    @staticmethod
    def _admin_knowledge(team: Team) -> List[Dict[str, str]]:
        return [
            {
                'text': 'haha',
                'color': 'default',
            }
        ]

    @abstractmethod
    def _render(self, is_admin: bool) -> Dict[str, Any]:
        raise NotImplementedError()

    def on_tick_change(self) -> None:
        self.clear_render_cache()


class ScoreBoard(Board):
    MAX_DISPLAY_USERS = 9999999

    def __init__(self, key: str, name: str, desc: Optional[str], game: Game):
        super().__init__('full', key, name, desc, game)

        self.board: List[ScoreBoardItemType] = []
        self.team_id_to_rank: dict[int, int] = {}

    def _update_board(self) -> None:
        def is_valid(x: ScoreBoardItemType) -> bool:
            team, score = x
            return team.gaming and score >= 0

        def sorter(x: ScoreBoardItemType) -> Tuple[Any, ...]:
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

    def _render(self, is_admin: bool) -> Dict[str, Any]:
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


class SimpleScoreBoard(Board):
    """
    一种简单的只按照分数排名的排行榜
    添加排行榜时需要同步更新 puzzle.on_simple_board, team.last_success_submission_by_board, team.score_by_board
    """

    def __init__(self, key: str, name: str, desc: Optional[str], game: Game):
        super().__init__('simple', key, name, desc, game)

        self.board: List[ScoreBoardItemType] = []
        self.team_id_to_rank: dict[int, int] = {}

    def _update_board(self) -> None:
        def is_valid(x: ScoreBoardItemType) -> bool:
            team, score = x
            return team.gaming and score > 0

        def sorter(x: ScoreBoardItemType) -> Tuple[Any, ...]:
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
        return {'detail_url': f'/staff/team-detail?tid={team.model.id}'}

    def _render(self, is_admin: bool) -> dict[str, Any]:
        self._game.worker.log('debug', 'board.render', f'rendering simple score board {self.key}')

        if is_admin:
            self.etag_admin = utils.gen_random_str(24)
        else:
            self.etag_normal = utils.gen_random_str(24)

        return {
            'list': [
                {
                    'r': idx + 1,
                    'n': team.model.team_name or '--',
                    'in': team.model.team_info,
                    'ms': team.leader_and_members,
                    's': score,
                    'lts': (
                        int(
                            team.last_success_submission_by_board.get(self.key, None).store.created_at / 1000  # type:ignore[union-attr]
                        )
                        if team.last_success_submission_by_board.get(self.key, None) is not None
                        else None
                    ),
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
            case SubmissionEvent(submission_id=sub_id):
                submission = self._game.submissions_by_id[sub_id]
                if submission.result.type == 'pass' and not is_reloading:
                    if submission.puzzle.on_simple_board(self.key):
                        self._update_board()
                        self.clear_render_cache()

    def on_team_event_reload_done(self) -> None:
        self._update_board()
        self.clear_render_cache()


class FirstBloodBoard(Board):
    def __init__(self, key: str, name: str, desc: Optional[str], game: Game):
        super().__init__('firstblood', key, name, desc, game)

        self.puzzle_board: dict[Puzzle, Submission] = {}

    def _render(self, is_admin: bool) -> Dict[str, Any]:
        self._game.worker.log('debug', 'board.render', f'rendering first blood board {self.name}')

        if is_admin:
            self.etag_admin = utils.gen_random_str(24)
        else:
            self.etag_normal = utils.gen_random_str(24)

        # ADHOC!!
        area_key_to_title = {'day1': '素青', 'day2': '秋蝉', 'day3': '临水'}

        return {
            'list': [
                {
                    'name': area_key_to_title.get(area, 'NONE'),
                    'list': [
                        {
                            'title': puzzle.model.title,
                            'key': puzzle.model.key,
                            # submission 中的 user 一定有 team
                            'team_name': submission.user.team.model.team_name  # type: ignore[union-attr]
                            if submission is not None
                            else None,
                            'timestamp': int(submission.store.created_at / 1000) if submission is not None else None,
                        }
                        for puzzle in self._game.puzzles.puzzle_by_area.get(area, [])
                        for submission in [self.puzzle_board.get(puzzle, None)]
                    ],
                }
                for area in ['day1', 'day2', 'day3']  # 这里保证一下顺序
            ]
        }

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.puzzle_board = {}
                self.clear_render_cache()

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent(submission_id=sub_id):
                submission = self._game.submissions_by_id[sub_id]
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


class SpeedRunBoard(Board):
    def __init__(self, key: str, name: str, desc: Optional[str], game: Game):
        super().__init__('speed_run', key, name, desc, game)
        # puzzle_key 到标题和花费时间
        self.fast_teams: dict[str, list[tuple[str, int]]] = {}

    def _render(self, is_admin: bool) -> Dict[str, Any]:
        self._game.worker.log('debug', 'board.render', f'rendering speed run board {self.name}')

        if is_admin:
            self.etag_admin = utils.gen_random_str(24)
        else:
            self.etag_normal = utils.gen_random_str(24)

        # ADHOC!!
        AREA_NAME = {'day1': '素青', 'day2': '秋蝉', 'day3': '临水'}

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
                for area in ['day1', 'day2', 'day3']  # 这里保证一下顺序
            ]
        }

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        match reloading_type:
            case 'all':
                self.fast_teams = {}
                self.clear_render_cache()

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        match event.model.info:
            case SubmissionEvent(submission_id=sub_id):
                submission = self._game.submissions_by_id[sub_id]
                if submission.result.type != 'pass':
                    return
                puzzle = submission.puzzle
                team = submission.team

                # 队伍已经被封禁了，爬爬爬
                if team.is_hidden or team.is_banned:
                    return

                assert puzzle.model.key in team.game_status.unlock_puzzle_keys, '答案正确时肯定已经通过了！'
                time_cost = (
                    int(submission.store.created_at / 1000) - team.game_status.unlock_puzzle_keys[puzzle.model.key]
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
