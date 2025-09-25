from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING

from src import secret, utils

from ..team_puzzle_state import SubmissionResult, TeamPuzzleState


if TYPE_CHECKING:
    from src.state import Puzzle, Submission, Team

    from ..team_game_state import TeamGameState


STATE_TO_ANSWER = {1: '韭菜盒子', 2: '花', 3: '密西西比', 4: '一目十行', 5: '乔治盖莫夫'}

ANSWERS = ['韭菜盒子', '花', '密西西比', '一目十行', '乔治盖莫夫']

if secret.DEBUG_MODE:
    COOLDOWN_TIME = 2
else:
    COOLDOWN_TIME = 30


class Day201State(TeamPuzzleState):
    def __init__(self, game_state: TeamGameState, team: Team, puzzle: Puzzle):
        super().__init__(game_state, team, puzzle)
        self.state_id = 1
        self.submission_set_by_id: dict[int, set[str]] = {1: set(), 2: set(), 3: set(), 4: set(), 5: set()}
        self.submission_set = self.submission_set_by_id[1]

    def handle_wrong_submission(self, submission: Submission) -> None:
        self.wrong_count += 1
        cold_down_seconds = self.wrong_count * COOLDOWN_TIME
        if self.wrong_count > 10:
            cold_down_seconds = 10 * COOLDOWN_TIME
        self.cold_down_ts = int(submission.store.created_at / 1000) + cold_down_seconds

    def on_submission(self, submission: Submission, is_reloading: bool = False) -> None:
        assert submission.cleaned_content not in self.submission_set
        self.submission_set.add(submission.cleaned_content)
        match submission.result.type:
            case 'wrong':
                self.handle_wrong_submission(submission)
            case 'milestone':
                self.state_id += 1
                self.submission_set = self.submission_set_by_id[self.state_id]
            case 'pass':
                self.correct_answers.append(submission.result.trigger_value)

    def test_submission(self, submission: str) -> SubmissionResult:
        cleaned_submission = utils.clean_submission(submission)
        if cleaned_submission == utils.clean_submission(STATE_TO_ANSWER[self.state_id]):
            if self.state_id != 5:
                return SubmissionResult('milestone', '答案正确！请继续回答下一个小题。')
            else:
                return SubmissionResult('pass', '答案正确！', trigger_value='乔治盖莫夫')

        return SubmissionResult('wrong', '答案错误！你没有得到任何信息！')

    def get_render_info(self) -> tuple[tuple[str, str | int | tuple[Hashable, ...]], ...]:
        return (('state_id', self.state_id),)
