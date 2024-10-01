import flask_admin

from src import store
from src.admin import fields
from .base_view import BaseView


class ExtraField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonFormattedInput()


class TicketView(BaseView):
    can_delete = False

    column_list = ["id", "created_at", "team_id", "user_id", "subject", "status", "type", "extra"]
    column_searchable_list = ['user_id', 'team_id', 'subject']
    column_filters = ['user_id', 'team_id', 'type']
    column_display_pk = True
    column_default_sort = ('created_at', True)

    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
    }

    form_choices = {
        # 第一项是实际的 value，第二项是显示的名称
        "type": [(x.name, x.value) for x in store.TicketStore.TicketType],
    }

    form_overrides = {
        "created_at": fields.TimestampMsField,
        "extra": ExtraField
    }

    def after_model_touched(self, model: store.TriggerStore) -> None:
        # TODO: 还没做
        return
        # self.emit_event(glitter.EventType.RELOAD_TRIGGER)
