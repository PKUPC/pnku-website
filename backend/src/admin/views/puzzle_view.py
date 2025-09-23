import json

from typing import Any, Optional

import flask_admin

from flask import current_app, flash, make_response, redirect, request
from flask.typing import ResponseReturnValue
from flask_admin import expose
from flask_admin.actions import action
from sqlalchemy import select
from wtforms import Form

from src import adhoc
from src.admin import fields
from src.logic import glitter
from src.logic.reducer import Reducer
from src.store import PuzzleStore, PuzzleStoreModel

from .base_view import BaseView


class ClipboardField(flask_admin.form.JSONField):  # type: ignore[misc]
    widget = fields.JsonFormattedInput()


class PuzzleView(BaseView):
    list_template = 'list_puzzle.html'
    can_delete = False
    can_create = False

    column_exclude_list = ['content_template', 'clipboard']
    column_default_sort = 'sorting_index'
    column_formatters = {
        'actions': lambda _v, _c, model, _n: '；'.join([f'[{a["type"]}] {a["name"]}' for a in model.actions]),
        'triggers': lambda _v, _c, model, _n: '；'.join([f'{f["type"]}: {f["value"]}' for f in model.triggers]),
        'puzzle_metadata': lambda _v, _c, model, _n: (
            f'type: {model.puzzle_metadata.get("type", "unknown")}; '
            f'author: {model.puzzle_metadata.get("author", "unknown")}'
        ),
    }
    column_descriptions = {
        'key': '题目唯一 ID，将会显示在 URL 中，比赛中不要随意修改，否则会导致已有提交失效',
        'sorting_index': '越小越靠前',
        'content_template': '支持 Markdown 和 Jinja2 模板（group: Optional[str]、tick: int）',
        'puzzle_metadata': '题目的其他元信息',
        'actions': '题面底部展示的动作列表',
    }

    form_widget_args = {
        'key': {
            'readonly': True,
        }
    }
    form_overrides = {
        'content_template': fields.MarkdownField,
        'puzzle_metadata': fields.JsonField,
        'actions': fields.PuzzleActionsField,
        'triggers': fields.PuzzleTriggersField,
        'clipboard': ClipboardField,
    }
    form_choices = {
        'category': [(x, x) for x in adhoc.PUZZLE_CATEGORY_LIST],
    }

    @staticmethod
    def _export_puzzle(puzzle: PuzzleStore) -> dict[str, Any]:
        return {
            'key': puzzle.key,
            'title': puzzle.title,
            'category': puzzle.category,
            'subcategory': puzzle.subcategory,
            'sorting_index': puzzle.sorting_index,
            'content_template': puzzle.content_template,
            'clipboard': puzzle.clipboard,
            'puzzle_metadata': puzzle.puzzle_metadata,
            'actions': puzzle.actions,
            'triggers': puzzle.triggers,
        }

    @staticmethod
    def _import_puzzle(data: dict[str, Any], puzzle: PuzzleStore) -> None:
        puzzle.key = data['key']
        puzzle.title = data['title']
        puzzle.category = data['category']
        puzzle.subcategory = data['subcategory']
        puzzle.sorting_index = data['sorting_index']
        puzzle.content_template = data['content_template']
        puzzle.clipboard = data['clipboard']
        puzzle.puzzle_metadata = data['puzzle_metadata']
        puzzle.actions = data['actions']
        puzzle.triggers = data['triggers']

    @expose('/import_json', methods=['GET', 'POST'])
    def import_json(self) -> ResponseReturnValue:
        url = request.args.get('url', self.get_url('.index_view'))

        if request.method == 'GET':
            return self.render('import_puzzle.html')  # type: ignore[no-any-return]
        else:
            reducer: Reducer = current_app.config['reducer_obj']
            puzzles = json.loads(request.form['imported_data'])

            touched_ids = []
            failed_puzzles = []

            with reducer.SqlSession() as session:
                n_added = 0
                n_modified = 0
                n_failed = 0
                for puzzle_data in puzzles:
                    puzzle: PuzzleStore | None = session.execute(
                        select(PuzzleStore).where(PuzzleStore.key == puzzle_data['key'])
                    ).scalar()

                    add_flag = False
                    if puzzle is None:
                        puzzle = PuzzleStore()
                        add_flag = True

                    self._import_puzzle(puzzle_data, puzzle)

                    rst, _ = puzzle.validate()
                    if not rst:
                        n_failed += 1
                        failed_puzzles.append(puzzle_data['key'])
                        continue

                    if add_flag:
                        n_added += 1
                    else:
                        n_modified += 1

                    session.add(puzzle)
                    session.flush()
                    touched_ids.append(puzzle.id)

                session.commit()

            for puzzle_id in touched_ids:
                self.emit_event(glitter.EventType.UPDATE_PUZZLE, puzzle_id)

            if n_failed == 0:
                flash(f'成功增加 {n_added} 个题目、修改 {n_modified} 个题目。', 'success')
            else:
                flash(
                    f'成功增加 {n_added} 个题目、修改 {n_modified} 个题目。\n失败题目：{str(failed_puzzles)}', 'success'
                )

            return redirect(url)

    @action('export', 'Export JSON')
    def action_export(self, puzzle_ids: list[int]) -> ResponseReturnValue:
        reducer: Reducer = current_app.config['reducer_obj']
        puzzles = [
            self._export_puzzle(reducer.game_nocheck.puzzles.puzzle_by_id[int(ch_id)]._store) for ch_id in puzzle_ids
        ]

        resp = make_response(json.dumps(puzzles, indent=1, ensure_ascii=False), 200)
        resp.mimetype = 'text/plain'
        return resp

    def create_form(self, **kwargs: Any) -> Form:
        form = super().create_form(**kwargs)
        if form.puzzle_metadata.data is None:
            form.puzzle_metadata.data = json.loads(PuzzleStore.METADATA_SNIPPET)
        return form  # type: ignore  # create_form itself returns Any

    def on_form_prefill(self, *args: Any, **kwargs: Any) -> None:
        flash('警告：比赛过程中修改题目信息需要重新载入游戏（目前需要手动重启）', 'warning')
        # flash('警告：增删题目或者修改 flags、effective_after 字段会重算排行榜', 'warning')

    def on_model_change(self, form: Any, model: PuzzleStore, is_created: bool) -> None:
        rst, e = model.validate()
        if not rst:
            assert e is not None
            raise e

    def after_model_touched(self, model: PuzzleStore) -> None:
        model.validated_model()
        self.emit_event(glitter.EventType.UPDATE_PUZZLE, model.id)
