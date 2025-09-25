from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from src.state import Puzzle, User


def gen_puzzles_by_structure(sorted_puzzles: list[Puzzle]) -> dict[str, dict[str, list[Puzzle]]]:
    puzzles_by_structure: dict[str, dict[str, list[Puzzle]]] = {}

    for puzzle in sorted_puzzles:
        puzzles_by_structure.setdefault(puzzle.model.category, {})
        puzzles_by_structure[puzzle.model.category].setdefault(puzzle.model.subcategory, [])
        puzzles_by_structure[puzzle.model.category][puzzle.model.subcategory].append(puzzle)

    return puzzles_by_structure


def get_more_puzzle_detail(puzzle: Puzzle, user: User | None = None) -> dict[str, Any]:
    rst: dict[str, Any] = {}
    match puzzle.model.category:
        case 'day1':
            rst['return'] = '/area?dst=day1'
            rst['area_name'] = '第一日'
        case 'day2':
            rst['return'] = '/area?dst=day2'
            rst['area_name'] = '第二日'
        case 'day3':
            rst['return'] = '/area?dst=day3'
            rst['area_name'] = '第三日'
        case _:
            rst['return'] = '/'
            rst['area_name'] = ''
    # 添加正确答案
    if user is not None and user.team is not None:
        correct_answers = user.team.game_state.get_correct_answers(puzzle.model.key)
        answer_display = ''.join(['『' + x + '』' for x in correct_answers])
        rst['answer_display'] = answer_display
    return rst
