"""
在这里导入时需要小心！很容易出现循环引用！
adhoc 内部实现时如果有需要 import 外部的模块（不能放到 TYPE_CHECKING 内的）可以放到函数内部。
"""

from .areas import (
    gen_puzzle_structure,
    gen_puzzle_structure_by_puzzle,
    get_area_info,
    get_simple_area,
    get_unlock_areas_info,
)
from .constants import (
    AREA_NAME,
    MANUAL_HINT_COOLDOWN,
    PUZZLE_CATEGORY_LIST,
    STAFF_DISPLAY_NAME,
    PuzzleVisibleStatus,
    PuzzleVisibleStatusLiteral,
)
from .game_start_reply import game_start_reply
from .hint import hint_cd_after_puzzle_unlock
from .puzzle import gen_puzzles_by_structure, get_extra_puzzle_detail
from .storys import get_story_list


__all__ = [
    'AREA_NAME',
    'MANUAL_HINT_COOLDOWN',
    'PUZZLE_CATEGORY_LIST',
    'STAFF_DISPLAY_NAME',
    'PuzzleVisibleStatus',
    'PuzzleVisibleStatusLiteral',
    'gen_puzzle_structure',
    'gen_puzzle_structure_by_puzzle',
    'get_area_info',
    'get_simple_area',
    'get_unlock_areas_info',
    'gen_puzzles_by_structure',
    'get_extra_puzzle_detail',
    'hint_cd_after_puzzle_unlock',
    'get_story_list',
    'game_start_reply',
]
