from __future__ import annotations

from typing import Any

import flask_admin

from src.admin import fields
from src.logic import glitter
from src.logic.reducer import Reducer
from src.store import PuzzleStateStore

from ..utils import run_reducer_callback
from .base_view import BaseView


class DataField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonFormattedInput()


class PuzzleStateView(BaseView):
    can_create = False
    can_edit = True
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

    form_overrides = {
        'data': DataField,
    }

    def on_model_change(self, form: Any, model: PuzzleStateStore, is_created: bool) -> None:
        assert not is_created, 'PuzzleStateStore should not be created'

        def check(reducer: Reducer) -> bool:
            assert reducer.game is not None
            team_id = model.team_id
            puzzle_key = model.puzzle_key

            puzzle_state = reducer.game_nocheck.teams.team_by_id[team_id].game_state.puzzle_state_by_key[puzzle_key]

            reducer.log(
                'debug',
                'PuzzleStateView',
                f'admin try to modify puzzle state of team {team_id} puzzle {puzzle_key}, new data is {model.data}',
            )

            return puzzle_state.check_stored_state(model.data)

        rst = run_reducer_callback(check)
        if not rst:
            raise ValueError('Puzzle state data is not valid, see logs for details.')

    def after_model_touched(self, model: PuzzleStateStore) -> None:
        self.emit_event(glitter.EventType.UPDATE_PUZZLE_STATE, model.id)
