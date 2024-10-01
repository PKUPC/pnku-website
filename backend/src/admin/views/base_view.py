import asyncio
from typing import Any, Optional

from flask import current_app
from flask_admin.contrib import fileadmin
from flask_admin.contrib import sqla
from flask_admin.form import SecureForm

from src.logic import glitter
from src.logic.reducer import Reducer


class BaseView(sqla.ModelView):  # type: ignore[misc]
    form_base_class = SecureForm
    list_template = 'list.html'
    edit_template = 'edit_ace.html'
    create_template = 'create_ace.html'
    details_modal_template = 'details_break_word.html'

    page_size = 100
    can_set_page_size = True

    @staticmethod
    def emit_event(event_type: glitter.EventType, id: Optional[int] = None) -> None:
        loop: asyncio.AbstractEventLoop = current_app.config['reducer_loop']
        reducer: Reducer = current_app.config['reducer_obj']

        async def task() -> None:
            reducer.state_counter += 1
            event = glitter.Event(event_type, reducer.state_counter, id or 0)
            await reducer.emit_event(event)

        asyncio.run_coroutine_threadsafe(task(), loop)

    def after_model_touched(self, model: Any) -> None:
        pass

    def after_model_change(self, form: Any, model: Any, is_created: bool) -> None:
        self.after_model_touched(model)

    def after_model_delete(self, model: Any) -> None:
        self.after_model_touched(model)


# fix crlf and encoding on windows
class FileAdmin(fileadmin.BaseFileAdmin):  # type: ignore[misc]
    class FixingCrlfFileStorage(fileadmin.LocalFileStorage):  # type: ignore[misc]
        def write_file(self, path: str, content: str) -> int:
            with open(path, 'w', encoding='utf-8') as f:
                return f.write(content.replace('\r\n', '\n'))

    def __init__(self, base_path: str, *args: Any, **kwargs: Any) -> None:
        storage = self.FixingCrlfFileStorage(base_path)
        super().__init__(*args, storage=storage, **kwargs)
