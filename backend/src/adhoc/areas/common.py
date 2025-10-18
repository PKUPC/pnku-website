from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from src.logic import Worker
    from src.state import Puzzle, User


def gen_puzzle_data_basic(puzzle: Puzzle) -> dict[str, Any]:
    puzzle_data = {
        'puzzle_key': puzzle.model.key,
        'title': puzzle.model.title,
        'status': 'untouched',
        'total_passed': len(puzzle.passed_teams),
        'total_attempted': len(puzzle.attempted_teams),
        'difficulty_status': puzzle.difficulty_status(),
    }
    return puzzle_data


def gen_puzzle_data(user: User, worker: Worker, puzzle: Puzzle) -> dict[str, Any] | None:
    assert user.team is not None
    from src.store import PuzzleType

    puzzle_status = 'untouched'

    if not user.is_staff:
        if user.team.game_state.puzzle_visible_status(puzzle.model.key) == 'lock':
            # PUBLIC 类型的题目允许在未解锁时查看，此时用特殊状态 public 表示
            if puzzle.model.puzzle_metadata.type == PuzzleType.PUBLIC:
                puzzle_status = 'public'
            else:
                return None

        if puzzle_status != 'public':
            assert user.team is not None
            # 这里是解题状态
            puzzle_status = puzzle.status_by_team(user.team)
            # 这里是是否发现该 puzzle
            if user.team.game_state.puzzle_visible_status(puzzle.model.key) == 'found':
                puzzle_status = 'found'

    # ADHOC day3_premeta
    if puzzle.model.key == 'day3_premeta' and (
        'day3_premeta' in user.team.game_state.unlock_puzzle_keys or user.is_staff
    ):
        puzzle_status = 'special'

    puzzle_data = {
        'puzzle_key': puzzle.model.key,
        'title': puzzle.model.title,
        'status': puzzle_status,
        'total_passed': len(puzzle.passed_teams),
        'total_attempted': len(puzzle.attempted_teams),
        'difficulty_status': puzzle.difficulty_status(),
    }

    if puzzle_status == 'found':
        puzzle_data['puzzle_key'] = ''

    if user.model.group != 'staff' and puzzle_status != 'found':
        assert user.team is not None
        puzzle_data['puzzle_key'] = worker.game_nocheck.hash_puzzle_key(user.team.model.id, puzzle.model.key)
    return puzzle_data


def gen_puzzle_structure(area: str, user: User, worker: Worker) -> list[Any]:
    puzzle_structure = worker.game_nocheck.puzzles.puzzles_by_structure.get(area, {})
    rst_puzzle_structure = []

    for key in puzzle_structure:
        group: dict[str, Any] = {'name': key, 'puzzles': []}
        for puzzle in puzzle_structure[key]:
            puzzle_data = gen_puzzle_data(user, worker, puzzle)
            if puzzle_data is None:
                continue

            if puzzle_data['status'] == 'found':
                puzzle_data['found_msg'] = '这里有一道谜题，请继续推进进度以解锁本题。'
            group['puzzles'].append(puzzle_data)

        # 默认按照标题字符串重新排序
        # group["puzzles"] = list(sorted(group["puzzles"], key=lambda x: x["title"]))

        if len(group['puzzles']) > 0:
            rst_puzzle_structure.append(group)

    return rst_puzzle_structure


def gen_puzzle_structure_by_puzzle(puzzle: Puzzle, user: User, worker: Worker) -> list[Any]:
    area = puzzle.model.category
    return gen_puzzle_structure(area, user, worker)
