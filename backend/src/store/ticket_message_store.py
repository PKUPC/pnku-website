from __future__ import annotations

import time

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import JSON, BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.utils import EnhancedEnum

from . import Table


class TicketMessageExtra(BaseModel):
    model_config = ConfigDict(extra='forbid')
    effective_after_ts: int | None = Field(default=None)


class TicketMessageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: int
    ticket_id: int
    user_id: int
    direction: Literal['TO_PLAYER', 'TO_STAFF']
    content_type: Literal['TEXT']
    content: str
    extra: TicketMessageExtra = Field(default=TicketMessageExtra())


class TicketMessageStore(Table):
    __tablename__ = 'ticket_message'

    class Direction(EnhancedEnum):
        TO_PLAYER = '发送给玩家'
        TO_STAFF = '发送给工作人员'

    class ContentType(EnhancedEnum):
        TEXT = '文字消息'

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    ticket_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # 这个也许没什么用，但是先从 message 那里抄来
    direction: Mapped[str] = mapped_column(String(32), nullable=False)

    # 之后可能会考虑支持别的类型，先预留
    content_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    extra: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default={})

    def __repr__(self) -> str:
        return f'[User#{self.user_id}][Ticket#{self.ticket_id}]'

    def validated_model(self) -> TicketMessageModel:
        """
        assert model is validated
        """
        try:
            model = TicketMessageModel.model_validate(self)
        except ValidationError:
            assert False
        return model

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = TicketMessageModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None
