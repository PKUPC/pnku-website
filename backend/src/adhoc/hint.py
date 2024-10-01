from __future__ import annotations

from typing import TYPE_CHECKING

from src.store import HintStore

if TYPE_CHECKING:
    from src.state import Hint


def hint_cd_after_puzzle_unlock(hint: Hint) -> int:
    match hint.model.type:
        case HintStore.HintType.BASIC.name:
            return 30 * 60
        case HintStore.HintType.NORMAL.name:
            return 60 * 60
        case HintStore.HintType.ADVANCE.name:
            return 6 * 60 * 60
        case _:
            return 14 * 24 * 60 * 60
