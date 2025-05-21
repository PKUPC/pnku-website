from typing import Any

import flask_admin

from src.admin import fields

from ... import store
from ...logic import glitter
from .base_view import BaseView


class TicketMessageExtraField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonFormattedInput()


class TicketMessageView(BaseView):
    can_delete = False
    can_create = False

    column_list = ['id', 'created_at', 'ticket_id', 'user_id', 'direction', 'content_type', 'content']
    column_searchable_list = ['user_id', 'ticket_id']
    column_filters = ['user_id', 'ticket_id', 'content_type']
    column_display_pk = True
    column_default_sort = ('created_at', True)

    column_descriptions = {
        'created_at': '用户发送消息的时间',
    }

    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
    }

    form_overrides = {
        'extra': TicketMessageExtraField,
    }

    form_excluded_columns = ['id', 'created_at', 'ticket_id', 'user_id', 'direction', 'content_type']

    def on_model_change(self, form: Any, model: store.TicketMessageStore, is_created: bool) -> None:
        rst, e = model.validate()
        if not rst:
            assert e is not None
            raise e

    def after_model_touched(self, model: store.TicketMessageStore) -> None:
        self.emit_event(glitter.EventType.UPDATE_TICKET_MESSAGE, model.id)
