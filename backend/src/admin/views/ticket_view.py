import flask_admin

from src import store
from src.admin import fields

from .base_view import BaseView


class ExtraField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonFormattedInput()


class TicketView(BaseView):
    can_delete = False
    can_edit = False
    can_create = False

    column_list = ['id', 'created_at', 'team_id', 'user_id', 'subject', 'status', 'type', 'extra']
    column_searchable_list = ['user_id', 'team_id', 'subject']
    column_filters = ['user_id', 'team_id', 'type']
    column_display_pk = True
    column_default_sort = ('created_at', True)

    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
    }

    form_overrides = {'created_at': fields.TimestampMsField, 'extra': ExtraField}

    def after_model_touched(self, model: store.TicketStore) -> None:
        # TODO: TicketStore 的 after model touched 还没做
        return
