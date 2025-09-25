from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy import JSON, BigInteger, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.utils import EnhancedEnum


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    pass
from . import Table


class ExtraInfoModel(BaseModel):
    provider: str
    cost: int


class HintStoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enable: bool
    puzzle_key: str
    question: str
    answer: str
    type: Literal['BASIC', 'NORMAL', 'ADVANCE']
    effective_after_ts: int
    extra: ExtraInfoModel


class HintStore(Table):
    __tablename__ = 'hint'

    enable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    puzzle_key: Mapped[str] = mapped_column(String(32), nullable=False)

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    type: Mapped[str] = mapped_column(String(32), nullable=False)

    class HintType(EnhancedEnum):
        BASIC = '指引'
        NORMAL = '观测'
        ADVANCE = '灵视'

    # 注意，这里指的是时间，不是 tick。这里用的是精确到秒的时间戳
    effective_after_ts: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1672502400)

    # 所有其他需要的信息都放在这里
    extra: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    EXTRA_SNIPPETS = {
        'basic': """{"provider": "staff", "cost" : 50}""",
        'normal': """{"provider": "staff", "cost" : 150}""",
        'advance': """{"provider": "staff", "cost" : 300}""",
    }

    def validated_model(self) -> HintStoreModel:
        """
        assert model is validated
        """
        try:
            model = HintStoreModel.model_validate(self)
        except ValidationError:
            assert False
        return model

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = HintStoreModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None

    def __repr__(self) -> str:
        return f'Hint#{self.id} type="{self.type}" puzzle_key={self.puzzle_key}'
