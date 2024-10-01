import json
from typing import Any

from markupsafe import Markup

from src import store
from src.admin import fields
from src.logic import glitter
from .base_view import BaseView


class TeamView(BaseView):
    can_create = False
    can_delete = False
    can_export = True
    can_view_details = True
    details_modal = True

    column_display_pk = True
    column_searchable_list = ["id", "team_name", "team_info"]
    column_list = ["id", "created_at", "team_name", "team_info", "leader_info", "status", "ban_status"]
    column_sortable_list = column_list
    column_details_list = ["id", "created_at", "updated_at", "team_name", "team_info", "_leader", "team_secret",
                           "status", "ban_status", "_members", "extra_info"]

    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
        'updated_at': fields.timestamp_ms_formatter,
        "status": lambda _view, _context, model, name: store.TeamStore.Status.dict().get(name, 'UNKNOWN'),
        "ban_status": lambda _view, _context, model, name: store.TeamStore.BanStatus.dict().get(name, 'UNKNOWN'),
        "team_info": lambda _v, _c, model, _n: (
            model.team_info[:18] + "..." if len(model.team_info) > 20 else model.team_info
        )
    }
    column_formatters_detail = {
        "created_at": fields.timestamp_ms_formatter,
        "updated_at": fields.timestamp_ms_formatter,
        "status": lambda _view, _context, model, name: store.TeamStore.Status.dict().get(name, 'UNKNOWN'),
        "ban_status": lambda _view, _context, model, name: store.TeamStore.BanStatus.dict().get(name, 'UNKNOWN'),
        "extra_info": lambda _v, _c, model, _n: (
                Markup('<samp style="white-space: pre-wrap">%s</samp>')
                % json.dumps(model.extra_info, indent=4, ensure_ascii=False)
        ),
        "team_info": lambda _v, _c, model, _n: (
                Markup('<div style="white-space: pre-wrap">%s</div>')
                % model.team_info
        ),
        "_members": lambda _v, _c, model, _n: (
                Markup('<samp style="white-space: pre-wrap">%s</samp>')
                % "\n".join([str(member) for member in model._members])
        ),
        "_leader": lambda _v, _c, model, _n: (
                Markup('<samp style="white-space: pre-wrap">%s</samp>')
                % str(model._leader)
        )
    }
    column_default_sort = ('id', True)
    column_descriptions = {
        'created_at': '用户保存此信息的时间',
        'updated_at': '用户更新队伍信息的时间',
    }
    column_filters = ["status"]

    form_excluded_columns = ["created_at", "updated_at", "leader_id"]
    form_choices = {
        'status': store.TeamStore.Status.list(),
        "ban_status": store.TeamStore.BanStatus.list(),
    }

    form_overrides = {
        'extra_info': fields.JsonField,
    }

    def after_model_touched(self, model: store.TeamStore) -> None:
        self.emit_event(glitter.EventType.UPDATE_TEAM_INFO, model.id)

    def on_model_change(self, form: Any, model: store.TeamStore, is_created: bool) -> None:
        if is_created:
            model.id = -1
        rst, e = model.validate()
        if not rst:
            assert e is not None
            raise e
        if is_created:
            model.id = None  # type: ignore[assignment]
