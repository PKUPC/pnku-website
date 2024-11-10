from __future__ import annotations

import time

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import JSON, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from . import Table


class ApIncreaseModel(BaseModel):
    begin_time_min: str = Field(pattern=r'(20\d\d)-(0[1-9]|1[0-2])-([0-2]\d|3[01]) ([01]\d|2[0-3]):([0-5]\d)')
    increase_per_min: int = Field(default=10)


class BoardSetting(BaseModel):
    begin_time: str = Field(pattern=r'(20\d\d)-(0[1-9]|1[0-2])-([0-2]\d|3[01]) ([01]\d|2[0-3]):([0-5]\d):([0-5]\d)')
    end_time: str = Field(pattern=r'(20\d\d)-(0[1-9]|1[0-2])-([0-2]\d|3[01]) ([01]\d|2[0-3]):([0-5]\d):([0-5]\d)')
    top_star_n: int = Field(default=10)


class PolicyModel(BaseModel):
    puzzle_passed_display: list[int]
    ap_increase_setting: list[ApIncreaseModel]
    board_setting: BoardSetting
    default_spap: int = Field(default=0)


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
                'default_spap': 0,
            },
        )

    def validated_model(self) -> GamePolicyStoreModel:
        """
        assert model is validated
        """
        try:
            model = GamePolicyStoreModel.model_validate(self)
            if len(model.json_policy.ap_increase_setting) == 0:
                assert False, 'ap_increase_setting 列表不能为空'
            pre_time = -1
            for item in model.json_policy.ap_increase_setting:
                date_obj = datetime.strptime(item.begin_time_min, '%Y-%m-%d %H:%M')
                t_min = int(time.mktime(date_obj.timetuple())) // 60
                if t_min <= pre_time:
                    assert False, 'ap_increase_setting 列表的时间不是严格递增的！！！！'
                else:
                    pre_time = t_min
        except ValidationError:
            assert False
        return model

    def validate(self) -> tuple[bool, ValidationError | AssertionError | None]:
        try:
            _model = self.validated_model()
        except ValidationError as e:
            return False, e
        except AssertionError as e:
            return False, e
        return True, None
