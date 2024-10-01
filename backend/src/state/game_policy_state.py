from __future__ import annotations

import time
from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Any

from . import WithGameLifecycle
# noinspection PyUnresolvedReferences
from ..store import GamePolicyStore, GamePolicyStoreModel, PolicyModel


class GamePolicy(WithGameLifecycle):
    def __init__(self, game: Game, stores: List[GamePolicyStore]):
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
    def cur_policy_modal(self) -> PolicyModel:
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

    @property
    def ap_increase_policy(self) -> list[tuple[int, int]]:
        """
            体力值增长的计算方式，是一个列表
            列表的每一项是一个元组，第一项为精确到分钟的时间戳，第二项是从这个时间戳开始每分钟获取的体力值
        """
        rst = []
        for item in self.cur_policy_modal.ap_increase_setting:
            date_obj = datetime.strptime(item.begin_time_min, "%Y-%m-%d %H:%M")
            t_min = int(time.mktime(date_obj.timetuple())) // 60
            rst.append((t_min, item.increase_per_min))

        return rst

    def calc_ap_increase_policy_by_team(self, team: Team) -> list[tuple[int, int]]:
        if team.game_start_time == -1:
            return [(0, 0)]
        origin_policy = self.ap_increase_policy
        game_start_min = team.game_start_time // 60
        if game_start_min <= origin_policy[0][0]:
            return origin_policy
        elif len(origin_policy) == 1:
            return [(game_start_min, origin_policy[0][1])]
        else:
            assert len(origin_policy) >= 2 and game_start_min > origin_policy[0][0]
            start_idx = 0
            for i in range(1, len(origin_policy)):
                if game_start_min > origin_policy[i][0]:
                    start_idx = i
                else:
                    break
            # start_idx 是要换掉的
            rst = [(game_start_min, origin_policy[start_idx][1])]
            if start_idx < len(origin_policy) - 1:
                for i in range(start_idx + 1, len(origin_policy)):
                    rst.append(origin_policy[i])
        return rst

    @property
    def board_setting(self) -> Dict[str, Any]:
        """
           排行榜设置
        """
        rst = {}
        board_setting = self.cur_policy_modal.board_setting
        date_obj = datetime.strptime(board_setting.begin_time, "%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(date_obj.timetuple()))
        rst["begin_ts"] = ts
        date_obj = datetime.strptime(board_setting.end_time, "%Y-%m-%d %H:%M:%S")
        ts = int(time.mktime(date_obj.timetuple()))
        rst["end_ts"] = ts
        rst["top_star_n"] = board_setting.top_star_n
        return rst

    @property
    def puzzle_passed_display(self) -> list[int]:
        return self.cur_policy_modal.puzzle_passed_display


if TYPE_CHECKING:
    from . import *
    from ..store import *
