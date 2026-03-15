from __future__ import annotations

from pathlib import Path

import plyvel

from pycrdt import Doc


class LevelDBStore:
    """
    LevelDB 持久化存储
    存储格式：key = f"yjs:{room_name}", value = YDoc 的 state vector
    """

    def __init__(self, db_path: Path | str):
        Path(db_path).mkdir(parents=True, exist_ok=True)
        self.db = plyvel.DB(str(db_path), create_if_missing=True)
        self._prefix = b'yjs:'

    def _make_key(self, room_name: str) -> bytes:
        return self._prefix + room_name.encode('utf-8')

    def load_doc(self, room_name: str) -> bytes | None:
        """
        从 LevelDB 加载文档的持久化状态
        返回 YDoc 的 encoded state (Uint8Array 格式)
        """
        key = self._make_key(room_name)
        data: bytes | None = self.db.get(key, None)
        return data

    def save_doc(self, room_name: str, update: bytes) -> None:
        """
        保存文档更新到 LevelDB
        使用 merge 策略：加载现有 Doc -> 应用 update -> 保存完整 state
        """
        key = self._make_key(room_name)
        # 加载现有文档
        existing: bytes | None = self.db.get(key, None)
        doc = Doc()  # type: ignore[var-annotated]

        if existing:
            doc.apply_update(existing)

        # 应用新的 update
        doc.apply_update(update)

        # 保存完整的 state vector
        state = doc.get_update()

        self.db.put(key, state)

    def delete_doc(self, room_name: str) -> None:
        """删除文档"""
        key = self._make_key(room_name)
        self.db.delete(key)

    def save_kv(self, room_name: str, key: str, value: bytes) -> None:
        db_key = self._make_key(room_name) + b':' + key.encode('utf-8')
        self.db.put(db_key, value)

    def load_kv(self, room_name: str, key: str, default_value: bytes | None = None) -> bytes | None:
        db_key = self._make_key(room_name) + b':' + key.encode('utf-8')
        return self.db.get(db_key, default_value)

    def close(self) -> None:
        """关闭数据库连接"""
        self.db.close()
