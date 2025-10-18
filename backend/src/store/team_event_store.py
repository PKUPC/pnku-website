from __future__ import annotations

import time

from enum import auto
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import JSON, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.adhoc.constants.enums import CurrencyType
from src.utils import EnhancedEnum

from . import Table


class TeamEventType(EnhancedEnum):
    GAME_START = auto()
    SUBMISSION = auto()
    BUY_NORMAL_HINT = auto()
    STAFF_MODIFY_CURRENCY = auto()
    PUZZLE_ACTION = auto()


class SingleCurrencyChange(BaseModel):
    type: CurrencyType
    delta: int


class CurrencyChangeModel(BaseModel):
    changed: bool = False
    change_list: list[SingleCurrencyChange] = Field(default_factory=list)


class TeamEventBase(BaseModel):
    type: TeamEventType
    currency_change: CurrencyChangeModel = Field(default_factory=CurrencyChangeModel)


class GameStartEvent(TeamEventBase):
    type: Literal[TeamEventType.GAME_START]


class SubmissionEvent(TeamEventBase):
    """
    提交答案事件，包含了提交的答案和当时的检查结果。
    """

    type: Literal[TeamEventType.SUBMISSION]
    puzzle_key: str
    content: str


class BuyNormalHintEvent(TeamEventBase):
    type: Literal[TeamEventType.BUY_NORMAL_HINT]
    hint_id: int


class StaffModifyCurrencyEvent(TeamEventBase):
    type: Literal[TeamEventType.STAFF_MODIFY_CURRENCY]
    currency_type: CurrencyType
    delta: int
    reason: str


class PuzzleActionEvent(TeamEventBase):
    type: Literal[TeamEventType.PUZZLE_ACTION]
    puzzle_key: str
    content: dict[str, str | int]


class TeamEventStoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: int
    user_id: int
    team_id: int
    info: GameStartEvent | SubmissionEvent | BuyNormalHintEvent | StaffModifyCurrencyEvent | PuzzleActionEvent


class TeamEventStore(Table):
    """
    不同的 puzzle hunt 活动总是会有着各种奇妙的设计，比如 pnku2 最早除了体力值之外还有个什么 “邮票”，在目前的设计中，还希望
    玩家可以给提示点赞点踩等，不如把这些奇妙行为都定义成 team_event，根据 type 进行区分
    """

    __tablename__ = 'team_event'

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    team_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # 所有其他需要的信息都放在这里
    info: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f'Event#{self.id} type="{self.info["type"]}" info={self.info}'

    def validated_model(self) -> TeamEventStoreModel:
        """
        return pydantic 验证后的 model，可能会抛异常，需要处理。
        """
        return TeamEventStoreModel.model_validate(self)

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = TeamEventStoreModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None
