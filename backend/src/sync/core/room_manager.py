from __future__ import annotations

import json

from collections.abc import Awaitable, Callable
from typing import Any, overload
from weakref import WeakSet

import pycrdt

from pycrdt import Awareness, Doc, Subscription, TransactionEvent
from sanic import Websocket

from .leveldb_store import LevelDBStore


class SyncRoom:
    """
    单个协作房间，管理一个 YDoc 实例和连接的客户端
    """

    def __init__(
        self, room_id: str, store: LevelDBStore, *, doc_initializer: Callable[[SyncRoom, Doc[Any]], None] | None = None
    ):
        self.room_id = room_id

        self.doc = Doc[Any]()
        self.store = store
        self.clients: WeakSet[Websocket] = WeakSet()  # WebSocket 连接集合
        self.awareness = Awareness(self.doc, outdated_timeout=10000)
        self._initialized = False
        self._doc_initializer = doc_initializer
        self._subscriptions: dict[str, Subscription] = {}

    def initialize(self) -> None:
        if self._initialized:
            return

        state = self.store.load_doc(self.room_id)
        if state:
            self.doc.apply_update(state)

        # 监听文档变化，自动持久化
        self.doc.observe(self._on_update)

        # 如果 state 为空，调用 doc_initializer 初始化
        if state is None and self._doc_initializer is not None:
            self._doc_initializer(self, self.doc)

        self._initialized = True

    def reset(self) -> None:
        self.store.delete_doc(self.room_id)
        self.doc = Doc[Any]()
        self._initialized = False
        self.initialize()

    def _on_update(self, event: TransactionEvent) -> None:
        update = event.update
        self.store.save_doc(self.room_id, update)

    def add_client(self, ws: Websocket) -> None:
        self.clients.add(ws)

    def remove_client(self, ws: Websocket) -> None:
        self.clients.discard(ws)

    async def broadcast(self, message: bytes, excludes: list[Websocket] = []) -> None:
        dead_clients = set()
        for client in self.clients:
            if client in excludes:
                continue
            try:
                await client.send(message)
            except Exception:
                dead_clients.add(client)

        for client in dead_clients:
            self.clients.discard(client)

    def add_observer(
        self, name: str, observer: Callable[[TransactionEvent], None] | Callable[[TransactionEvent], Awaitable[None]]
    ) -> None:
        if name in self._subscriptions:
            return
        sub = self.doc.observe(observer)
        self._subscriptions[name] = sub

    def remove_observer(self, name: str) -> None:
        if name not in self._subscriptions:
            return
        self.doc.unobserve(self._subscriptions[name])
        del self._subscriptions[name]

    def save_kv(self, key: str, value: bytes) -> None:
        self.store.save_kv(self.room_id, key, value)

    @overload
    def load_kv(self, key: str) -> bytes | None: ...
    @overload
    def load_kv(self, key: str, default_value: None = None) -> bytes | None: ...
    @overload
    def load_kv(self, key: str, default_value: bytes) -> bytes: ...

    def load_kv(self, key: str, default_value: bytes | None = None) -> bytes | None:
        return self.store.load_kv(self.room_id, key, default_value)

    def debug_print(self) -> None:
        """
        以 JSON 格式打印当前 doc 和 awareness 的调试信息
        """
        try:
            data = {}
            for key in self.doc.keys():
                if key.endswith('_text'):
                    data[key] = self.doc.get(key, type=pycrdt.Text).to_py()
                elif key.endswith('_array'):
                    data[key] = self.doc.get(key, type=pycrdt.Array).to_py()
                elif key.endswith('_map'):
                    data[key] = self.doc.get(key, type=pycrdt.Map).to_py()

            # 构建调试信息字典
            debug_info = {
                'room_id': self.room_id,
                'initialized': self._initialized,
                'client_count': len(self.clients),
                'doc': {
                    'guid': self.doc.guid,
                    'client_id': self.doc.client_id,
                    'data': data,
                },
                'awareness': {
                    'local_client_id': self.awareness.client_id,
                    'states': self.awareness.states,
                    'meta': self.awareness.meta,
                },
            }

            # 打印格式化的 JSON
            print(json.dumps(debug_info, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f'room_manager.debug_print error: {e}')


class RoomManager:
    """
    全局 Room 管理器。
    """

    def __init__(self, store: LevelDBStore):
        self.store = store
        self.rooms: dict[str, SyncRoom] = {}

    def get_or_create_room(
        self,
        room_id: str,
        *,
        doc_initializer: Callable[[SyncRoom, Doc[Any]], None] | None = None,
        observer_maker: Callable[
            [SyncRoom], Callable[[TransactionEvent], None] | Callable[[TransactionEvent], Awaitable[None]]
        ]
        | None = None,
    ) -> SyncRoom:
        if room_id in self.rooms:
            return self.rooms[room_id]

        room = SyncRoom(room_id, self.store, doc_initializer=doc_initializer)
        room.initialize()
        if observer_maker is not None:
            observer = observer_maker(room)
            room.doc.observe(observer)
        self.rooms[room_id] = room
        return room

    def cleanup_empty_rooms(self) -> None:
        empty_rooms = [room_id for room_id, room in self.rooms.items() if len(room.clients) == 0]
        for room_id in empty_rooms:
            del self.rooms[room_id]
