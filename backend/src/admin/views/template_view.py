from typing import Any, Type

from flask_admin.babel import lazy_gettext
from flask_admin.form import SecureForm
from wtforms import validators

from src.admin import fields

from .base_view import FileAdmin


class TemplateView(FileAdmin):
    can_upload = True
    can_mkdir = False
    can_delete = False
    can_delete_dirs = False
    can_rename = False
    editable_extensions = ['md']

    form_base_class = SecureForm
    edit_template = 'edit_ace.html'

    def get_edit_form(self) -> Type[Any]:
        class EditForm(self.form_base_class):  # type: ignore[name-defined, misc]
            content = fields.MarkdownField(lazy_gettext('Content'), (validators.InputRequired(),))

        return EditForm
