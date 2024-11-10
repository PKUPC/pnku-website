from flask_admin.model.template import macro

from src.admin import fields

from .base_view import BaseView


class LogView(BaseView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    column_default_sort = ('id', True)
    column_searchable_list = ['module', 'message']
    column_filters = ['level', 'process', 'module', 'message']

    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
        'level': macro('status_label'),
        'message': macro('in_pre'),
    }
