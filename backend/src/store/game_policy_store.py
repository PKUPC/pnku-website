from __future__ import annotations

import time

from datetime import datetime
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import JSON, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.adhoc.constants import CurrencyType
from src.utils import validate_time_minute_str, validate_time_second_str

from . import Table


class CurrencyIncreasePolicy(BaseModel):
    begin_time_min: Annotated[str, AfterValidator(validate_time_minute_str)]
    increase_per_min: int


class CurrencyIncreaseModel(BaseModel):
    type: CurrencyType
    increase_policy: list[CurrencyIncreasePolicy]


class BoardSetting(BaseModel):
    begin_time: Annotated[str, AfterValidator(validate_time_second_str)] = Field(
        default='2000-01-01 00:00:00',
    )
    end_time: Annotated[str, AfterValidator(validate_time_second_str)] = Field(
        default='2099-12-31 23:59:59',
    )
    top_star_n: int = Field(default=10)


class PolicyModel(BaseModel):
    model_config = ConfigDict(extra='ignore')

    puzzle_passed_display: list[int] = Field(default_factory=list)
    currency_increase_policy: list[CurrencyIncreaseModel] = Field(default_factory=list)
    board_setting: BoardSetting


class GamePolicyStoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    effective_after: int
    json_policy: PolicyModel


class GamePolicyStore(Table):
    __tablename__ = 'game_policy'

    effective_after: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

    json_policy: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default={})

    @classmethod
    def fallback_policy(cls) -> GamePolicyStore:
        return cls(
            effective_after=0,
            json_policy={
                'puzzle_passed_display': [1, 2, 4, 8, 16, 32, 64, 96, 128],
                'ap_increase_setting': [{'begin_time_min': '2023-01-01 00:00', 'increase_per_min': 0}],
                'board_setting': {
                    'begin_time': '2023-01-01 00:00:00',
                    'end_time': '2024-03-31 00:00:00',
                    'top_star_n': 10,
                },
            },
        )

    def validated_model(self) -> GamePolicyStoreModel:
        """
        return pydantic 验证后的 model，可能会抛异常，需要处理。
        """
        model = GamePolicyStoreModel.model_validate(self)

        for policy in model.json_policy.currency_increase_policy:
            pre_time = -1
            for item in policy.increase_policy:
                date_obj = datetime.strptime(item.begin_time_min, '%Y-%m-%d %H:%M')
                t_min = int(time.mktime(date_obj.timetuple())) // 60
                if t_min <= pre_time:
                    assert False, f'{policy.type.value} 的 increase_policy 列表的时间不是严格递增的！！！！'
                else:
                    pre_time = t_min

        return model

    def validate(self) -> tuple[bool, ValidationError | AssertionError | None]:
        try:
            _model = self.validated_model()
        except ValidationError as e:
            return False, e
        except AssertionError as e:
            return False, e
        return True, None
