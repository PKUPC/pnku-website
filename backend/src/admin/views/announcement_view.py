from flask_admin.model.template import macro

from src import store
from src.admin import fields
from src.logic import glitter
from .base_view import BaseView


class AnnouncementView(BaseView):
    column_list = ["id", "publish_at", "sorting_index", "category", "title", "content_template"]
    column_display_pk = True
    column_default_sort = ('id', True)
    column_formatters = {
        'publish_at': fields.timestamp_s_formatter,
        'content_template': macro('in_pre'),
    }
    column_descriptions = {
        "publish_at": "公告放出的时间，可自行设置。以前的公告有重要更新也建议调整此时间。",
        "sorting_index": "设置为大于等于 0 的数即为置顶公告，数字越大，置顶优先级越高。不用置顶则默认为 -1 即可。",
        'content_template': '支持 Markdown 和 Jinja2 模板（group: Optional[str]、tick: int）',
    }

    form_overrides = {
        'publish_at': fields.TimestampSField,
        'content_template': fields.MarkdownField,
    }
    form_choices = {
        'category': [(x.name, x.value) for x in store.AnnouncementStore.Category],
    }

    def after_model_touched(self, model: store.AnnouncementStore) -> None:
        self.emit_event(glitter.EventType.UPDATE_ANNOUNCEMENT, model.id)
