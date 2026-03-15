from __future__ import annotations

from src.admin import fields

from .base_view import BaseView


class PuzzleStateView(BaseView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    column_list = ['id', 'updated_at', 'puzzle_key', 'team_id']
    column_display_pk = True
    column_default_sort = 'team_id'
    column_searchable_list: list[str] = []
    column_filters: list[str] = ['team_id', 'puzzle_key']

    column_formatters = {
        'updated_at': fields.timestamp_ms_formatter,
    }
