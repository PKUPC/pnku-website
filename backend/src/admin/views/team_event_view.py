from __future__ import annotations

from typing import TYPE_CHECKING

from src import secret
from src.admin import fields

from ...logic import glitter
from .base_view import BaseView


if TYPE_CHECKING:
    from src.store import TeamEventStore


class TeamEventView(BaseView):
    can_create = False
    can_edit = False
    can_delete = secret.DEBUG_MODE
    can_view_details = True

    column_list = ['id', 'created_at', 'user_id', 'team_id', 'info']
    column_display_pk = True
    column_default_sort = ('id', True)
    column_searchable_list: list[str] = []
    column_filters: list[str] = ['team_id']

    column_formatters = {
        'created_at': fields.timestamp_ms_formatter,
    }

    def on_model_delete(self, model: TeamEventStore) -> None:
        self.emit_event(glitter.EventType.REINIT_GAME, model.id)
