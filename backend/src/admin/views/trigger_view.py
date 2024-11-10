from typing import Any

from flask import flash

from src import store
from src.admin import fields
from src.logic import glitter
from src.state import Trigger

from .base_view import BaseView


class TriggerView(BaseView):
    column_descriptions = {
        'tick': f'Tick 编号，应为自然数且随时间递增，排行榜横轴范围是 Tick {Trigger.TICK_GAME_START} ~ {Trigger.TICK_GAME_END}',
        'name': '将在前端展示，半角分号表示换行',
    }
    column_formatters = {
        'timestamp_s': fields.timestamp_s_formatter,
    }
    form_overrides = {
        'timestamp_s': fields.TimestampSField,
    }
    column_default_sort = 'timestamp_s'

    def on_form_prefill(self, *args: Any, **kwargs: Any) -> None:
        flash('警告：修改赛程配置会重算排行榜', 'warning')

    def after_model_touched(self, model: store.TriggerStore) -> None:
        self.emit_event(glitter.EventType.RELOAD_TRIGGER)
