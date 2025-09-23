from typing import Any

import flask_admin

from flask import current_app
from wtforms import Form

from src import store
from src.admin import fields
from src.logic.reducer import Reducer

from ...logic import glitter
from .base_view import BaseView


class HintExtraField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonObjectInputWithSingleSnippet(store.HintStore.EXTRA_SNIPPETS)


class HintView(BaseView):
    can_create = True
    can_delete = False

    column_list = ['id', 'enable', 'effective_after_ts', 'puzzle_key', 'type', 'question', 'answer', 'extra']
    column_display_pk = True
    column_searchable_list = ['puzzle_key']
    column_default_sort = ('id', True)

    # form_excluded_columns = ["puzzle_key"]

    column_descriptions = {
        'extra': '额外的自定义信息',
        'puzzle_key': '这个提示关联的 puzzle 的 key，禁止更改，如果真的要更改，请将这个 hint 设为不可用并新建另一个 hint',
    }
    column_formatters = {
        'effective_after_ts': fields.timestamp_s_formatter,
    }

    form_widget_args = {
        'puzzle_key': {
            'readonly': True,
        }
    }
    form_overrides = {
        'effective_after_ts': fields.TimestampSField,
        'extra': HintExtraField,
    }
    form_choices = {'type': store.HintStore.HintType.list(), 'puzzle_key': [('TBD', 'TBD')]}

    def create_form(self, **kwargs: Any) -> Form:
        form = super().create_form(**kwargs)
        if 'puzzle_key' in dir(form):
            reducer: Reducer = current_app.config['reducer_obj']
            form.puzzle_key.choices = [
                (k, p.model.title) for k, p in reducer.game_nocheck.puzzles.puzzle_by_key.items()
            ]
        return form  # type: ignore  # create_form itself returns Any

    def on_model_change(self, form: Any, model: store.HintStore, is_created: bool) -> None:
        reducer: Reducer = current_app.config['reducer_obj']

        if is_created:
            model.id = -1
            rst, e = model.validate()
            if not rst:
                assert e is not None
                raise e
            model.id = None  # type:ignore[assignment]
            reducer.log('debug', 'hint_view', f'admin add new hint {model}')
        else:
            rst, e = model.validate()
            if not rst:
                assert e is not None
                raise e
            # 如果模型更改，需要检查
            assert reducer.game is not None
            # 可能是从 disable 变成 enable
            if model.id not in reducer.game_nocheck.hints.hint_by_id:
                current_hint = reducer.load_one_data(store.HintStore, model.id)
                if current_hint is None:
                    reducer.log('debug', 'HintView', 'on_model_change meet a new hint')
                else:
                    reducer.log('debug', 'HintView', f'on_model_change try to set hint {model.id} enable')
            else:
                assert model.id in reducer.game.hints.hint_by_id
            reducer.log('debug', 'hint_view', f'admin modify hint {model}')

    def after_model_touched(self, model: store.HintStore) -> None:
        self.emit_event(glitter.EventType.UPDATE_HINT, model.id)

    def after_model_delete(self, model: store.HintStore) -> None:
        if model.enable:
            self.after_model_touched(model)
