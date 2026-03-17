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


class FeatureEnableConfig(BaseModel):
    """
    控制某个 feature 启用的配置，三个条件均满足时才启用。
    effective_after 表示需要当前 tick 大于等于这个值
    effective_before 表示需要当前 tick 小于这个值
    """

    default: bool = Field(default=True)
    effective_after: int | None = Field(default=None)
    effective_before: int | None = Field(default=None)

    def is_enabled(self, tick: int) -> bool:
        if self.effective_after is not None and tick < self.effective_after:
            return False
        if self.effective_before is not None and tick >= self.effective_before:
            return False
        return self.default


class FeatureModel(BaseModel):
    user_register: FeatureEnableConfig = Field(default_factory=FeatureEnableConfig)


class PolicyModel(BaseModel):
    model_config = ConfigDict(extra='ignore')

    puzzle_passed_display: list[int] = Field(default_factory=list)
    currency_increase_policy: list[CurrencyIncreaseModel] = Field(default_factory=list)
    board_setting: BoardSetting
    feature: FeatureModel = Field(default_factory=FeatureModel)
    skip_recaptcha_emails: list[str] = Field(default_factory=list)


class GamePolicyStoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    effective_after: int
    json_policy: PolicyModel

    @classmethod
    def need_reload_team_event(cls, old_model: GamePolicyStoreModel, new_model: GamePolicyStoreModel) -> bool:
        """
        检查是否需要 reload team event。
        目前只检查 currency_increase_policy 字段，判断条件为改变的项的时间是否至少距离现在 3 分钟。
        """
        old_policy = old_model.json_policy.currency_increase_policy
        new_policy = new_model.json_policy.currency_increase_policy

        # 获取当前时间（分钟级别）
        current_time_min = int(time.time()) // 60
        min_future_minutes = 3  # 至少 3 分钟

        old_policy_dict: dict[CurrencyType, list[CurrencyIncreasePolicy]] = {}
        for item in old_policy:
            old_policy_dict[item.type] = item.increase_policy

        # 检查每种货币类型
        for new_item in new_policy:
            currency_type = new_item.type
            new_increase_policy = new_item.increase_policy
            old_increase_policy = old_policy_dict.get(currency_type, [])

            old_policy_set = {(item.begin_time_min, item.increase_per_min) for item in old_increase_policy}
            new_policy_set = {(item.begin_time_min, item.increase_per_min) for item in new_increase_policy}

            diff_set = (old_policy_set | new_policy_set) - (old_policy_set & new_policy_set)

            if len(diff_set) == 0:
                continue

            # 分析时间最小的变化项
            min_diff_item = min(diff_set, key=lambda x: x[0])

            print(diff_set)

            # model 中的时间一定是合法的
            date_obj = datetime.strptime(min_diff_item[0], '%Y-%m-%d %H:%M')
            time_min = int(time.mktime(date_obj.timetuple())) // 60
            if time_min < current_time_min + min_future_minutes:
                return True

        new_policy_types = {item.type for item in new_policy}
        old_policy_types = {item.type for item in old_policy}
        if not new_policy_types.issuperset(old_policy_types):
            return True

        return False


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
