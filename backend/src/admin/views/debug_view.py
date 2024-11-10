from flask import current_app, make_response
from flask.typing import ResponseReturnValue
from flask_admin import BaseView, expose

from src.logic.reducer import Reducer


class DebugView(BaseView):  # type: ignore[misc]
    @expose('/')
    def index(self) -> ResponseReturnValue:
        return self.render('debug.html')  # type: ignore[no-any-return]

    @expose('/get_puzzles_state')
    def get_puzzles_state(self) -> ResponseReturnValue:
        reducer: Reducer = current_app.config['reducer_obj']

        puzzle_structure = reducer._game.puzzles.puzzles_by_structure
        rst = ''
        for category in puzzle_structure:
            rst += category + ':\n'
            for subcategory in puzzle_structure[category]:
                rst += f'    {subcategory}:\n'
                for puzzle in puzzle_structure[category][subcategory]:
                    rst += f'        {puzzle.model.key}: {puzzle.model.sorting_index} | {puzzle.model.title}\n'

        resp = make_response(rst, 200)
        resp.mimetype = 'text/plain'
        return resp
