from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING

from src import secret, utils
from src.state.submission_state import SubmissionResult

from ..team_puzzle_status import TeamPuzzleStatus


if TYPE_CHECKING:
    from src.state import Puzzle, Submission, Team

    from ..team_game_state import TeamGameStatus

STATE_TO_ANSWER = {1: '相', 2: '力', 3: 'SAND', 4: '乏力', 5: '锦', 6: 'tuberose', 7: '巫', 8: 'HANDS'}

ANSWERS = ['相', '力', 'sand', '乏力', '锦', 'tuberose', '巫', 'hands']

if secret.DEBUG_MODE:
    COOLDOWN_TIME = 2
else:
    COOLDOWN_TIME = 30


class Day320Status(TeamPuzzleStatus):
    def __init__(self, game_status: TeamGameStatus, team: Team, puzzle: Puzzle):
        super().__init__(game_status, team, puzzle)
        self.state_id = 1
        self.submission_set_by_id: dict[int, set[str]] = {
            1: set(),
            2: set(),
            3: set(),
            4: set(),
            5: set(),
            6: set(),
            7: set(),
            8: set(),
        }
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
            if self.state_id != 8:
                return SubmissionResult('milestone', '答案正确！请继续回答下一个小题。')
            else:
                return SubmissionResult('pass', '答案正确！', trigger_value='HANDS')

        return SubmissionResult('wrong', '答案错误！你没有得到任何信息！')

    def get_render_info(self) -> tuple[tuple[str, str | int | tuple[Hashable, ...]], ...]:
        return (('state_id', self.state_id),)
