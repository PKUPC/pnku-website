from typing import Any

import flask_admin

from src import store
from src.admin import fields

from ...logic import glitter
from .base_view import BaseView


class MessageExtraField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonFormattedInput()


class MessageView(BaseView):
    can_delete = False
    can_create = False

    column_list = ['id', 'created_at', 'user_id', 'team_id', 'direction', 'content_type', 'content']
    column_searchable_list = ['user_id', 'direction']
    column_filters = ['user_id', 'direction']
    column_display_pk = True
    column_sortable_list = ['id', 'created_at']
    column_default_sort = ('created_at', True)

    form_excluded_columns = ['id', 'created_at', 'user_id', 'team_id', 'direction', 'content_type']

    column_descriptions = {
        'created_at': '用户发送消息的时间',
    }
    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
    }

    form_choices = {
        # 第一项是实际的 value，第二项是显示的名称
        'direction': [(x, x) for x in store.MessageStore.DIRECTION.TYPE_SET],
        'content_type': [(x, x) for x in store.MessageStore.CONTENT_TYPE.TYPE_SET],
    }

    form_overrides = {
        'extra': MessageExtraField,
    }

    def on_model_change(self, form: Any, model: store.MessageStore, is_created: bool) -> None:
        rst, e = model.validate()
        if not rst:
            assert e is not None
            raise e

    def after_model_touched(self, model: store.MessageStore) -> None:
        self.emit_event(glitter.EventType.UPDATE_MESSAGE, model.id)
