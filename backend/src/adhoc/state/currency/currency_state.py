from __future__ import annotations

import time

from abc import abstractmethod
from typing import TYPE_CHECKING

from src.adhoc.constants.enums import CurrencyType

from .currency_event import CurrencyEvent
from .utils import calc_balance


if TYPE_CHECKING:
    from src.adhoc.state.team_game_state import TeamGameState


class CurrencyState:
    base: int = 0
    denominator: int = 1
    precision: int = 0
    name: str = 'DEFAULT'
    icon: str = 'DEFAULT'
    currency_type: CurrencyType

    # TODO: 这两个字段尚未使用，目前仅作保留
    # 是否可以被 staff 修改
    can_modify: bool = True
    # 是否显示货币变动记录
    show_change_record: bool = True

    def __init__(self, team_game_state: TeamGameState):
        """
        货币类，内部永远用 int 存储，用 denominator 和 denominator 来控制实际显示的值。
        denominator 表示实际的值应该为 1 / denominator。
        precision 表示在计算后应当保留几位小数，0 即为整数，代码没有保证对于任意长度都是正确的。

        denominator 和 precision 只在传给前端显示时有用，内部全是 int，支持的各类计算也只会关注 value。

        该类中提供了一些通用逻辑，默认需要自行实现 increase_policy_from_last_event 方法，该方法需要返回
        从上次货币变动事件开始的货币增长策略，用于实现不同的货币增量需求。
        """
        self.team_game_state: TeamGameState = team_game_state
        # 截止到上一个 event 时，所有 event 的变化量
        self.accumulated_event_changes: int = 0
        # 截止到上一个 event 时，随时间增长的变化量
        self.accumulated_time_based_changes: int = 0
        self.change_event: list[CurrencyEvent] = []

    @abstractmethod
    def increase_policy_from_last_event(self) -> list[tuple[int, int]]:
        """
        从上次货币变动事件开始的货币增长策略，需要根据货币的需求自行实现。
        """
        raise NotImplementedError()

    @property
    def last_timestamp_s(self) -> int:
        """
        返回上次货币变动事件的时间。
        """
        last_timestamp_s = self.team_game_state.gaming_timestamp_s
        if last_timestamp_s < 0:
            last_timestamp_s = 0
        if len(self.change_event) == 0:
            return last_timestamp_s
        return self.change_event[-1].timestamp_s

    @property
    def balance_until_last_event(self) -> int:
        """
        返回直到上一次货币变动事件为止的货币值。
        """
        base = self.base
        if len(self.change_event) > 0:
            base = self.change_event[-1].current_currency[self.currency_type]
        return base

    @property
    def current_balance(self) -> int:
        """
        获取当前的货币值，以现在时间为准，返回货币值
        """
        return calc_balance(
            self.increase_policy_from_last_event(),
            int(time.time()),
            self.last_timestamp_s,
            self.balance_until_last_event,
        )

    def on_currency_event(self, event: CurrencyEvent) -> None:
        """
        处理 currency event 的逻辑。
        """
        self.accumulated_event_changes += event.currency_change[self.currency_type]

        # 计算货币增长量
        increase_policy = self.increase_policy_from_last_event()
        time_based_change = calc_balance(increase_policy, event.timestamp_s, self.last_timestamp_s, 0)
        self.accumulated_time_based_changes += time_based_change

        # 进行完这个 event 后的剩余为：上一次剩余 + 增加量 + 本次变动量
        event.current_currency[self.currency_type] = (
            self.balance_until_last_event + time_based_change + event.currency_change[self.currency_type]
        )
        event.time_based_currency_change[self.currency_type] = time_based_change

        self.change_event.append(event)

    def get_currency_history(self, with_time_based_changes: bool = True) -> list[dict[str, str | int]]:
        """
        获取货币的历史变动记录

        with_time_based_changes 表示是否包含随时间自动增长的变化量，默认包含。
        """

        rst: list[dict[str, str | int]] = []

        for currency_event in self.change_event:
            change = currency_event.currency_change[self.currency_type]
            current = currency_event.current_currency[self.currency_type]
            time_based_change = currency_event.time_based_currency_change[self.currency_type]

            change_str = f'{change / self.denominator:.{self.precision}f}'
            time_based_change_str = f'{time_based_change / self.denominator:.{self.precision}f}'
            current_str = f'{current / self.denominator:.{self.precision}f}'

            rst.append(
                {
                    'timestamp_s': currency_event.timestamp_s,
                    'change': change_str,
                    'time_based_change': time_based_change_str,
                    'current': current_str,
                    'info': currency_event.describe_cost(),
                }
            )

        if with_time_based_changes:
            # 随时间增长总量为 accumulated_time_based_changes + 从上次 event 到现在的增长量
            cur_timestamp_s = int(time.time())
            current_policy = self.increase_policy_from_last_event()
            time_based_change_from_last_event = calc_balance(
                current_policy,
                cur_timestamp_s,
                self.last_timestamp_s,
                0,
            )
            # 当前货币量为 self.balance_until_last_event + 从上次 event 到现在的增长量
            current = self.balance_until_last_event + time_based_change_from_last_event

            change_str = f'{0 / self.denominator:.{self.precision}f}'
            time_based_change_str = f'{time_based_change_from_last_event / self.denominator:.{self.precision}f}'
            current_str = f'{current / self.denominator:.{self.precision}f}'

            rst.append(
                {
                    'timestamp_s': cur_timestamp_s,
                    'change': change_str,
                    'time_based_change': time_based_change_str,
                    'current': current_str,
                    'info': f'随时间自动增长的{self.currency_type.value}。',
                }
            )

        return rst
