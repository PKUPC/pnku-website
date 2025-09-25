"""
TeamGameState 描述了一个队伍在一次活动中的全部游戏状态，包括各类信息的解锁状态、谜题状态等
题目最关键的解锁逻辑
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING, Any

from src.adhoc.constants import PuzzleVisibleStatusLiteral
from src.store import PuzzleActionEvent

from .special_puzzles import (
    Day2Meta,
    Day3Normal,
    Day3PreMetaState,
    Day201State,
    Day202State,
    Day203State,
    Day206State,
    Day320State,
)
from .team_puzzle_state import TeamPuzzleState


if TYPE_CHECKING:
    from src.state import Puzzle, Submission, SubmissionResult, Team


class TeamGameState:
    """
    TeamGameState 描述了一个队伍在一次活动中的全部游戏状态，包括各类信息的解锁状态、谜题状态等。
    解锁逻辑也全都在这里实现，根据用户当前的提交和当前的状态计算应当解锁的题目，是完全由代码实现的。
    对不不同的活动来说，需要完全手动在这里实现自己的需求，这是 feature。
    """

    def __init__(self, team: Team, puzzle_list: list[Puzzle]):
        """
        会传入对应的 team 对象和所有 puzzle 列表，按需初始化自己的状态和各种题目的状态
        """
        self.team: Team = team
        self.puzzle_state_by_key: dict[str, TeamPuzzleState] = {}
        # 解锁的题目，key 是 puzzle_key，value 是解锁时间
        self.unlock_puzzle_keys: dict[str, int] = {}
        # 通过的题目，key 是 puzzle_key，value 是通过时间
        self.passed_puzzle_keys: dict[str, int] = {}
        # 解锁的模板
        self.unlock_templates: set[str] = {'introduction'}
        # 解锁的区域，默认解锁序章
        self.unlock_areas: set[str] = {'intro'}
        # 解锁的排行榜，对排行榜有特殊需求时使用
        self.unlock_boards: list[str] = []
        # 解锁的公告分类
        self.unlock_announcement_categories: set[str] = set()
        # 接受到的 Puzzle Actions
        self.puzzle_actions: dict[str, list[PuzzleActionEvent]] = {}

        # 一些游戏相关逻辑
        # TODO: 这些是从最早的版本继承而来的，需要进一步确定能否精简
        self.submissions: list[Submission] = []
        self.passed_puzzles: set[tuple[Puzzle, Submission]] = set()
        self.success_submissions: list[Submission] = []

        # 游戏状态
        self.finished: bool = False  # 完赛标记
        self.finished_timestamp_s: int = -1
        self.day1_count = 0
        self.day2_count = 0
        self.day3_count = 0

        # 特殊 Puzzle 可以继承 TeamPuzzleStatus 实现，并在这里使用对应的类
        for puzzle in puzzle_list:
            self.puzzle_actions.setdefault(puzzle.model.key, [])
            match puzzle.model.key:
                case 'day2_01':
                    self.puzzle_state_by_key[puzzle.model.key] = Day201State(self, team, puzzle)
                case 'day2_02':
                    self.puzzle_state_by_key[puzzle.model.key] = Day202State(self, team, puzzle)
                case 'day2_03':
                    self.puzzle_state_by_key[puzzle.model.key] = Day203State(self, team, puzzle)
                case 'day2_06':
                    self.puzzle_state_by_key[puzzle.model.key] = Day206State(self, team, puzzle)
                case 'day2_meta':
                    self.puzzle_state_by_key[puzzle.model.key] = Day2Meta(self, team, puzzle)
                case _ if puzzle.model.key.startswith('day3'):
                    if puzzle.model.key in ['day3_meta1', 'day3_meta2', 'day3_meta3']:
                        self.puzzle_state_by_key[puzzle.model.key] = TeamPuzzleState(self, team, puzzle)
                    elif puzzle.model.key == 'day3_premeta':
                        self.puzzle_state_by_key[puzzle.model.key] = Day3PreMetaState(self, team, puzzle)
                    elif puzzle.model.key == 'day3_20':
                        self.puzzle_state_by_key[puzzle.model.key] = Day320State(self, team, puzzle)
                    else:
                        self.puzzle_state_by_key[puzzle.model.key] = Day3Normal(self, team, puzzle)
                case _:
                    self.puzzle_state_by_key[puzzle.model.key] = TeamPuzzleState(self, team, puzzle)

    def puzzle_visible_status(self, puzzle_key: str) -> PuzzleVisibleStatusLiteral:
        """
        题目可见性，用于自定义题目都有哪些状态，用于按需处理。
        """
        assert puzzle_key in self.puzzle_state_by_key
        return self.puzzle_state_by_key[puzzle_key].visible

    def on_submission(self, submission: Submission, is_reloading: bool) -> None:
        """
        处理提交结果。is_reloading 表示现在是否是重新计算状态阶段，此阶段是全局状态正在重新
        加载，应当避免在此时发送之应当在第一次到达某状态时发送的信息。
        """
        self.submissions.append(submission)
        match submission.result.type:
            case 'pass':
                # 这里需要考虑多解的题的处理
                assert submission.puzzle.model.key not in self.passed_puzzle_keys
                puzzle_key = submission.puzzle.model.key
                self.passed_puzzle_keys[submission.puzzle.model.key] = int(submission.store.created_at / 1000)
                self.passed_puzzles.add((submission.puzzle, submission))
                self.success_submissions.append(submission)

                if puzzle_key.startswith('day1'):
                    if puzzle_key == 'day1_meta':
                        self.unlock_areas.add('day2')
                        self.unlock_templates.add('day1_meta')
                        self.unlock_templates.add('day2_intro')
                        self.add_unlock_puzzle('day2_01', int(submission.store.created_at / 1000), is_reloading)
                        self.add_unlock_puzzle('day2_02', int(submission.store.created_at / 1000), is_reloading)
                        self.add_unlock_puzzle('day2_03', int(submission.store.created_at / 1000), is_reloading)
                        self.add_unlock_puzzle('day2_04', int(submission.store.created_at / 1000), is_reloading)
                        self.add_unlock_puzzle('day2_05', int(submission.store.created_at / 1000), is_reloading)
                        self.add_unlock_puzzle('day2_06', int(submission.store.created_at / 1000), is_reloading)
                    else:
                        self.day1_count += 1
                        # 做出一道解锁一道，做出 5 道时应当解锁完毕
                        if self.day1_count <= 5:
                            self.add_unlock_puzzle(
                                f'day1_{3 + self.day1_count:0>2}', int(submission.store.created_at / 1000), is_reloading
                            )
                        # 做出 7 题时开放 meta
                        if self.day1_count == 7:
                            self.add_unlock_puzzle('day1_meta', int(submission.store.created_at / 1000), is_reloading)

                elif puzzle_key.startswith('day2'):
                    if puzzle_key == 'day2_meta':
                        self.unlock_areas.add('day3')
                        self.unlock_templates.add('day2_meta')
                        self.unlock_templates.add('day3_intro')
                        self.add_unlock_puzzle('day3_01', int(submission.store.created_at / 1000), is_reloading)
                        self.add_unlock_puzzle('day3_02', int(submission.store.created_at / 1000), is_reloading)
                        self.add_unlock_puzzle('day3_03', int(submission.store.created_at / 1000), is_reloading)
                    else:
                        self.day2_count += 1
                        # if self.day2_count <= 3:
                        #     self.add_unlock_puzzle(
                        #         f"day2_{3 + self.day2_count:0>2}",
                        #         int(submission.store.created_at / 1000), is_reloading
                        #     )
                        # 六道题全都做出的时候开放 meta
                        if self.day2_count == 4:
                            self.add_unlock_puzzle('day2_meta', int(submission.store.created_at / 1000), is_reloading)

                elif puzzle_key.startswith('day3'):
                    if puzzle_key in ['day3_meta1', 'day3_meta2', 'day3_meta3']:
                        # 这里名字刚好一样
                        self.unlock_templates.add(puzzle_key)
                        if (
                            'day3_meta1' in self.passed_puzzle_keys
                            and 'day3_meta2' in self.passed_puzzle_keys
                            and 'day3_meta3' in self.passed_puzzle_keys
                        ):
                            self.finished = True
                            self.finished_timestamp_s = int(submission.store.created_at / 1000)
                            self.unlock_boards.append('first_blood')
                            self.unlock_boards.append('speed_run')
                            self.unlock_templates.add('ending')
                            self.unlock_templates.add('staff')
                            if not is_reloading:
                                self.team.game.worker.emit_ws_message(
                                    {
                                        'type': 'normal',
                                        'to_users': self.team.member_ids,
                                        'payload': {'type': 'game_message', 'title': '通知', 'message': '恭喜通关！'},
                                    }
                                )
                    else:
                        self.day3_count += 1
                        if self.day3_count < 4:
                            self.add_unlock_puzzle(
                                f'day3_{3 + self.day3_count:0>2}', int(submission.store.created_at / 1000), is_reloading
                            )
                        elif self.day3_count == 4:
                            self.add_unlock_puzzle('day3_07', int(submission.store.created_at / 1000), is_reloading)
                            self.add_unlock_puzzle('day3_08', int(submission.store.created_at / 1000), is_reloading)
                        elif self.day3_count < 7:
                            self.add_unlock_puzzle(
                                f'day3_{4 + self.day3_count:0>2}', int(submission.store.created_at / 1000), is_reloading
                            )
                        elif self.day3_count == 7:
                            self.add_unlock_puzzle('day3_11', int(submission.store.created_at / 1000), is_reloading)
                            self.add_unlock_puzzle('day3_12', int(submission.store.created_at / 1000), is_reloading)
                        elif self.day3_count < 12:
                            self.add_unlock_puzzle(
                                f'day3_{5 + self.day3_count:0>2}', int(submission.store.created_at / 1000), is_reloading
                            )
                        elif self.day3_count == 12:
                            self.add_unlock_puzzle('day3_17', int(submission.store.created_at / 1000), is_reloading)
                            self.add_unlock_puzzle('day3_18', int(submission.store.created_at / 1000), is_reloading)
                        elif self.day3_count < 17:
                            self.add_unlock_puzzle(
                                f'day3_{6 + self.day3_count:0>2}', int(submission.store.created_at / 1000), is_reloading
                            )
                        elif self.day3_count == 17:
                            self.add_unlock_puzzle(
                                'day3_premeta', int(submission.store.created_at / 1000), is_reloading
                            )
                            self.add_unlock_puzzle('day3_meta1', int(submission.store.created_at / 1000), is_reloading)
                            self.add_unlock_puzzle('day3_meta2', int(submission.store.created_at / 1000), is_reloading)
                            self.add_unlock_puzzle('day3_meta3', int(submission.store.created_at / 1000), is_reloading)
                            self.unlock_templates.add('day3_premeta')
                else:
                    assert False

                submission.finished = self.finished

        self.puzzle_state_by_key[submission.puzzle.model.key].on_submission(submission, is_reloading)

    def test_submission(self, puzzle_key: str, submission: str) -> SubmissionResult:
        """
        检查 submission 的结果，不更改状态
        """
        submission_result = self.puzzle_state_by_key[puzzle_key].test_submission(submission)
        if submission_result.type == 'pass':
            if puzzle_key.startswith('day1') and puzzle_key != 'day1_meta' and 'day1_meta' in self.passed_puzzle_keys:
                submission_result.pass_after_meta = True
            if puzzle_key.startswith('day2') and puzzle_key != 'day2_meta' and 'day2_meta' in self.passed_puzzle_keys:
                submission_result.pass_after_meta = True
            if (
                puzzle_key.startswith('day3')
                and puzzle_key not in ['day3_meta1', 'day3_meta2', 'day3_meta3']
                and self.finished
            ):
                submission_result.pass_after_meta = True
            if self.finished:
                submission_result.pass_after_finished = True

        return submission_result

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
        assert puzzle_key not in self.unlock_puzzle_keys
        if not is_reloading:
            self.team.game.worker.log(
                'debug', 'team_game_state.add_unlock_puzzle', f'team#{self.team.model.id} unlock {puzzle_key}'
            )
        self.unlock_puzzle_keys[puzzle_key] = unlock_ts
        self.puzzle_state_by_key[puzzle_key].visible = 'unlock'

        if not is_reloading:
            if puzzle_key == 'day1_meta':
                self.team.game.worker.emit_ws_message(
                    {
                        'type': 'normal',
                        'to_users': self.team.member_ids,
                        'payload': {
                            'type': 'game_message',
                            'title': '元谜题解锁！',
                            'message': '你解锁了第一日的元谜题，快去看看吧！',
                        },
                    }
                )
            if puzzle_key == 'day2_meta':
                self.team.game.worker.emit_ws_message(
                    {
                        'type': 'normal',
                        'to_users': self.team.member_ids,
                        'payload': {
                            'type': 'game_message',
                            'title': '元谜题解锁！',
                            'message': '你解锁了第二日的元谜题，快去看看吧！',
                        },
                    }
                )
            if puzzle_key == 'day3_premeta':
                self.team.game.worker.emit_ws_message(
                    {
                        'type': 'normal',
                        'to_users': self.team.member_ids,
                        'payload': {
                            'type': 'game_message',
                            'title': '元谜题解锁！',
                            'message': '你解锁了第三日的元谜题，快去看看吧！',
                        },
                    }
                )

    def team_start_game(self, team_game_start_time: int, is_reloading: bool) -> None:
        game_start_time = self.team.game.game_begin_timestamp_s
        if team_game_start_time < game_start_time:
            team_game_start_time = game_start_time

        self.unlock_boards.append('score_board')
        self.unlock_templates.add('prologue')
        self.unlock_templates.add('day1_intro')
        self.unlock_areas.add('day1')
        self.add_unlock_puzzle('day1_01', team_game_start_time, is_reloading)
        self.add_unlock_puzzle('day1_02', team_game_start_time, is_reloading)
        self.add_unlock_puzzle('day1_03', team_game_start_time, is_reloading)

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
