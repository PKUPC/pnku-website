from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from src.adhoc.constants.enums import CurrencyType
from src.adhoc.constants.messages import describe_buy_hint_message, describe_staff_modify_currency
from src.store import BuyNormalHintEvent, StaffModifyCurrencyEvent


if TYPE_CHECKING:
    from src.state import Game, TeamEvent


class CurrencyEvent:
    """
    产生 Currency 变动的需要构造一个 CurrencyEvent 并记录在 TeamGameState 中
    """

    def __init__(self, event: TeamEvent):
        self.team_event: TeamEvent = event
        self.game: Game = event.game

        if not isinstance(event.model.info, (StaffModifyCurrencyEvent, BuyNormalHintEvent)):
            raise ValueError(f'Invalid event type: {type(event.model.info)}')

        self.info: StaffModifyCurrencyEvent | BuyNormalHintEvent = event.model.info

        # 货币变化量，实际显示的值
        self.currency_change: dict[CurrencyType, int] = {}
        # 货币隐藏变化量，只用于计算，不实际限制，用于做一些特殊需求
        self.hidden_currency_change: dict[CurrencyType, int] = {}
        # 当前变化后的货币值
        self.current_currency: dict[CurrencyType, int] = defaultdict(int)
        # 随时间变化的货币值
        self.time_based_currency_change: dict[CurrencyType, int] = defaultdict(int)
        # 时间
        self.timestamp_s: int = event.model.created_at // 1000

    def describe_cost(self) -> str:
        info = self.info
        match info:
            case StaffModifyCurrencyEvent():
                return describe_staff_modify_currency(info.currency_type, info.delta, info.reason)

            case BuyNormalHintEvent(hint_id=hint_id):
                assert hint_id in self.game.hints.hint_by_id
                hint = self.game.hints.hint_by_id[hint_id]
                puzzle = self.game.puzzles.puzzle_by_key[hint.model.puzzle_key]
                user = self.game.users.user_by_id.get(self.team_event.model.user_id, None)
                user_name = user.model.user_info.nickname if user is not None else '未知'
                # 『 』
                return describe_buy_hint_message(
                    user_name, puzzle.model.title, hint.describe_type(), hint.model.question
                )
