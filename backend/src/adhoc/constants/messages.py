from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import CurrencyType


if TYPE_CHECKING:
    from src.store import PriceModel


def make_modify_currency_message(currency_type: CurrencyType, delta: int, reason: str) -> str:
    from src.adhoc.state.currency import CurrencyTypeToClass

    denominator = CurrencyTypeToClass[currency_type].denominator
    precision = CurrencyTypeToClass[currency_type].precision
    delta_str = f'{delta / denominator:.{precision}f}'
    action = '增加' if delta > 0 else '扣除'
    return f'工作人员{action}了你们队伍的{delta_str} {currency_type.value}，原因是：{reason}'


def make_buy_hint_message(teammate: str, puzzle_title: str, price: list[PriceModel]) -> str:
    from src.adhoc.state.currency import CurrencyTypeToClass

    cost_str = '、'.join(
        [
            f'{p.price / CurrencyTypeToClass[p.type].denominator:.{CurrencyTypeToClass[p.type].precision}f} {p.type.value}'
            for p in price
        ]
    )
    return f'你的队友 {teammate} 花费了 {cost_str} 购买了题目《{puzzle_title}》的提示。'


def describe_staff_modify_currency(currency_type: CurrencyType, delta: int, reason: str) -> str:
    action = '增加' if delta > 0 else '扣除'
    return f'工作人员{action}了你们队伍的{currency_type.value}，原因是：{reason}'


def describe_buy_hint_message(username: str, puzzle_title: str, hint_type: str, hint_title: str) -> str:
    return (
        f'玩家 {username} 购买了题目《{puzzle_title}》的提示，提示类型为『{hint_type}』，'
        + f'提示标题为："{hint_title}"。'
    )
