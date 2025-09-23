from typing import Any

from flask import current_app, flash

from src import store
from src.admin import fields
from src.logic.reducer import Reducer

from .base_view import BaseView


def _flag_match_formatter(_view: Any, _context: Any, model: store.SubmissionStore, _name: str) -> str:
    reducer: Reducer = current_app.config['reducer_obj']
    sub = reducer.game_nocheck.submissions_by_id.get(model.id, None)

    if sub is None:
        return '???'

    return f'{sub.result.type}: {sub.result.info}'


def _flag_override_formatter(_view: Any, _context: Any, model: store.SubmissionStore, _name: str) -> str:
    ret: list[str] = []
    # if model.score_override_or_null is not None:
    #     ret.append(f'[={model.score_override_or_null}]')
    # if model.precentage_override_or_null is not None:
    #     ret.append(f'[*{model.precentage_override_or_null}%]')

    return ' '.join(ret)


class SubmissionView(BaseView):
    can_create = False
    can_delete = False

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

    # TODO: 完成 submission 逻辑
    # def after_model_touched(self, model: store.ChallengeStore) -> None:
    #     self.emit_event(glitter.EventType.UPDATE_SUBMISSION, model.id)
