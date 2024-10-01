import re
import time
from datetime import datetime
from typing import Any, Literal

import sqlalchemy
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, ValidationInfo
from sqlalchemy import String, Integer, BigInteger, Text, JSON, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.utils.enum import EnumWrapper
from . import Table
from .user_store import UserStore


class TeamExtraSpecialStatus(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str
    color: str

    def to_dict(self) -> dict[str, str]:
        return {
            "text": self.text,
            "color": self.color
        }


class BanList(BaseModel):
    model_config = ConfigDict(extra='forbid')
    ban_message_until: str = Field(default="2024-01-01 00:00")
    ban_manual_hint_until: str = Field(default="2024-01-01 00:00")
    ban_recruiting_until: str = Field(default="2024-01-01 00:00")
    ban_upload_image: bool = Field(default=False)

    @field_validator("ban_message_until", "ban_manual_hint_until", "ban_recruiting_until")
    @classmethod
    def check_time(cls, v: str, info: ValidationInfo) -> str:
        if isinstance(v, str):
            try:
                datetime.strptime(v, '%Y-%m-%d %H:%M')
                return v
            except ValueError:
                assert False, f'{info.field_name} 不是合法的时间格式！'
        return v

    @property
    def ban_message_until_ts(self) -> int:
        return int(datetime.strptime(self.ban_message_until, '%Y-%m-%d %H:%M').timestamp())

    @property
    def ban_manual_hint_until_ts(self) -> int:
        return int(datetime.strptime(self.ban_manual_hint_until, '%Y-%m-%d %H:%M').timestamp())

    @property
    def ban_recruiting_until_ts(self) -> int:
        return int(datetime.strptime(self.ban_recruiting_until, '%Y-%m-%d %H:%M').timestamp())


class ExtraTeamInfo(BaseModel):
    model_config = ConfigDict(extra='forbid')
    recruiting: bool = Field(default=False)
    recruiting_contact: str = Field(default="")
    special_status: list[TeamExtraSpecialStatus] = Field(default=[])
    ban_list: BanList = Field(default=BanList())
    upload_image_limit: int = Field(default=10)


class TeamStoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    id: int
    created_at: int
    updated_at: int
    team_name: str
    team_info: str
    leader_id: int
    team_secret: str
    status: Literal["NORMAL", "DISSOLVED"]
    ban_status: Literal["NORMAL", "HIDDEN", "BANNED"]
    extra_info: ExtraTeamInfo


class TeamStore(Table):
    __tablename__ = 'team'

    MAX_TOKEN_LEN = 512
    MAX_INFO_LEN = 128

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))
    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    team_name: Mapped[str] = mapped_column('team_name', String(MAX_INFO_LEN), nullable=False)
    TEAM_NAME_VAL = re.compile(r'^.{1,20}$')

    team_info: Mapped[str] = mapped_column('team_info', Text, nullable=False, default="")
    TEAM_INFO_VAL = re.compile(r'^.{0,512}$')

    leader_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    _leader = relationship('UserStore', foreign_keys=[leader_id])
    _members = relationship('UserStore', back_populates='_team', foreign_keys=[UserStore.team_id])

    team_secret: Mapped[str] = mapped_column('team_secret', String(MAX_INFO_LEN), nullable=False, default="")
    TEAM_SECRET_VAL = re.compile(r'^.{10,20}$')

    class Status(EnumWrapper):
        NORMAL = '正常'
        DISSOLVED = '已解散'

    DEFAULT_STATUS = Status.NORMAL.name

    status: Mapped[str] = mapped_column('status', String(32), nullable=False, default=DEFAULT_STATUS)

    class BanStatus(EnumWrapper):
        NORMAL = '一般通过队伍'
        BANNED = '已封禁'
        HIDDEN = '在排行榜上隐藏'

    ban_status: Mapped[str] = mapped_column('ban_status', String(32), nullable=False, default=BanStatus.NORMAL.name)

    extra_info: Mapped[dict[str, Any]] = mapped_column('extra_info', JSON, nullable=False)

    EXTRA_INFO_TYPES = {"recruitment", "ban_list"}

    @hybrid_property
    def leader_info(self):
        return f"{self._leader.nickname} [U#{self._leader.id}]"

    @leader_info.expression  # type: ignore[no-redef]
    def leader_info(cls):
        return (sqlalchemy.select(sqlalchemy.func.json_extract(UserStore.user_info, "$.nickname"))
                .where(UserStore.id == cls.leader_id)
                .scalar_subquery(),
                " [U#", cls.leader_id, "]"
                )

    def __repr__(self) -> str:
        return f'[T#{self.id} {self.team_name} team_leader=U#{self.leader_id} status={self.status}]'

    def check_profile(self) -> str | None:
        if self.team_name is None or not self.TEAM_NAME_VAL.match(self.team_name):
            return "队名格式错误，应为1到20字符"
        if self.team_info is None or not self.TEAM_NAME_VAL.match(self.team_info):
            return "队伍简介错误，最多为512字符"
        if self.team_secret is None or not self.TEAM_SECRET_VAL.match(self.team_secret):
            return "队伍邀请口令错误，应在10-20个字符之间"
        return None

    def validated_model(self) -> TeamStoreModel:
        """
        assert model is validated
        """
        try:
            model = TeamStoreModel.model_validate(self)
        except ValidationError:
            assert False
        return model

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = TeamStoreModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None
