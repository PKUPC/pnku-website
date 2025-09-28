from __future__ import annotations

import time

from typing import TYPE_CHECKING

from src.adhoc.constants.enums import CurrencyType

from .currency_event import CurrencyEvent
from .currency_state import CurrencyState
from .utils import calc_balance, truncate_increase_policy


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

    def balance_until_last_event(self) -> int:
        base = self.base
        if len(self.change_event) > 0:
            base = self.change_event[-1].current_currency[self.currency_type]
        return base

    def on_currency_event(self, event: CurrencyEvent) -> None:
        self.total_change += event.currency_change[self.currency_type]

        # 直接计算此时的货币量
        last_base = self.balance_until_last_event()

        origin_policy = self.get_origin_increase_policy()
        # 进行完这个 event 后的剩余为：上一次剩余 + 增加量 - 这次减少的
        event.current_currency[self.currency_type] = (
            calc_balance(origin_policy, event.timestamp_s, self.last_timestamp_s(), last_base)
            + event.currency_change[self.currency_type]
        )

        self.change_event.append(event)

    def current_balance(self) -> int:
        cur_timestamp_s = int(time.time())
        last_base = self.balance_until_last_event()
        last_timestamp_s = self.last_timestamp_s()
        origin_policy = self.get_origin_increase_policy()
        return calc_balance(origin_policy, cur_timestamp_s, last_timestamp_s, last_base)

    def get_origin_increase_policy(self) -> list[tuple[int, int]]:
        origin_policy = self.team_game_state.game.policy.currency_increase_policy_by_type(self.currency_type)
        if len(origin_policy) == 0:
            return [(0, 0)]
        return origin_policy

    def increase_policy_from_last_event(self) -> list[tuple[int, int]]:
        if self.team_game_state.gaming_timestamp_s == -1:
            return [(0, 0)]

        origin_policy = self.get_origin_increase_policy()
        last_timestamp_s = self.last_timestamp_s()

        return truncate_increase_policy(origin_policy, last_timestamp_s)

    def get_currency_history(self) -> list[dict[str, str | int]]:
        rst: list[dict[str, str | int]] = []

        for currency_event in self.change_event:
            change = currency_event.currency_change[self.currency_type]
            current = currency_event.current_currency[self.currency_type]

            change_str = f'{change / self.denominator:.{self.precision}f}'
            current_str = f'{current / self.denominator:.{self.precision}f}'

            rst.append(
                {
                    'timestamp_s': currency_event.timestamp_s,
                    'change': change_str,
                    'current': current_str,
                    'info': currency_event.describe_cost(),
                }
            )

        cur_timestamp_s = int(time.time())
        origin_policy = self.get_origin_increase_policy()
        default_change = calc_balance(origin_policy, cur_timestamp_s, self.team_game_state.gaming_timestamp_s, 0)
        current = default_change + self.total_change

        change_str = f'{default_change / self.denominator:.{self.precision}f}'
        current_str = f'{current / self.denominator:.{self.precision}f}'

        rst.append(
            {
                'timestamp_s': cur_timestamp_s,
                'change': change_str,
                'current': current_str,
                'info': f'随时间增长自动增长的{self.currency_type.value}。',
            }
        )

        return rst
