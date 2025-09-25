from __future__ import annotations

from ...constants.enums import CurrencyType
from .attention_state import AttentionCurrencyState
from .currency_event import CurrencyEvent
from .currency_state import CurrencyState


CurrencyTypeToClass: dict[CurrencyType, type[CurrencyState]] = {
    CurrencyType.ATTENTION: AttentionCurrencyState,
}

__all__ = ['CurrencyState', 'AttentionCurrencyState', 'CurrencyTypeToClass', 'CurrencyEvent']
