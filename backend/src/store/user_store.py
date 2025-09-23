from __future__ import annotations

import time

from typing import TYPE_CHECKING, Any, Literal

import sqlalchemy

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import ValidationError
from sqlalchemy import JSON, BigInteger, Boolean, ForeignKey, Integer, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    pass

from . import Table


USER_GROUPS = {
    'staff': '工作人员',
    'player': '参赛选手',
    # 'banned': '已封禁',
}


class EmailLoginPropertyModel(BaseModel):
    type: Literal['email']
    salt: str
    cnt: str  # TODO: 当时是怀着怎样的心情把这个设置为 str 的
    jwt_salt: str
    cur_password: str
    next_password: str


class ManualLoginPropertyModel(BaseModel):
    type: Literal['manual']


class WebsiteSettingModel(BaseModel):
    use_html_link: bool = Field(default=False)


class BanList(BaseModel):
    model_config = ConfigDict(extra='forbid')
    ban_message: bool = Field(default=False)
    ban_ticket: bool = Field(default=False)
    ban_staff: bool = Field(default=False)


class UserInfoModel(BaseModel):
    nickname: str
    email: str
    website_setting: WebsiteSettingModel = Field(default=WebsiteSettingModel())
    ban_list: BanList = Field(default=BanList())


class UserStoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: int
    updated_at: int
    login_key: str
    login_properties: EmailLoginPropertyModel | ManualLoginPropertyModel
    enabled: bool
    group: Literal['player', 'staff']
    team_id: int | None
    user_info: UserInfoModel

    def format_login_properties(self) -> str:
        match self.login_properties.type:
            case 'email':
                return f'[E-Mail] {self.user_info.email}'
            case 'manual':
                return '[Manual]'
            case _:
                return f'[{self.login_properties.type}]'

    def group_disp(self) -> str:
        return USER_GROUPS.get(self.group, f'({self.group})')


class UserStore(Table):
    __tablename__ = 'user'

    DEFAULT_GROUP = 'player'

    MAX_TOKEN_LEN = 512

    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))
    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))

    login_key: Mapped[str] = mapped_column(String(192), nullable=False, unique=True)
    login_properties: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    group: Mapped[str] = mapped_column(String(32), nullable=False)

    team_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('team.id'), nullable=True)
    _team = relationship('TeamStore', back_populates='_members', foreign_keys=[team_id])
    user_info: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    @hybrid_property
    def nickname(self):
        return self.user_info.get('nickname', None)

    # ignore type to make mypy happy
    @nickname.expression  # type: ignore[no-redef]
    def nickname(cls):
        return sqlalchemy.case(
            (
                sqlalchemy.func.json_extract(cls.user_info, '$.nickname').isnot(None),
                sqlalchemy.cast(sqlalchemy.func.json_extract(cls.user_info, '$.nickname'), String(128)),
            ),
            else_=sqlalchemy.null(),
        )

    @hybrid_property
    def team_info(self):
        if self.team_id is None:
            return None
        else:
            return f'{self._team.team_name} [T#{self._team.id}]'

    @team_info.expression  # type: ignore[no-redef]
    def team_info(cls):
        from .team_store import TeamStore

        return sqlalchemy.case(
            (
                cls.team_id.isnot(None),
                func.concat(
                    sqlalchemy.select(TeamStore.team_name).where(TeamStore.id == cls.team_id).scalar_subquery(),
                    ' [T#',
                    cls.team_id,
                    ']',
                ),
            ),
            else_=sqlalchemy.null(),
        )

    def __repr__(self) -> str:
        nick = self.user_info['nickname']
        login_key = self.login_key
        return f'[U#{self.id} {login_key} {nick!r} T#{self.team_id}]'

    def validated_model(self) -> UserStoreModel:
        """
        assert model is validated
        """
        try:
            model = UserStoreModel.model_validate(self)
        except ValidationError:
            assert False
        return model

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = UserStoreModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None
