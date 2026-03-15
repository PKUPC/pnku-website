from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from typing import TYPE_CHECKING, Any

from pycrdt import Doc, TransactionEvent, YMessageType, YSyncMessageType
from sanic import Websocket
from websockets.exceptions import ConnectionClosed

from .room_manager import RoomManager, SyncRoom
from .websocket_handler import YWebSocketHandler


if TYPE_CHECKING:
    from src.logic import Worker


class SyncIntegration:
    """
    同步相关方法集成模块。
    默认使用与 y-websocket 一致的接口处理 websocket 消息，同时支持自定义消息处理。
    """

    def __init__(self, room_manager: RoomManager, worker: Worker):
        self.room_manager = room_manager
        self.worker = worker

    async def handle_sync_websocket(
        self,
        ws: Websocket,
        room_id: str,
        *,
        custom_handler: Callable[[SyncRoom, Websocket, bytes, dict[str, Any] | None], Coroutine[Any, Any, None]]
        | None = None,
        doc_initializer: Callable[[SyncRoom, Doc[Any]], None] | None = None,
        observer_maker: Callable[
            [SyncRoom], Callable[[TransactionEvent], None] | Callable[[TransactionEvent], Awaitable[None]]
        ]
        | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """
        处理 y-websocket 协议的 WebSocket 连接

        参数：
            ws: Sanic WebSocket 对象
            room_id: 房间 ID

            custom_handler: 自定义消息处理函数，用于替换默认的 y-websocket 处理
            doc_initializer: 文档初始化函数，在文档不存在时初始化文档
            observer_maker: 用于生成 doc observer 的函数，在初始化 room 时调用，用于实现自定义逻辑，例如服务端主动
                            更改文档状态时发送 update 消息
        """
        room = self.room_manager.get_or_create_room(
            room_id, doc_initializer=doc_initializer, observer_maker=observer_maker
        )
        room.add_client(ws)
        self.worker.log('debug', 'sync_integration.handle_sync_websocket', f'adding client to room {room_id}')

        if custom_handler is not None:
            handler = custom_handler
        else:
            handler = self._handle_message

        try:
            # 消息循环
            async for message in ws:
                await handler(room, ws, message, extra)

        except ConnectionClosed:
            self.worker.log('debug', 'sync_integration.handle_sync_websocket', f'connection closed for room {room_id}')
        finally:
            self.worker.log('debug', 'sync_integration.handle_sync_websocket', f'removing client from room {room_id}')
            room.remove_client(ws)

    async def _handle_message(
        self, room: SyncRoom, ws: Websocket, data: bytes, extra: dict[str, Any] | None = None
    ) -> None:
        """路由消息到对应的处理器"""
        try:
            msg_type, sync_type, payload = YWebSocketHandler.decode_message(data)

            if msg_type == YMessageType.SYNC:
                if sync_type == YSyncMessageType.SYNC_STEP1:
                    await YWebSocketHandler.handle_sync_step1(room, payload, ws)
                elif sync_type == YSyncMessageType.SYNC_STEP2:
                    await YWebSocketHandler.handle_sync_step2(room, payload, ws)
                elif sync_type == YSyncMessageType.SYNC_UPDATE:
                    await YWebSocketHandler.handle_sync_update(room, payload, ws)
                else:
                    self.worker.log(
                        'warning', 'sync_integration._handle_message', f'Unknown sync message type: {sync_type}'
                    )
            elif msg_type == YMessageType.AWARENESS:
                await YWebSocketHandler.handle_awareness(room, payload, ws)
            else:
                self.worker.log('warning', 'sync_integration._handle_message', f'Unknown message type: {msg_type}')

        except Exception as e:
            self.worker.log('critical', 'sync_integration._handle_message', f'Error handling message: {e}')
