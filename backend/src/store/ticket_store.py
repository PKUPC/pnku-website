from __future__ import annotations

import time

from typing import TYPE_CHECKING, Any, Literal

import sqlalchemy

from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy import JSON, BigInteger, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from src.utils import EnhancedEnum


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

    extra: ManualHintModel

    @property
    def type(self) -> Literal['MANUAL_HINT']:
        return self.extra.type


class TicketStore(Table):
    __tablename__ = 'ticket'

    class TicketType(EnhancedEnum):
        MANUAL_HINT = '人工提示'

    class TicketStatus(EnhancedEnum):
        OPEN = '进行中'
        CLOSED = '已关闭'

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    subject: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    extra: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    @hybrid_property
    def type(self):
        return self.extra.get('type', None)

    @type.expression  # type: ignore[no-redef]
    def type(cls):
        return sqlalchemy.case(
            (
                sqlalchemy.func.json_extract(cls.extra, '$.type').isnot(None),
                sqlalchemy.cast(sqlalchemy.func.json_extract(cls.extra, '$.type'), String(128)),
            ),
            else_=sqlalchemy.null(),
        )

    def validated_model(self) -> TicketStoreModel:
        """
        return pydantic 验证后的 model，可能会抛异常，需要处理。
        """
        return TicketStoreModel.model_validate(self)

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = TicketStoreModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None

    def __repr__(self) -> str:
        return f'[Team${self.team_id}][{self.subject}]'
