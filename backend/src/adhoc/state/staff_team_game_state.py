from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING, Any

from src.store import PuzzleActionEvent

from .team_game_state import TeamGameState


if TYPE_CHECKING:
    from src.state import Puzzle, Submission, Team

    from .team_puzzle_state import SubmissionResult


class StaffTeamGameState(TeamGameState):
    """
    只跟游戏进程有关的类，只影响与解谜本身相关的进度，包括解锁状态、特殊谜题状态等。
    """

    def __init__(self, team: Team, puzzle_list: list[Puzzle]):
        super().__init__(team, puzzle_list)
        # 初始全部解锁
        for puzzle in puzzle_list:
            self.unlock_puzzle_keys[puzzle.model.key] = 0
        # self.passed_puzzle_keys 暂时不使用，staff 通过题目也没有意义，这个永远是空的
        # self.unlock_templates 暂时不使用，staff 天然就可以解锁所有模板，逻辑写在模板 api 里
        # self.unlock_areas 暂时不使用
        # self.unlock_boards 暂时不使用，
        # self.unlock_announcement_categories 暂时不使用

    def on_submission(self, submission: Submission, is_reloading: bool) -> None:
        # 和普通队伍不同的是，staff 队伍不需要解锁谜题，所以所有解锁相关的都不需要处理
        # 顺便，staff 队伍的 submission type 也都跟普通队伍区分开，用于做一些特殊处理
        self.submissions.append(submission)
        self.puzzle_state_by_key[submission.puzzle.model.key].on_submission(submission, is_reloading)
        # staff 重复提交答案的问题
        self.puzzle_state_by_key[submission.puzzle.model.key].submission_set.clear()

    def test_submission(self, puzzle_key: str, submission: str) -> SubmissionResult:
        """
        检查 submission 的结果，不更改状态
        """
        test_rst = self.puzzle_state_by_key[puzzle_key].test_submission(submission)
        match test_rst.type:
            case 'pass':
                test_rst.type = 'staff_pass'
                test_rst.info = (
                    '这是一个正确答案，但是工作人员的队伍不会计算通过状态。对于多解题目来说，每一个正确答案都如此。'
                )
            case 'wrong':
                test_rst.type = 'staff_wrong'
                test_rst.info = '答案错误，但是工作人员的队伍不会有冷却时间。'
        self.team.game.log('debug', 'StaffTeamGameState.test_submission', f'{test_rst.type}')
        return test_rst

    def get_render_info(self, puzzle_key: str) -> tuple[tuple[str, str | int | tuple[Hashable, ...]], ...]:
        """
        渲染参数，在实现特殊题目时可能会用到。
        由于 lru_cache 需要参数是 Hashable 的，这里约定渲染参数是一个元组，元组中的每一个元素是一个包含两个参数的元组，第一个参数为
        key，第二个参数为一个 Hashable 的数据。渲染会将这个渲染参数转化为一个字典。例如：
            (("status", 2), ("image", "test.png"))
        在渲染时将会转化成
            {"status": 2, "image", "test.png"}
        后由 jinja2 渲染。
        """
        return self.puzzle_state_by_key[puzzle_key].get_render_info()

    def add_unlock_puzzle(self, puzzle_key: str, unlock_ts: int, is_reloading: bool) -> None:
        assert False

    def team_start_game(self, team_game_start_time: int, is_reloading: bool) -> None:
        assert False

    def on_puzzle_action(self, event: PuzzleActionEvent) -> None:
        if event.puzzle_key in self.puzzle_state_by_key:
            self.puzzle_actions[event.puzzle_key].append(event)
            self.puzzle_state_by_key[event.puzzle_key].on_puzzle_action(event)
        else:
            self.team.game.log('warning', 'TeamGameStatus.on_puzzle_action', f'Unknown puzzle_key: {event.puzzle_key}')

    def get_submission_set(self, puzzle_key: str) -> set[str]:
        return self.puzzle_state_by_key[puzzle_key].submission_set

    def get_correct_answers(self, puzzle_key: str) -> list[str]:
        return self.puzzle_state_by_key[puzzle_key].correct_answers

    def get_dyn_actions(self, puzzle_key: str) -> list[dict[str, Any]]:
        return self.puzzle_state_by_key[puzzle_key].get_dyn_actions()
