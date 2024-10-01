from typing import Any, Type

from flask_admin.babel import lazy_gettext
from flask_admin.form import SecureForm
from wtforms import validators

from src.admin import fields
from .base_view import FileAdmin


class FilesView(FileAdmin):
    can_upload = True
    can_mkdir = True
    can_delete = True
    can_delete_dirs = True
    can_rename = True
    can_download = True
    editable_extensions = ['py']

    form_base_class = SecureForm
    edit_template = 'edit_ace.html'

    def get_edit_form(self) -> Type[Any]:
        class EditForm(self.form_base_class):  # type: ignore[name-defined, misc]
            content = fields.PythonField(lazy_gettext('Content'), (validators.InputRequired(),))

        return EditForm
