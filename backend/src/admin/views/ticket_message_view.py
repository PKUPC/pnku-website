from src.admin import fields
from .base_view import BaseView
from ... import store
from ...logic import glitter


class TicketMessageView(BaseView):
    can_delete = False
    can_create = False

    column_list = ["id", "created_at", "ticket_id", "user_id", "direction", "content_type", "content"]
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
    form_excluded_columns = ["id", "created_at", "ticket_id", "user_id", "direction", "content_type"]

    def after_model_touched(self, model: store.TicketMessageStore) -> None:
        self.emit_event(glitter.EventType.UPDATE_TICKET_MESSAGE, model.id)
