from __future__ import annotations

from typing import TYPE_CHECKING

from src.store import SubmissionEvent, TeamEventStoreModel

from ..utils import clean_submission


if TYPE_CHECKING:
    from src.adhoc.state.team_puzzle_state import SubmissionResult

    from . import Game, Puzzle, Team, User


class Submission:
    constructed_ids: set[int] = set()

    def __init__(self, game: Game, submission_event_model: TeamEventStoreModel):
        assert submission_event_model.id not in Submission.constructed_ids
        Submission.constructed_ids.add(submission_event_model.id)

        self.game: Game = game
        self.model: TeamEventStoreModel = submission_event_model
        assert isinstance(self.model.info, SubmissionEvent)
        self.info: SubmissionEvent = self.model.info

        self.user: User = self.game.users.user_by_id[self.model.user_id]
        assert self.user.team is not None
        self.team: Team = self.user.team

        # 感觉没什么必要考虑提交时题目不存在的情况……为什么会比赛中途删题（？
        self.puzzle: Puzzle = self.game.puzzles.puzzle_by_key[self.model.info.puzzle_key]

        self.cleaned_content = clean_submission(self.model.info.content)

        self.result: SubmissionResult = self.team.game_state.test_submission(
            self.model.info.puzzle_key, self.cleaned_content
        )
        self.finished = False

    @property
    def status(self) -> str:
        return self.result.describe_status()

    def gained_score(self) -> int:
        # 检查是否是在游戏结束后的提交
        if self.model.created_at > self.game.game_end_ts * 1000:
            return 0
        if self.result.type == 'pass':
            return 1
        return 0

    def __repr__(self) -> str:
        assert isinstance(self.model.info, SubmissionEvent)
        return f'[Sub#{self.model.id} U#{self.user.model.id}Puzzle={self.model.info.puzzle_key!r} Flag={self.result}]'
