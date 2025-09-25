from __future__ import annotations

import time

from datetime import datetime
from typing import TYPE_CHECKING, Any

from src.adhoc.constants.enums import CurrencyType

from .base import WithGameLifecycle


if TYPE_CHECKING:
    from ..store import GamePolicyStore, GamePolicyStoreModel, PolicyModel
    from . import Game


class GamePolicy(WithGameLifecycle):
    def __init__(self, game: Game, stores: list[GamePolicyStore]):
        self.game: Game = game
        self.stores: list[GamePolicyStore] = []
        self.models: list[GamePolicyStoreModel] = []
        self.cur_policy_idx: int = -1

        self.on_store_reload(stores)

    def on_store_reload(self, stores: list[GamePolicyStore]) -> None:
        self.stores = stores
        self.stores = sorted(stores, key=lambda x: x.effective_after)
        self.models = [x.validated_model() for x in self.stores]
        self.update_current_policy_idx_at_time()
        self.game.need_reload_team_event = True

    def update_current_policy_idx_at_time(self) -> None:
        self.cur_policy_idx = -1
        current_timestamp_ts = int(time.time())
        for idx, s in enumerate(self.stores):
            if s.effective_after <= current_timestamp_ts:
                self.cur_policy_idx = idx
            else:
                break

    @property
    def cur_policy(self) -> GamePolicyStore:
        current_timestamp_ts = int(time.time())
        for i in range(self.cur_policy_idx + 1, len(self.stores)):
            if self.stores[i].effective_after <= current_timestamp_ts:
                self.cur_policy_idx = i
            else:
                break
        if self.cur_policy_idx == -1:
            return GamePolicyStore.fallback_policy()
        else:
            return self.stores[self.cur_policy_idx]

    @property
    def cur_policy_model(self) -> PolicyModel:
        current_timestamp_ts = int(time.time())
        for i in range(self.cur_policy_idx + 1, len(self.stores)):
            if self.stores[i].effective_after <= current_timestamp_ts:
                self.cur_policy_idx = i
            else:
                break
        if self.cur_policy_idx == -1:
            return GamePolicyStore.fallback_policy().validated_model().json_policy
        else:
            return self.models[self.cur_policy_idx].json_policy

    def currency_increase_policy_by_type(self, currency_type: CurrencyType) -> list[tuple[int, int]]:
        rst = []
        for item in self.cur_policy_model.currency_increase_policy:
            if item.type != currency_type:
                continue
            for policy in item.increase_policy:
                date_obj = datetime.strptime(policy.begin_time_min, '%Y-%m-%d %H:%M')
                t_min = int(time.mktime(date_obj.timetuple())) // 60
                rst.append((t_min, policy.increase_per_min))
        return rst

    @property
    def board_setting(self) -> dict[str, Any]:
        """
        排行榜设置
        """
        rst = {}
        board_setting = self.cur_policy_model.board_setting
        date_obj = datetime.strptime(board_setting.begin_time, '%Y-%m-%d %H:%M:%S')
        ts = int(time.mktime(date_obj.timetuple()))
        rst['begin_ts'] = ts
        date_obj = datetime.strptime(board_setting.end_time, '%Y-%m-%d %H:%M:%S')
        ts = int(time.mktime(date_obj.timetuple()))
        rst['end_ts'] = ts
        rst['top_star_n'] = board_setting.top_star_n
        return rst

    @property
    def puzzle_passed_display(self) -> list[int]:
        return self.cur_policy_model.puzzle_passed_display
