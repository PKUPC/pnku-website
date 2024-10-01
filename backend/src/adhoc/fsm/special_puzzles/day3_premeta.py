from __future__ import annotations

from typing import TYPE_CHECKING

from src import utils, secret
from src.state import SubmissionResult
from ..team_puzzle_status import TeamPuzzleStatus

if TYPE_CHECKING:
    from src.state import Submission

if secret.DEBUG_MODE:
    COOLDOWN_TIME = 6
else:
    COOLDOWN_TIME = 60


# meta1：cdegklmqsv
# meta2：afghijlmnprstv
# meta3：bcefhjkorsu

class Day3PreMetaStatus(TeamPuzzleStatus):

    def on_submission(self, submission: Submission, is_reloading: bool = False) -> None:
        assert submission.cleaned_content not in self.submission_set
        self.submission_set.add(submission.cleaned_content)
        match submission.result.type:
            case "wrong":
                self.handle_wrong_submission(submission)

    def test_submission(self, submission: str) -> SubmissionResult:
        cleaned_submission = utils.clean_submission(submission)
        if cleaned_submission in ["cdegklmqsv".upper(), "afghijlmnprstv".upper(), "bcefhjkorsu".upper()]:
            return SubmissionResult("multipass", "精妙的选择！这是一组正确的组合！")

        return SubmissionResult("wrong", "这是什么？你没有得到任何信息！")
