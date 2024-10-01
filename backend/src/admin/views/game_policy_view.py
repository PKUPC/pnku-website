import json
from typing import Any

from flask import flash
from markupsafe import Markup

from src import store
from src.logic import glitter
from .base_view import BaseView
from .. import fields


class GamePolicyView(BaseView):
    can_create = False
    can_delete = False
    column_descriptions = {
        'effective_after': "目前这一项没启用，请置0，所有设置都直接在下面的 json 中写",
    }
    column_formatters = {
        "json_policy": lambda _v, _c, model, _n: (
                Markup('<samp style="white-space: pre-wrap">%s</samp>') %
                json.dumps(model.json_policy, indent=4, ensure_ascii=False)
        ),
    }
    form_overrides = {
        "json_policy": fields.JsonField,
    }

    def on_form_prefill(self, *args: Any, **kwargs: Any) -> None:
        flash('警告：修改赛程配置会重算排行榜', 'warning')

    def after_model_touched(self, model: store.GamePolicyStore) -> None:
        self.emit_event(glitter.EventType.RELOAD_GAME_POLICY)

    def on_model_change(self, form: Any, model: store.GamePolicyStore, is_created: bool) -> None:
        if is_created:
            model.id = -1
        rst, e = model.validate()
        if not rst:
            assert e is not None
            raise e
        if is_created:
            model.id = None  # type: ignore[assignment]
