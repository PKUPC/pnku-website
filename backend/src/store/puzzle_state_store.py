from __future__ import annotations

import time

from typing import Any

from sqlalchemy import JSON, BigInteger, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from . import Table


class PuzzleStateStore(Table):
    """
    持久化版本的 puzzle state，对于较为复杂的题目应当使用这种存储而不是只存 team_event，避免 team_event 数量过多的问题。
    """

    __tablename__ = 'puzzle_state'

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    puzzle_key: Mapped[str] = mapped_column(String(32), nullable=False)

    team_id: Mapped[int] = mapped_column(Integer, nullable=False)

    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        Index('uk_puzzle_team', 'puzzle_key', 'team_id', unique=True),
        Index('idx_puzzle_key', 'puzzle_key'),
        Index('idx_team_id', 'team_id'),
    )

    def __repr__(self) -> str:
        return f'State#{self.id} puzzle_key={self.puzzle_key} team_id={self.team_id}'
