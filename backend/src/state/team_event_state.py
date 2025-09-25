from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from src.adhoc.constants import (
    CurrencyType,
    describe_buy_hint_message,
    describe_staff_modify_currency,
)

from ..store import BuyNormalHintEvent, StaffModifyCurrencyEvent, TeamEventStore


if TYPE_CHECKING:
    from . import Game


class TeamEvent:
    constructed_ids: set[int] = set()

    def __init__(self, game: Game, store: TeamEventStore):
        assert store.id not in TeamEvent.constructed_ids
        TeamEvent.constructed_ids.add(store.id)
        # team event 的 store 是不会变的
        self.game: Game = game
        self._store: TeamEventStore = store
        self.model = self._store.validated_model()

        assert self._store.team_id in self.game.teams.team_by_id
        self.team = self.game.teams.team_by_id[self._store.team_id]
        # 货币变化量，实际显示的值
        self.currency_change: dict[CurrencyType, int] = defaultdict(int)
        # 货币隐藏变化量，只用于计算，不实际限制，用于做一些特殊需求
        self.hidden_currency_change: dict[CurrencyType, int] = defaultdict(int)

    def describe_cost(self) -> str:
        info = self.model.info
        match info:
            case StaffModifyCurrencyEvent():
                return describe_staff_modify_currency(info.currency_type, info.delta, info.reason)

            case BuyNormalHintEvent(hint_id=hint_id):
                assert hint_id in self.game.hints.hint_by_id
                hint = self.game.hints.hint_by_id[hint_id]
                puzzle = self.game.puzzles.puzzle_by_key[hint.model.puzzle_key]
                user = self.game.users.user_by_id.get(self.model.user_id, None)
                user_name = user.model.user_info.nickname if user is not None else '未知'
                # 『 』
                return describe_buy_hint_message(
                    user_name, puzzle.model.title, hint.describe_type(), hint.model.question
                )
            case _:
                assert False, 'wrong team event type'

    def __repr__(self) -> str:
        return self._store.__repr__()
