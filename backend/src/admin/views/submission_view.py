from typing import Any

from flask import flash

from src.admin import fields

from .base_view import BaseView


class SubmissionView(BaseView):
    can_create = False
    can_delete = False
    can_edit = False

    column_list = ['id', 'created_at', 'user_id', 'puzzle_key', 'content', 'extra']

    column_display_pk = True
    column_searchable_list = ['id']
    column_filters = ['user_id', 'puzzle_key']
    column_default_sort = ('id', True)

    column_descriptions = {
        'extra': '额外的自定义信息',
    }
    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
    }

    def on_form_prefill(self, *args: Any, **kwargs: Any) -> None:
        flash('警告：修改历史提交会重算排行榜', 'warning')
