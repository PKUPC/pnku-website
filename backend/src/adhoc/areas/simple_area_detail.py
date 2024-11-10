from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.adhoc.areas.common import gen_puzzle_structure

from ..constants import AREA_NAME
from .data import EXTRA_DATA


if TYPE_CHECKING:
    from src.logic import Worker
    from src.state import User


def get_simple_area(area: str, user: User, worker: Worker) -> dict[str, Any]:
    puzzle_structure = gen_puzzle_structure(area, user, worker)

    return {
        'type': 'list',
        'name': AREA_NAME.get(area, '未知'),
        'template': f'{area}_intro',
        'puzzle_groups': puzzle_structure,
        'extra': EXTRA_DATA.get(area, {}),
    }
