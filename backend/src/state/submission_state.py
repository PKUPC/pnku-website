from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils import clean_submission


if TYPE_CHECKING:
    from src.adhoc.state.team_puzzle_state import SubmissionResult
    from src.store import SubmissionStore

    from . import Game, Puzzle, Team, User


class Submission:
    constructed_ids: set[int] = set()

    def __init__(self, game: Game, store: SubmissionStore):
        assert store.id not in Submission.constructed_ids, f'{store.id} or {Submission.constructed_ids}'
        Submission.constructed_ids.add(store.id)

        self.game: Game = game
        self.store: SubmissionStore = store

        # foreign key constraint on SubmissionStore ensured user always exist
        assert self.store.user_id in self.game.users.user_by_id
        self.user: User = self.game.users.user_by_id[self.store.user_id]
        assert self.user.team is not None
        self.team: Team = self.user.team
        # 感觉没什么必要考虑提交时题目不存在的情况……为什么会比赛中途删题（？
        assert self.store.puzzle_key in self.game.puzzles.puzzle_by_key
        self.puzzle: Puzzle = self.game.puzzles.puzzle_by_key[self.store.puzzle_key]

        self.cleaned_content = clean_submission(store.content)

        self.result: SubmissionResult = self.team.game_state.test_submission(
            self.store.puzzle_key, self.cleaned_content
        )
        self.finished = False

    @property
    def status(self) -> str:
        return self.result.describe_status()

    def before_game_end(self) -> bool:
        return self.store.created_at < self.game.game_end_ts * 1000

    def gained_score(self) -> int:
        # 检查是否是在游戏结束后的提交
        if self.store.created_at > self.game.game_end_ts * 1000:
            return 0
        if self.result.type == 'pass':
            return 1
        return 0

    def __repr__(self) -> str:
        return f'[Sub#{self.store.id} U#{self.user.model.id}Puzzle={self.store.puzzle_key!r} Flag={self.result}]'
