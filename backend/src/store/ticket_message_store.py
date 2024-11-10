from __future__ import annotations

import time

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.utils.enum import EnumWrapper


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    pass
from . import Table


class TicketMessageStore(Table):
    __tablename__ = 'ticket_message'

    class Direction(EnumWrapper):
        TO_PLAYER = '发送给玩家'
        TO_STAFF = '发送给工作人员'

    class ContentType(EnumWrapper):
        TEXT = '文字消息'

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    ticket_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # 这个也许没什么用，但是先从 message 那里抄来
    direction: Mapped[str] = mapped_column(String(32), nullable=False)

    # 之后可能会考虑支持别的类型，先预留
    content_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'[User#{self.user_id}][Ticket#{self.ticket_id}]'
