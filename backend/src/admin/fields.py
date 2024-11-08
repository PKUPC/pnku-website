import datetime
import json
from typing import Any, Dict, List

import flask_admin.form
import wtforms
from markupsafe import Markup

from .. import store
from .. import utils


def timestamp_s_formatter(_view: Any, _context: Any, model: Any, name: str) -> str:
    return utils.format_timestamp(getattr(model, name))


def timestamp_ms_formatter(_view: Any, _context: Any, model: Any, name: str) -> str:
    return utils.format_timestamp(getattr(model, name) / 1000)


# noinspection PyAttributeOutsideInit
class TimestampSField(wtforms.fields.IntegerField):
    widget = wtforms.widgets.DateTimeLocalInput()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.flags.step = 1

    def _value(self) -> str:
        if self.data is not None:
            return datetime.datetime.isoformat(datetime.datetime.fromtimestamp(self.data))
        else:
            return ''

    def process_formdata(self, valuelist: List[str]) -> None:
        if valuelist:
            self.data = int(datetime.datetime.fromisoformat(valuelist[0]).timestamp())
        else:
            self.data = None


class TimestampMsField(wtforms.fields.IntegerField):
    widget = wtforms.widgets.DateTimeLocalInput()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.flags.step = 1

    def _value(self) -> str:
        if self.data is not None:
            return datetime.datetime.isoformat(datetime.datetime.fromtimestamp(int(self.data / 1000)))
        else:
            return ''

    def process_formdata(self, valuelist: List[str]) -> None:
        if valuelist:
            self.data = int(datetime.datetime.fromisoformat(valuelist[0]).timestamp() * 1000)
        else:
            self.data = None


class AceInput(wtforms.widgets.TextArea):
    def __init__(self) -> None:
        self.unique_id: str = utils.gen_random_str(8)

    def script_body(self) -> str:
        return f'''
            editor.session.setValue(textarea.value.trim());
            editor.session.on('change', ()=>{'{'}
                textarea.value = editor.session.getValue();
            {'}'});
            textarea.value = editor.session.getValue();
        '''

    def __call__(self, field: wtforms.fields.StringField, **kwargs: Any) -> Markup:
        filed_value = ""
        if field.data is not None:
            if isinstance(field.data, dict) or isinstance(field.data, list):
                filed_value = json.dumps(field.data, ensure_ascii=False)
            elif isinstance(field.data, str):
                filed_value = str(field.data)
            else:
                print("[WARNING] unknown field.data type")
                filed_value = str(field.data)

        return Markup(f'''
            <textarea {wtforms.widgets.html_params(name=field.name, id=field.id, **kwargs)} data-ace-id={self.unique_id} readonly>{Markup.escape(filed_value)}</textarea> 
            <div class="ace-editor" id="{self.unique_id}"></div>
            
            <script>
                (()=>{'{'}
                    let textarea = document.querySelector('[data-ace-id="{self.unique_id}"]');
                    let editor = ace.edit('{self.unique_id}');
                    window.editor_{self.unique_id} = editor;
                    editor.setTheme("ace/theme/sqlserver");
                    editor.session.setUseWrapMode(true);
                    editor.session.setUseSoftTabs(true);
                    {self.script_body()}
                {'}'})();
            </script>
        ''')


class SyntaxHighlightInput(AceInput):
    def __init__(self, lang: str):
        super().__init__()
        self.lang = lang

    def script_body(self) -> str:
        return f'''
            editor.session.setMode("ace/mode/{self.lang}");
            {super().script_body()}
        '''


class JsonFormattedInput(SyntaxHighlightInput):
    def __init__(self) -> None:
        super().__init__('json')

    def script_body(self) -> str:
        return f'''
            {super().script_body()}
            editor.session.setValue(JSON.stringify(JSON.parse(textarea.value), null, "\t"));
        '''


class JsonListInputWithSnippets(SyntaxHighlightInput):
    def __init__(self, snippets: Dict[str, str]):
        self.snippets = snippets
        super().__init__('json')

    def script_body(self) -> str:
        return f'''
            editor.session.setMode("ace/mode/json");
            try {'{'}
                let val = JSON.parse(textarea.value);
                editor.session.setValue(JSON.stringify((val.length ? val : []), null, "\t"));
            {'}'} catch(e) {'{'}
                editor.session.setValue(textarea.value.trim()||"[]");
            {'}'};
            editor.session.on('change', ()=>{'{'}
                textarea.value = editor.session.getValue();
            {'}'});
            textarea.value = editor.session.getValue();
        '''

    def __call__(self, field: wtforms.fields.StringField, **kwargs: Any) -> Markup:
        base_markup = super().__call__(field, **kwargs)

        snippets = [
            f'''
                <button type="button" onclick="append_snippet(editor_{self.unique_id}, '{Markup.escape(v)}');">+{Markup.escape(k)}</button>
            '''
            for k, v in self.snippets.items()
        ]

        return base_markup + Markup(f'''
            <script>
                function append_snippet(editor, s) {'{'}
                    let obj = eval(editor.getValue()); 
                    obj.push(JSON.parse(s));
                    editor.setValue(JSON.stringify(obj, null, "\t"));
                    editor.navigateFileEnd();
                    editor.scrollToLine(Infinity);
                    editor.focus();
                {'}'}
            </script>
            {"".join(snippets)}
        ''')


class JsonObjectInputWithSingleSnippet(SyntaxHighlightInput):
    def __init__(self, snippets: Dict[str, str]):
        self.snippets = snippets
        super().__init__('json')

    def script_body(self) -> str:
        return f'''
            editor.session.setMode("ace/mode/json");
            try {'{'}
                let val = JSON.parse(textarea.value);
                editor.session.setValue(JSON.stringify((typeof val === 'object' ? val : {'{}'}), null, "\t"));
            {'}'} catch(e) {'{'}
                editor.session.setValue(textarea.value.trim()||"[]");
            {'}'};
            editor.session.on('change', ()=>{'{'}
                textarea.value = editor.session.getValue();
            {'}'});
            textarea.value = editor.session.getValue();
        '''

    def __call__(self, field: wtforms.fields.StringField, **kwargs: Any) -> Markup:
        base_markup = super().__call__(field, **kwargs)

        snippets = [
            f'''
                <button type="button" onclick="use_snippet(editor_{self.unique_id}, '{Markup.escape(v)}');">{Markup.escape(k)}</button>
            '''
            for k, v in self.snippets.items()
        ]

        return base_markup + Markup(f'''
            <script>
                function use_snippet(editor, s) {'{'}
                    let obj = JSON.parse(s);
                    editor.setValue(JSON.stringify(obj, null, "\t"));
                    editor.navigateFileEnd();
                    editor.scrollToLine(Infinity);
                    editor.focus();
                {'}'}
            </script>
            {"".join(snippets)}
        ''')


class MarkdownField(wtforms.fields.TextAreaField):
    widget = SyntaxHighlightInput('markdown')


class JsonTextField(wtforms.fields.TextAreaField):
    widget = SyntaxHighlightInput('json')


class PythonField(wtforms.fields.TextAreaField):
    widget = SyntaxHighlightInput('python')


# `JsonField` should be used for a JSON sqlalchemy type, while `JsonTextField` should be used for a string type.
class JsonField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = JsonFormattedInput()


class PuzzleTriggersField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = JsonListInputWithSnippets(store.PuzzleStore.TRIGGER_SNIPPETS)


class PuzzleActionsField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = JsonListInputWithSnippets(store.PuzzleStore.ACTION_SNIPPETS)
