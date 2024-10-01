from flask_admin.model.template import macro

from src.admin import fields
from .base_view import BaseView


class LogUserView(BaseView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    column_list = ["id", "created_at", "user_id", "team_id", "ip_address", "emt", "module", "event", "message",
                   "extra"]
    column_display_pk = True
    column_default_sort = ('id', True)
    column_searchable_list = ["module", "event", "message"]

    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
        'message': macro('in_pre'),
    }
