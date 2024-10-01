from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Dict, Tuple, Set

from sanic import HTTPResponse

from src import secret
from . import WithGameLifecycle
from .team_state import Team
from .. import utils

if TYPE_CHECKING:
    from . import WithGameLifecycle, Game
    from ..store import *


class Users(WithGameLifecycle):
    constructed: bool = False

    def __init__(self, game: Game, stores: List[UserStore]):
        assert not Users.constructed, "Users State 只能有一个实例"
        Users.constructed = True
        self.game: Game = game
        self._stores: List[UserStore] = []
        self.staff_ids: Set[int] = set()

        self.list: List[User] = []
        self.user_by_id: Dict[int, User] = {}
        self.user_by_login_key: Dict[str, User] = {}
        self.user_by_auth_token: Dict[str, User] = {}

        self.on_store_reload(stores)

    def _update_aux_dicts(self) -> None:
        self.user_by_id = {u.model.id: u for u in self.list}
        self.user_by_login_key = {u.model.login_key: u for u in self.list}

    def on_store_reload(self, stores: list[UserStore]) -> None:
        self._stores = stores
        self.list = [User(self.game, x) for x in self._stores]
        self._update_aux_dicts()
        self.staff_ids = set(x.model.id for x in self.list if x.model.group == "staff")

    def on_create_team(self, user_id: int, store: Optional[UserStore]) -> None:
        assert store is not None
        assert user_id in self.user_by_id
        assert self.user_by_id[user_id].team is not None
        assert self.user_by_id[user_id].team.model.leader_id == user_id  # type: ignore  # safe
        self.user_by_id[user_id].on_store_reload(store)

    def on_join_team(self, user_id: int, store: Optional[UserStore]) -> None:
        assert store is not None and user_id in self.user_by_id
        target_user = self.user_by_id[user_id]
        target_user.on_store_reload(store)
        assert store.team_id in self.game.teams.team_by_id
        target_user.team = self.game.teams.team_by_id[store.team_id]
        self.game.teams.team_by_id[store.team_id].members.append(target_user)
        if self.game.teams.team_by_id[store.team_id].total_score > 0:
            self.game.clear_boards_render_cache()

    def on_leave_team(self, user_id: int, store: Optional[UserStore]) -> None:
        assert store is not None and user_id in self.user_by_id
        assert store.team_id is None
        target_user = self.user_by_id[user_id]
        assert target_user.model.team_id in self.game.teams.team_by_id, f"target team_id is {target_user.model.team_id}"
        # 从队伍列表中移除成员
        self.game.teams.team_by_id[target_user.model.team_id].members.remove(target_user)
        target_user.on_store_reload(store)
        target_user.team = None

    def on_store_update(self, id: int, new_store: Optional[UserStore]) -> None:
        # noinspection PyTypeChecker
        old_user: Optional[User] = ([x for x in self.list if x.model.id == id] + [None])[0]
        other_users = [x for x in self.list if x.model.id != id]

        if new_store is None:  # remove
            self.list = other_users
            if id in self.staff_ids:
                self.staff_ids.remove(id)
            # TODO: 检查这个情况 self.game.need_reloading_scoreboard = True
        elif old_user is None:  # add
            self.list = other_users + [User(self.game, new_store)]
            if new_store.group == "staff":
                self.staff_ids.add(id)
            # no need to reload scoreboard, because newly added user does not have any submissions yet
        else:  # modify
            old_user.on_store_reload(new_store)
            if new_store.group == "staff":
                self.staff_ids.add(id)
            elif new_store.group != "staff" and old_user.model.group == "staff":
                self.staff_ids.remove(id)

        self._update_aux_dicts()


class User(WithGameLifecycle):
    constructed_ids: Set[int] = set()

    def __init__(self, game: Game, store: UserStore):
        assert store.id not in User.constructed_ids
        User.constructed_ids.add(store.id)
        #
        self.game: Game = game
        self._store: UserStore = store
        self.model = self._store.validated_model()
        # MAGIC !!
        # 这里为 staff 安插一个队伍
        if self.is_staff:
            self.model.team_id = 0
        # 从逻辑上来说，用户确实可以不在一个队伍中
        self.team: Team | None = None
        # 建立和队伍的关联
        if self.model.team_id is not None:
            assert self.model.team_id in self.game.teams.team_by_id
            team = self.game.teams.team_by_id[self.model.team_id]
            team.members.append(self)
            if team.model.leader_id == self.model.id:
                team.leader = self
            self.team = team

    @property
    def avatar_url(self) -> str:
        return f"https://cravatar.cn/avatar/{utils.calc_md5(self.model.user_info.email)}?d=mp"

    @property
    def is_staff(self) -> bool:
        return self.model.group == "staff"

    @property
    def is_admin(self) -> bool:
        return secret.IS_ADMIN(self.model.id)

    def on_store_reload(self, store: UserStore) -> None:
        # TODO: 检查这个情况
        # # 如果发生 group 切换，则重新载入排行榜
        # if self._store.group != store.group:
        #     self.game.need_reloading_scoreboard = True
        # 处理 group 切换
        staff_flag = False
        if self._store.group != "staff" and store.group == "staff":
            staff_flag = True

        self.game.need_updating_scoreboard = True
        self._store = store
        self.model = self._store.validated_model()

        if staff_flag:
            self.model.team_id = 0
            staff_team = self.game.teams.team_by_id[0]
            self.team = staff_team
            staff_team.members.append(self)

    def check_login(self) -> Optional[Tuple[str, str]]:
        if not self.model.enabled:
            return 'USER_DISABLED', '账号不允许登录'
        return None

    def check_status(self) -> Optional[Tuple[str, str]]:
        """
            基本的用户信息检查，之后会考虑替换掉其他的check，检查以下信息：
            - 是否 enable
            - 是否阅读了参赛须知
            - 是否被 ban 了

            大部分操作都应当需要这个检查
        """
        if not self.model.enabled:
            return 'USER_DISABLED', '账号不允许登录'
        # if not self.store.terms_agreed:
        #     return 'SHOULD_AGREE_TERMS', '请阅读参赛须知'
        # if self.model.group == "banned":
        #     return 'USER_BANNED', '此用户组被禁止参赛'
        return None

    def check_update_profile(self) -> Optional[Tuple[str, str]]:
        """
            用户当前是否能修改信息
            判断：是否登录、是否阅读了参赛须知、是否被 ban 了
        """
        if self.check_login() is not None:
            return self.check_login()
        # if not self.store.terms_agreed:
        #     return 'SHOULD_AGREE_TERMS', '请阅读参赛须知'
        # if self.model.group == 'banned':
        #     return 'USER_BANNED', '此用户组被禁止参赛'
        return None

    def check_play_game(self) -> Optional[Tuple[str, str]]:
        if self.check_update_profile() is not None:
            return self.check_update_profile()
        return None

    def get_teammate_ids(self) -> List[int]:
        """
            获取队友的 id（不包含自己）
            如果没有组队则返回空列表
        """
        if self.team is None:
            return []
        return [t.model.id for t in self.team.members if t.model.id != self.model.id]

    def update_cookie(self, res: HTTPResponse) -> None:
        if self.model.login_properties.type == "email":
            auth_token_value = utils.jwt_encode({
                "user_id": self.model.id, "jwt_salt": self.model.login_properties.jwt_salt
            })
        else:
            auth_token_value = utils.jwt_encode({"user_id": self.model.id})
        utils.add_cookie(res, "auth_token", auth_token_value, "/", secret.JWT_DEFAULT_TIMEOUT)
        user_token = utils.calc_md5(f'nginx uid{self.model.id}')
        utils.add_cookie(res, "user_token", user_token, "/", secret.JWT_DEFAULT_TIMEOUT)

    def __repr__(self) -> str:
        return f"User[{self.model.id}][{self.model.group}]"
