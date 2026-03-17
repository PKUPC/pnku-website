from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine, Hashable
from typing import TYPE_CHECKING, Any

from pycrdt import Doc, TransactionEvent
from pydantic import BaseModel, ValidationError

from src import secret, utils
from src.adhoc.constants import PuzzleVisibleStatusLiteral
from src.store import PuzzleActionEvent, PuzzleStateStore


if TYPE_CHECKING:
    from sanic import Websocket

    from src.state import Puzzle, Submission, Team
    from src.sync.core.room_manager import SyncRoom

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
    StoredStateModel: type[BaseModel] = BaseModel

    def __init__(self, game_state: TeamGameState, team: Team, puzzle: Puzzle):
        self.game_state = game_state
        self.game = game_state.game
        self.team: Team = team
        self.puzzle: Puzzle = puzzle
        self.visible: PuzzleVisibleStatusLiteral = 'lock'
        self.wrong_count = 0
        self.cold_down_ts = -1
        self.submission_set: set[str] = set()

        self.correct_answers: list[str] = []
        self.triggered_milestone_count: int = 0

    @property
    def passed(self) -> bool:
        return self.puzzle.model.key in self.game_state.passed_puzzle_keys

    @property
    def stored_state(self) -> PuzzleStateStore | None:
        """
        获取持久化 stored_state，一定需要处理为 None 的情况，并且需要由特殊题目自行检查 json 字段的合法性。
        """
        return self.game.puzzle_states.puzzle_state_store_by_puzzle_key_and_team_id.get(
            (self.puzzle.model.key, self.team.model.id), None
        )

    def check_stored_state(self, data: dict[str, Any]) -> bool:
        try:
            self.StoredStateModel.model_validate(data)
        except ValidationError as e:
            self.game.log('error', 'TeamPuzzleState.check_stored_state', f'ValidationError: {e}')
            return False
        return True

    @property
    def total_milestone_count(self) -> int:
        """
        里程碑数量，特殊题目可能需要自定义这个数量。
        """
        if self.puzzle.model.puzzle_metadata.manual_milestone_count is not None:
            return self.puzzle.model.puzzle_metadata.manual_milestone_count

        return sum(1 for trigger in self.puzzle.model.triggers if trigger.type == 'milestone')

    def check_puzzle_state_update(
        self,
        param: dict[str, Any],
        stored_user_log: Callable[[str, str, str, dict[str, int | str | bool]], None],
    ) -> dict[str, str] | None:
        """
        检查用于更新 stored state 的参数是否合法，由特殊题目自定义检查逻辑。
        stored_user_log 用于在内部记录用户操作日志，参数为：
        module: str, event: str, message: str, extra: dict[str, int | str | bool]
        """
        return None

    def update_puzzle_state(self, old_state: dict[str, Any], param: dict[str, Any]) -> dict[str, Any]:
        """
        更新 stored state，由特殊题目自定义更新逻辑。
        """
        return old_state

    def after_update_puzzle_state(self) -> None:
        """
        在更新 stored state 后调用，由特殊题目自定义调用逻辑。
        """
        pass

    def get_custom_sync_handler(
        self,
    ) -> Callable[[SyncRoom, Websocket, bytes, dict[str, Any] | None], Coroutine[Any, Any, None]] | None:
        return None

    def get_custom_sync_doc_initializer(self) -> Callable[[SyncRoom, Doc[Any]], None] | None:
        return None

    def get_custom_sync_observer_maker(
        self,
    ) -> (
        Callable[[SyncRoom], Callable[[TransactionEvent], None] | Callable[[TransactionEvent], Awaitable[None]]] | None
    ):
        return None

    def on_submission(self, submission: Submission, is_reloading: bool = False) -> None:
        assert submission.cleaned_content not in self.submission_set
        self.submission_set.add(submission.cleaned_content)
        match submission.result.type:
            case 'wrong':
                self.handle_wrong_submission(submission)
            case 'pass':
                self.correct_answers.append(submission.result.trigger_value)
            case 'milestone':
                self.triggered_milestone_count += 1

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

    def on_puzzle_action(self, event: PuzzleActionEvent, is_reloading: bool = False) -> None:
        pass

    def get_dyn_actions(self) -> list[dict[str, Any]]:
        return []

    def handle_wrong_submission(self, submission: Submission) -> None:
        self.wrong_count += 1
        cold_down_seconds = self.wrong_count * COOLDOWN_TIME
        if self.wrong_count > 10:
            cold_down_seconds = 10 * COOLDOWN_TIME
        self.cold_down_ts = int(submission.model.created_at / 1000) + cold_down_seconds
