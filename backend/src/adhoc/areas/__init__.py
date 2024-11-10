from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .area_list import get_unlock_areas_info
from .common import gen_puzzle_structure, gen_puzzle_structure_by_puzzle
from .data import EXTRA_DATA
from .simple_area_detail import get_simple_area


if TYPE_CHECKING:
    from src.logic import Worker
    from src.state import User


def get_area_info(area: str, user: User, worker: Worker) -> dict[str, Any]:
    match area:
        case 'intro':
            return {
                'type': 'intro',
                'template': 'prologue',
                'extra': EXTRA_DATA.get(area, {}),
            }
        case 'day1' | 'day2' | 'day3':
            return get_simple_area(area, user, worker)
        case _:
            assert False, 'never area info case!'
