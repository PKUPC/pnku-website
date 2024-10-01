from __future__ import annotations

from src import utils
from src.state import SubmissionResult
from ..team_puzzle_status import TeamPuzzleStatus

ANSWER_STRING = "梦中的" * 36


class Day2Meta(TeamPuzzleStatus):

    def test_submission(self, submission: str) -> SubmissionResult:
        cleaned_submission = utils.clean_submission(submission)
        # 检查除了正确答案之外的 trigger
        for trigger in self.puzzle.model.triggers:
            if trigger.type == "answer":
                continue
            if cleaned_submission == utils.clean_submission(trigger.value):
                result_type, result_info, trigger_value = trigger.type, trigger.info, trigger.value
                return SubmissionResult(result_type, result_info, trigger_value=trigger_value)
        # 检查是否是正确答案
        if len(cleaned_submission) >= 3:
            if cleaned_submission in ANSWER_STRING:
                if self.passed:
                    return SubmissionResult("multipass", "答案正确！", trigger_value="……梦中的梦中的梦中的……")
                else:
                    return SubmissionResult("pass", "答案正确！", trigger_value="……梦中的梦中的梦中的……")

        return SubmissionResult("wrong", "答案错误！你没有得到任何信息！")
