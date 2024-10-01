from __future__ import annotations

from typing import TYPE_CHECKING

from . import WithGameLifecycle
from ..store import MessageStore

if TYPE_CHECKING:
    from . import WithGameLifecycle, Game


class MessageList:
    """
        用来存储消息的 list，稍微做一些优化
        消息应该天然是有序的
        这个结构同时管理未读消息状态，这里我们做了一个假定：用户不可能已读 t 时刻消息缺未读 t - \delta_t 时刻的消息
    """

    def __init__(self) -> None:
        # list 应当是按时间从前向后排序的
        self._list: list[MessageStore] = []
        # 如果 unread_idx == -1，说明没有未读消息
        self.team_unread_idx: int = -1
        self.staff_unread_idx: int = -1
        self.id_to_idx: dict[int, int] = {}

    def append(self, x: MessageStore) -> None:
        if len(self._list) > 0:
            assert x.created_at > self._list[-1].created_at, "MESSAGE_TIME_ERROR"
        self.team_unread_idx = len(self._list) if x.player_unread else -1
        self.staff_unread_idx = len(self._list) if x.staff_unread else -1
        self.id_to_idx[x.id] = len(self._list)
        self._list.append(x)

    def update(self, msg: MessageStore) -> None:
        target_idx = None
        for idx, x in enumerate(self._list):
            if x.id == msg.id:
                target_idx = idx
                break
        if target_idx is not None:
            self._list[target_idx] = msg

    def find_idx_before(self, timestamp: int) -> int:
        """
            找到小于等于给定时间戳的第一个 idx
            理论上来说应该找的都是等于的
            2024-07-12: 这玩意到底是干啥的，一点用都没有
        """
        if len(self._list) == 0 or timestamp < self._list[0].created_at:
            return -1
        left, right = 0, len(self._list) - 1
        while left < right:
            # r == l + 1 时保证收敛
            mid = (left + right + 1) // 2
            if self._list[mid].created_at <= timestamp:
                left = mid
            else:
                right = mid - 1
        return left

    def staff_read(self, last_id: int) -> None:
        assert last_id in self.id_to_idx
        cur_idx = self.id_to_idx[last_id]
        self.staff_unread_idx = -1 if cur_idx == len(self._list) else cur_idx + 1
        while True:
            self._list[cur_idx].staff_unread = False
            cur_idx -= 1
            if cur_idx < 0 or not self._list[cur_idx].staff_unread:
                break

    def player_read(self, last_id: int) -> None:
        assert last_id in self.id_to_idx
        cur_idx = self.id_to_idx[last_id]
        self.team_unread_idx = -1 if cur_idx == len(self._list) else cur_idx + 1
        while True:
            self._list[cur_idx].player_unread = False
            cur_idx -= 1
            if cur_idx < 0 or not self._list[cur_idx].player_unread:
                break

    def get_slice(self, start_id: int) -> list[MessageStore] | None:
        if start_id == 0:
            return self._list
        elif start_id in self.id_to_idx:
            start_idx = self.id_to_idx[start_id]
            if start_idx == len(self._list) - 1:
                return []
            return self._list[self.id_to_idx[start_id] + 1:]
        else:
            return None

    @property
    def list(self) -> list[MessageStore]:
        return self._list

    @property
    def last_message(self) -> MessageStore | None:
        if len(self._list) == 0:
            return None
        return self._list[-1]

    @property
    def player_unread_count(self) -> int:
        return 0 if self.team_unread_idx < 0 else len(self._list) - self.team_unread_idx

    @property
    def staff_unread_count(self) -> int:
        return 0 if self.staff_unread_idx < 0 else len(self._list) - self.staff_unread_idx


class Messages(WithGameLifecycle):
    """
        消息载入逻辑：
            服务器启动时，base.py 中会读入所有的 store，然后传给 Game 的构造函数，Game 中管理其他的 State，会将读出的 Store
            列表传给各个 State 进行初始化
    """

    def __init__(self, game: Game, stores: list[MessageStore]):
        self.game: Game = game
        self._stores: list[MessageStore] = []
        self.message_by_team_id: dict[int, MessageList] = {}
        self.on_store_reload(stores)

    def on_store_reload(self, stores: list[MessageStore]) -> None:
        self._stores = stores
        for msg in self._stores:
            if msg.team_id not in self.message_by_team_id:
                self.message_by_team_id[msg.team_id] = MessageList()
            self.message_by_team_id[msg.team_id].append(msg)

    def on_new_message(self, store: MessageStore) -> None:
        if store.team_id not in self.message_by_team_id:
            self.message_by_team_id[store.team_id] = MessageList()
        self.message_by_team_id[store.team_id].append(store)
        if store.direction == MessageStore.DIRECTION.TO_USER:
            # 如果是管理员回复的，则更新管理员已读状态
            self.on_staff_read_message(store.team_id, store.id)

    def on_update_message(self, store: MessageStore) -> None:
        assert store.team_id in self.message_by_team_id
        self.message_by_team_id[store.team_id].update(store)

    def on_staff_read_message(self, team_id: int, last_msg_id: int) -> None:
        assert team_id in self.message_by_team_id
        self.message_by_team_id[team_id].staff_read(last_msg_id)
        pass

    def on_player_read_message(self, team_id: int, last_msg_id: int) -> None:
        assert team_id in self.message_by_team_id
        self.message_by_team_id[team_id].player_read(last_msg_id)
        pass

    def get_msg_list(self, team_id: int, start_id: int) -> list[MessageStore] | None:
        if team_id not in self.message_by_team_id:
            return []
        return self.message_by_team_id[team_id].get_slice(start_id)

    def get_last_msg_time_by_team_id(self, team_id: int) -> int | None:
        if team_id in self.message_by_team_id:
            return self.message_by_team_id[team_id].list[-1].created_at // 1000
        return None

    def get_team_unread(self, team_id: int) -> bool:
        if team_id in self.message_by_team_id:
            return self.message_by_team_id[team_id].staff_unread_count > 0
        return False

    @property
    def total_staff_unread_cnt(self) -> int:
        """
            统计 staff 有多少个队伍的未读消息
        """
        cnt = 0
        for key in self.message_by_team_id:
            if self.message_by_team_id[key].staff_unread_count > 0:
                cnt += 1
        return cnt
