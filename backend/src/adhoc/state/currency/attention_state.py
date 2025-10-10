from __future__ import annotations

from typing import TYPE_CHECKING

from src.adhoc.constants.enums import CurrencyType

from .currency_state import CurrencyState
from .utils import truncate_increase_policy


if TYPE_CHECKING:
    from src.adhoc.state.team_game_state import TeamGameState


class AttentionCurrencyState(CurrencyState):
    """
    P&KU3 中的注意力，本质是一种标准的随时间增长的货币，理论上很多场景下可以复用。
    """

    base = 0
    denominator = 1
    precision = 0
    name = CurrencyType.ATTENTION.name
    icon = 'attention'
    currency_type = CurrencyType.ATTENTION

    def __init__(self, team_game_state: TeamGameState):
        super().__init__(team_game_state)

    def get_origin_increase_policy(self) -> list[tuple[int, int]]:
        origin_policy = self.team_game_state.game.policy.currency_increase_policy_by_type(self.currency_type)
        if len(origin_policy) == 0:
            return [(0, 0)]
        return origin_policy

    def increase_policy_from_last_event(self) -> list[tuple[int, int]]:
        if self.team_game_state.gaming_timestamp_s == -1:
            return [(0, 0)]

        origin_policy = self.team_game_state.game.policy.currency_increase_policy_by_type(self.currency_type)
        if len(origin_policy) == 0:
            return [(0, 0)]

        return truncate_increase_policy(origin_policy, self.last_timestamp_s)
