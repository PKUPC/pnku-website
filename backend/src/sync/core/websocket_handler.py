"""
处理 y-websocket 协议。
参考 https://github.com/y-crdt/pycrdt/blob/main/python/pycrdt/_sync.py
"""

from pycrdt import (
    YMessageType,
    YSyncMessageType,
    create_awareness_message,
    read_message,
    write_message,
)
from sanic import Websocket

from .room_manager import SyncRoom


class YWebSocketHandler:
    @staticmethod
    def encode_sync_message(sync_type: YSyncMessageType, payload: bytes) -> bytes:
        """
        编码 SYNC 消息格式：[messageType(1 byte)][payload]
        """
        return bytes([YMessageType.SYNC, sync_type]) + write_message(payload)

    @staticmethod
    def decode_message(data: bytes) -> tuple[YMessageType, YSyncMessageType | None, bytes]:
        """
        解码消息
        返回: (message_type, sync_type_or_none, payload)
        """
        if len(data) < 1:
            raise ValueError('Invalid message: too short')
        msg_type = YMessageType(data[0])
        payload = data[1:]

        # sync 类型
        sync_type = None
        if msg_type == YMessageType.SYNC:
            if len(data) < 2:
                raise ValueError('Invalid message: too short')
            sync_type = YSyncMessageType(data[1])
            payload = data[2:]

        return msg_type, sync_type, payload

    @staticmethod
    async def handle_sync_step1(room: SyncRoom, payload: bytes, ws: Websocket) -> None:
        """
        处理 SYNC_STEP1：客户端发送自己的 state vector
        服务端计算差异并返回 SYNC_STEP2

        y-websocket 协议：
        - 客户端发送：[0][state vector]
        - 服务端返回：[1][missing update]
        """

        state = read_message(payload)
        update = room.doc.get_update(state)
        response = YWebSocketHandler.encode_sync_message(YSyncMessageType.SYNC_STEP2, update)

        # 同时发送服务端的 state vector 给客户端
        server_state = room.doc.get_state()
        sync_step1_to_client = YWebSocketHandler.encode_sync_message(YSyncMessageType.SYNC_STEP1, server_state)

        await ws.send(response)
        await ws.send(sync_step1_to_client)

        # 新客户端连接时，发送当前房间中所有客户端的 awareness 状态
        # 获取所有活跃客户端的 client_ids
        if len(room.awareness.states) > 0:
            all_client_ids = list(room.awareness.states.keys())
            awareness_update = room.awareness.encode_awareness_update(all_client_ids)
            awareness_message = create_awareness_message(awareness_update)
            await ws.send(awareness_message)

    @staticmethod
    async def handle_sync_step2(room: SyncRoom, payload: bytes, ws: Websocket) -> None:
        """
        处理 SYNC_STEP2：客户端返回服务端缺失的更新
        应用到 Doc 并广播
        """
        update = read_message(payload)
        if update == b'\x00\x00':
            return

        room.doc.apply_update(update)

        # 广播给其他客户端
        message = YWebSocketHandler.encode_sync_message(YSyncMessageType.SYNC_UPDATE, update)
        await room.broadcast(message, excludes=[ws])

    @staticmethod
    async def handle_sync_update(room: SyncRoom, payload: bytes, ws: Websocket) -> None:
        """
        处理 UPDATE：客户端发送增量更新
        应用到 Doc 并广播给其他客户端
        """
        update = read_message(payload)
        if update == b'\x00\x00':
            return

        room.doc.apply_update(update)

        # 广播给其他客户端
        message = YWebSocketHandler.encode_sync_message(YSyncMessageType.SYNC_UPDATE, update)
        await room.broadcast(message, excludes=[ws])

    @staticmethod
    async def handle_awareness(room: SyncRoom, payload: bytes, ws: Websocket) -> None:
        """
        处理 AWARENESS：客户端发送 awareness 更新
        更新房间的 awareness 状态并广播给其他客户端

        y-websocket 协议：
        - 客户端发送：[1][awareness update]
        - 服务端广播给其他客户端：[1][awareness update]
        """
        awareness_update = read_message(payload)
        room.awareness.apply_awareness_update(awareness_update, 'remote')
        message = create_awareness_message(awareness_update)
        await room.broadcast(message, excludes=[ws])
