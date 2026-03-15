from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING, Any

from src import secret, utils
from src.adhoc.constants import PuzzleVisibleStatusLiteral
from src.store import PuzzleActionEvent


if TYPE_CHECKING:
    from src.state import Puzzle, Submission, Team

    from .team_game_state import TeamGameState

if secret.DEBUG_MODE:
    COOLDOWN_TIME = 2
else:
    COOLDOWN_TIME = 60


class SubmissionResult:
    def __init__(
        self,
        sub_type: str,
        sub_info: str,
        *,
        trigger_value: str = '',
        extra: str = '',
        pass_after_meta: bool = False,
        pass_after_finished: bool = False,
        manual_type_name: str | None = None,
    ) -> None:
        self.type = sub_type
        self.info = sub_info
        self.trigger_value = trigger_value
        self.extra = extra
        self.pass_after_meta = pass_after_meta
        self.pass_after_finished = pass_after_finished
        self.manual_type_name = manual_type_name

    def describe_status(self) -> str:
        if self.manual_type_name is not None:
            return self.manual_type_name
        match self.type:
            case 'wrong':
                return '答案错误'
            case 'pass':
                return '答案正确'
            case 'multipass':
                return '答案正确'
            case 'milestone':
                return '里程碑'
            case 'staff_wrong':
                return '答案错误'
            case 'staff_pass':
                return '答案正确'
            case _:
                return '未知错误'

    def describe_response(self) -> dict[str, str]:
        """
        API 返回的响应。
        """

        status = 'error'
        title = self.describe_status()
        message = '请联系网站管理员。'

        match self.type:
            case 'wrong':
                status = 'error'
                message = '答案错误！你没有得到任何信息！'
            case 'milestone':
                status = 'info'
                message = f'你收到了一条信息：\n{self.info}'
            case 'pass':
                status = 'success'
                message = f'{self.info}'
            case 'multipass':
                status = 'success'
                message = f'{self.info}'
            case 'staff_pass':
                status = 'success'
                message = f'{self.info}'
            case 'staff_wrong':
                status = 'error'
                message = f'{self.info}'

        if self.manual_type_name is not None:
            title = self.manual_type_name

        return {
            'status': status,
            'title': title,
            'message': message,
        }

    def __repr__(self) -> str:
        return f'SubmissionResult[{self.type}, {self.info}, {self.trigger_value}, {self.extra}]'


class TeamPuzzleState:
    def __init__(self, game_state: TeamGameState, team: Team, puzzle: Puzzle):
        self.game_state = game_state
        self.team: Team = team
        self.puzzle: Puzzle = puzzle
        self.visible: PuzzleVisibleStatusLiteral = 'lock'
        self.wrong_count = 0
        self.cold_down_ts = -1
        self.submission_set: set[str] = set()

        self.correct_answers: list[str] = []

    @property
    def passed(self) -> bool:
        return self.puzzle.model.key in self.game_state.passed_puzzle_keys

    def on_submission(self, submission: Submission, is_reloading: bool = False) -> None:
        assert submission.cleaned_content not in self.submission_set
        self.submission_set.add(submission.cleaned_content)
        match submission.result.type:
            case 'wrong':
                self.handle_wrong_submission(submission)
            case 'pass':
                self.correct_answers.append(submission.result.trigger_value)

    def test_submission(self, submission: str) -> SubmissionResult:
        cleaned_submission = utils.clean_submission(submission)
        for trigger in self.puzzle.model.triggers:
            if cleaned_submission == utils.clean_submission(trigger.value):
                result_type, result_info = trigger.type, trigger.info
                if result_type == 'answer':
                    result_type = 'pass'
                if result_type == 'pass' and result_info in ['答案正确', '']:
                    result_info = '答案正确！'
                return SubmissionResult(result_type, result_info, trigger_value=trigger.value)
        return SubmissionResult('wrong', '答案错误！你没有得到任何信息！')

    def get_render_info(self) -> tuple[tuple[str, str | int | tuple[Hashable, ...]], ...]:
        return tuple()

    def on_puzzle_action(self, event: PuzzleActionEvent) -> None:
        pass

    def get_dyn_actions(self) -> list[dict[str, Any]]:
        return []

    def handle_wrong_submission(self, submission: Submission) -> None:
        self.wrong_count += 1
        cold_down_seconds = self.wrong_count * COOLDOWN_TIME
        if self.wrong_count > 10:
            cold_down_seconds = 10 * COOLDOWN_TIME
        self.cold_down_ts = int(submission.model.created_at / 1000) + cold_down_seconds
