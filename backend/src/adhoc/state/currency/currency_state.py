from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from src.adhoc.constants.enums import CurrencyType

from .currency_event import CurrencyEvent


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
        货币类，内部永远用 int 存储，用 denominator 和 denominator 来控制实际显示的值
        denominator 表示实际的值应该为 1 / denominator
        precision 表示在计算后应当保留几位小数，0 即为整数，代码没有保证对于任意长度都是正确的

        denominator 和 precision 只在传给前端显示时有用，内部全是 int，支持的各类计算也只会关注 value

        """
        self.team_game_state: TeamGameState = team_game_state
        self.total_change: int = 0
        self.change_event: list[CurrencyEvent] = []

    @abstractmethod
    def current_balance(self) -> int:
        """
        获取当前的货币值，以现在时间为准，返回货币值
        """
        raise NotImplementedError()

    @abstractmethod
    def on_currency_event(self, event: CurrencyEvent) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_increase_policy(self) -> list[tuple[int, int]]:
        raise NotImplementedError()

    @abstractmethod
    def get_currency_history(self) -> list[dict[str, str | int]]:
        """
        获取货币的历史变动记录
        """
        raise NotImplementedError()
