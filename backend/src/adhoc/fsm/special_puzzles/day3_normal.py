from __future__ import annotations

from typing import TYPE_CHECKING

from src import secret, utils
from src.state.submission_state import SubmissionResult

from ..team_puzzle_status import TeamPuzzleStatus


if TYPE_CHECKING:
    from src.state import Submission

if secret.DEBUG_MODE:
    COOLDOWN_TIME = 6
else:
    COOLDOWN_TIME = 60


class Day3Normal(TeamPuzzleStatus):
    def on_submission(self, submission: Submission, is_reloading: bool = False) -> None:
        assert submission.cleaned_content not in self.submission_set
        self.submission_set.add(submission.cleaned_content)
        match submission.result.type:
            case 'wrong':
                self.wrong_count += 1
                cold_down_seconds = self.wrong_count * COOLDOWN_TIME
                if self.wrong_count > 10:
                    cold_down_seconds = 10 * COOLDOWN_TIME
                self.cold_down_ts = int(submission.store.created_at / 1000) + cold_down_seconds
            case 'pass':
                self.correct_answers.append(submission.result.trigger_value)
            case 'multipass':
                self.correct_answers.append(submission.result.trigger_value)

    def test_submission(self, submission: str) -> SubmissionResult:
        cleaned_submission = utils.clean_submission(submission)
        for trigger in self.puzzle.model.triggers:
            if cleaned_submission == utils.clean_submission(trigger.value):
                result_type, result_info = trigger.type, trigger.info
                if result_type == 'answer':
                    if self.passed:
                        result_type = 'multipass'
                    else:
                        result_type = 'pass'
                if (result_type == 'pass' or result_type == 'multipass') and result_info in ['答案正确', '']:
                    result_info = '答案正确！'
                return SubmissionResult(result_type, result_info, trigger_value=trigger.value)

        return SubmissionResult('wrong', '答案错误！你没有得到任何信息！')
