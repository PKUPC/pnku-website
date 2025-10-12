from __future__ import annotations

from typing import TYPE_CHECKING

from flask import flash, make_response, redirect, url_for
from flask.typing import ResponseReturnValue
from flask_admin import BaseView, expose

from src import secret
from src.logic import glitter
from src.logic.reducer import Reducer

from ..utils import emit_event, run_reducer_callback


if TYPE_CHECKING:
    from src.logic.reducer import Reducer


class DebugView(BaseView):  # type: ignore[misc]
    @expose('/')
    def index(self) -> ResponseReturnValue:
        return self.render('debug.html')  # type: ignore[no-any-return]

    @expose('/hello_world')
    def hello_world(self) -> ResponseReturnValue:
        flash('hello world')
        return redirect(url_for('.index'))

    @expose('/get_puzzles_state')
    def get_puzzles_state(self) -> ResponseReturnValue:
        def task(reducer: Reducer) -> str:
            puzzle_structure = reducer._game.puzzles.puzzles_by_structure
            rst = ''
            for category in puzzle_structure:
                rst += category + ':\n'
                for subcategory in puzzle_structure[category]:
                    rst += f'    {subcategory}:\n'
                    for puzzle in puzzle_structure[category][subcategory]:
                        rst += f'        {puzzle.model.key}: {puzzle.model.sorting_index} | {puzzle.model.title}\n'
            return rst

        result = run_reducer_callback(task)

        resp = make_response(result, 200)
        resp.mimetype = 'text/plain'
        return resp

    @expose('/emit_reinit_game_event')
    def emit_reinit_game_event(self) -> ResponseReturnValue:
        if not secret.DEBUG_MODE:
            flash('debug mode is not enabled')
            return redirect(url_for('.index'))

        emit_event(glitter.EventType.REINIT_GAME, 1)
        flash('done')
        return redirect(url_for('.index'))
