import time

from typing import Any

from sqlalchemy import JSON, BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from . import Table


class LogUserStore(Table):
    __tablename__ = 'log_user'

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    team_id: Mapped[int] = mapped_column(Integer, nullable=True)

    ip_address: Mapped[str] = mapped_column(String(96), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)

    ram: Mapped[str] = mapped_column(String(16), nullable=True)
    rem: Mapped[str] = mapped_column(String(16), nullable=True)
    emt: Mapped[int] = mapped_column(Integer, nullable=True)

    module: Mapped[str] = mapped_column(String(64), nullable=False)
    event: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    extra: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
