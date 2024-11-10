from __future__ import annotations

import time

from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy import JSON, BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.utils.enum import EnumWrapper


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    pass
from . import Table


class ManualHintModel(BaseModel):
    type: Literal['MANUAL_HINT']
    puzzle_key: str


class TicketStoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: int
    team_id: int
    user_id: int

    subject: str
    status: str
    type: Literal['MANUAL_HINT']

    extra: ManualHintModel


class TicketStore(Table):
    __tablename__ = 'ticket'

    class TicketType(EnumWrapper):
        MANUAL_HINT = '人工提示'

    class TicketStatus(EnumWrapper):
        OPEN = '进行中'
        CLOSED = '已关闭'

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    subject: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)

    extra: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    def validated_model(self) -> TicketStoreModel:
        """
        assert model is validated
        """
        try:
            model = TicketStoreModel.model_validate(self)
        except ValidationError:
            assert False
        return model

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = TicketStoreModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None

    def __repr__(self) -> str:
        return f'[Team${self.team_id}][{self.subject}]'
