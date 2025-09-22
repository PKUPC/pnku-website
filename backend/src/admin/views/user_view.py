import json

from typing import Any

import flask_admin

from flask import current_app, flash
from markupsafe import Markup

from src import store
from src.admin import fields
from src.logic import glitter
from src.logic.reducer import Reducer

from .base_view import BaseView


class UserInfoField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonFormattedInput()


class LoginPropertiesField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonFormattedInput()


def _user_nickname_formatter(_view: Any, _context: Any, model: store.UserStore, _name: str) -> str:
    reducer: Reducer = current_app.config['reducer_obj']
    user = reducer.game_nocheck.users.user_by_id.get(model.id, None)

    if user is None:
        return '[NONE]' + f'{model.user_info.get("nickname", "NONE")}'

    return f'{user.model.user_info.nickname}'


class UserView(BaseView):
    can_create = False
    can_delete = False
    can_export = True
    can_view_details = True
    details_modal = True

    column_list = ['id', 'created_at', 'nickname', 'group', 'enabled', 'login_key', 'team_info']
    column_sortable_list = column_list

    column_display_pk = True
    column_default_sort = ('id', True)
    column_searchable_list = ['id', 'login_key', 'nickname', 'team_info']
    column_filters = ['group', 'login_key', 'enabled']
    column_details_list = [
        'id',
        'created_at',
        'updated_at',
        'login_key',
        'login_properties',
        'nickname',
        'enabled',
        'group',
        'user_info',
        'team_info',
    ]
    # column

    column_descriptions = {
        'created_at': '注册时间',
        'login_key': 'OAuth Provider 提供的唯一 ID，用于判断用户是注册还是登录',
        'login_properties': 'OAuth Provider 提供的用户信息',
        'enabled': '是否允许登录',
        'token': '在前端展示，平台本身不使用',
        'auth_token': '登录凭据，登录后会存在 Cookie 里',
    }
    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
    }
    column_formatters_detail = {
        'login_properties': lambda _v, _c, model, _n: (
            Markup('<samp style="white-space: pre-wrap">%s</samp>')
            % json.dumps(model.login_properties, indent=4, ensure_ascii=False)
        ),
        'created_at': fields.timestamp_ms_formatter,
        'updated_at': fields.timestamp_ms_formatter,
    }

    form_choices = {
        'group': list(store.user_store.USER_GROUPS.items()),
    }
    form_overrides = {
        'login_properties': LoginPropertiesField,
        'created_at': fields.TimestampMsField,
        'user_info': UserInfoField,
    }

    def on_form_prefill(self, *args: Any, **kwargs: Any) -> None:
        flash('警告：修改 group 字段会重算排行榜', 'warning')

    def on_model_change(self, form: Any, model: store.UserStore, is_created: bool) -> None:
        rst, e = model.validate()
        if not rst:
            assert e is not None
            raise e
        if model.group == 'staff' and model.team_id is not None:
            raise Exception('staff 不能在队伍中，需要先退出队伍后再更改。如果原始队伍已经开始游戏则无法修改。')

    def after_model_touched(self, model: store.UserStore) -> None:
        self.emit_event(glitter.EventType.UPDATE_USER, model.id)
