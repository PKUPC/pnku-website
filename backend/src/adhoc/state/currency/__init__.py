from __future__ import annotations

from ...constants.enums import CurrencyType
from .currency_event import CurrencyEvent
from .currency_state import CurrencyState
from .hint_point_state import HintPointCurrencyState


CurrencyTypeToClass: dict[CurrencyType, type[CurrencyState]] = {
    CurrencyType.HINT_POINT: HintPointCurrencyState,
}

__all__ = ['CurrencyState', 'HintPointCurrencyState', 'CurrencyTypeToClass', 'CurrencyEvent']
