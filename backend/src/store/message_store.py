from __future__ import annotations

import time

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import JSON, BigInteger, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from . import Table


class MessageExtra(BaseModel):
    model_config = ConfigDict(extra='forbid')
    effective_after_ts: int | None = Field(default=None)


class MessageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: int
    team_id: int
    user_id: int
    direction: Literal['to_user', 'to_staff']
    content_type: Literal['text']
    content: str
    player_unread: bool
    staff_unread: bool
    extra: MessageExtra = Field(default=MessageExtra())


class MessageStore(Table):
    __tablename__ = 'message'

    MAX_CONTENT_LEN = 233

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    # 队伍id
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # 一个用户id，如果是玩家发给管理员的，就是玩家的id，否则是管理员的id，即发送者id
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # 站内信只能是 player 和 staff 互相发，记一下发送方向
    direction: Mapped[str] = mapped_column(String(32), nullable=False)
    # 之后可能会考虑支持别的类型，先预留
    content_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 对于状态管理来说，只需要记录最后一个已读信息即可，之前的可以认为都已读了
    # 对于数据库存储来说，更新的时候可以考虑将历史的 **应当已读** 的信息都更新了
    player_unread: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    staff_unread: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    extra: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    class DIRECTION:
        TO_STAFF: str = 'to_staff'
        TO_USER: str = 'to_user'

        TYPE_SET: set[str] = {TO_USER, TO_STAFF}

    class CONTENT_TYPE:
        TEXT: str = 'text'
        IMAGE: str = 'image'

        TYPE_SET: set[str] = {TEXT, IMAGE}

    def __repr__(self) -> str:
        content = self.content[:20]
        if len(self.content) > 20:
            content += '...'
        if self.direction == self.DIRECTION.TO_USER:
            return (
                f'[Staff#{self.user_id} reply to Team#{self.team_id}'
                f'content={self.content} su={self.staff_unread} pu={self.player_unread}]'
            )
        else:
            return (
                f'[User#{self.user_id} ask Staff content={self.content}'
                f'su={self.staff_unread} pu={self.player_unread}]'
            )

    def validated_model(self) -> MessageModel:
        """
        assert model is validated
        """
        try:
            model = MessageModel.model_validate(self)
        except ValidationError:
            assert False
        return model

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = MessageModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None
