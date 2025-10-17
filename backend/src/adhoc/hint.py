from __future__ import annotations

from typing import TYPE_CHECKING

from src import secret


if TYPE_CHECKING:
    from src.state import Hint


def hint_cd_after_puzzle_unlock(hint: Hint) -> int:
    from src.store import HintStore

    cooldown = 0

    match hint.model.type:
        case HintStore.HintType.BASIC.name:
            cooldown = 30 * 60
        case HintStore.HintType.NORMAL.name:
            cooldown = 60 * 60
        case HintStore.HintType.ADVANCE.name:
            cooldown = 6 * 60 * 60

    if secret.DEBUG_MODE:
        cooldown = 60

    return cooldown
