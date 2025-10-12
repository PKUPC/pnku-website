import json

from collections.abc import Hashable
from typing import Any

from sanic import Blueprint, HTTPResponse, Request, response

from src import adhoc, secret, utils
from src.adhoc.constants import PUZZLE_AREA_NAMES, VALID_AREA_NAMES
from src.logic import Worker
from src.state import Hint
from src.store import HintStore


bp = Blueprint('archive', url_prefix='/archive')

if secret.USE_ARCHIVE_API:

    @bp.route('/game_info.json')
    async def game_info_json(_req: Request, worker: Worker) -> HTTPResponse:
        board_key_to_icon = {
            'score_board': 'ranking',
            'first_blood': 'first-blood',
            'speed_run': 'thunder',
        }

        unlock_areas = [
            adhoc.areas.data.AREA_LIST[2],
            adhoc.areas.data.AREA_LIST[3],
            adhoc.areas.data.AREA_LIST[4],
            adhoc.areas.data.AREA_LIST[5],
        ]

        result_dict = {
            'user': None,
            'team': None,
            'game': {
                'login': None,
                'isPrologueUnlock': True,
                'isGameBegin': True,
                'isGameEnd': True,
                'start_ts': worker.game_nocheck.game_begin_timestamp_s,
                'aboutTemplates': [],
                'boards': [
                    {
                        'key': board,
                        'icon': board_key_to_icon.get(worker.game_nocheck.boards[board].key, 'unknown'),
                        'name': worker.game_nocheck.boards[board].name,
                    }
                    for board in worker.game_nocheck.boards
                ],
            },
            'feature': {
                'push': False,
                'debug': False,
                'email_login': False,
                'sso_login': False,
            },
            'areas': unlock_areas,
        }

        return response.text(json.dumps(result_dict, ensure_ascii=False, indent=4))

    @bp.route('/boards.json')
    async def boards_json(_req: Request, worker: Worker) -> HTTPResponse:
        result_dict = {}
        for board in worker.game_nocheck.boards:
            board_obj = worker.game_nocheck.boards[board]
            result_dict[board] = {
                **board_obj.get_rendered(False),
                'type': board_obj.board_type,
                'desc': board_obj.desc,
            }

        return response.text(json.dumps(result_dict, ensure_ascii=False, indent=4))

    @bp.route('/misc.json')
    async def misc_json(_req: Request, worker: Worker) -> HTTPResponse:
        result_dict = {
            'announcements': [ann.describe_json(None) for ann in worker.game_nocheck.announcements.list],
            'schedule': [
                {
                    'timestamp_s': trigger.timestamp_s,
                    'name': trigger.name,
                    'status': (
                        'prs'
                        if trigger.tick == worker.game_nocheck.cur_tick
                        else 'ftr'
                        if trigger.tick > worker.game_nocheck.cur_tick
                        else 'pst'
                    ),
                }
                for trigger in worker.game_nocheck.trigger.stores
            ],
        }

        return response.text(json.dumps(result_dict, ensure_ascii=False, indent=4))

    @bp.route('/templates.json')
    async def templates_json(_req: Request, worker: Worker) -> HTTPResponse:
        template_list = [
            'acknowledgements',
            'faq',
            'introduction',
            'tools',
            'endoftime',
            'ending',
            'prologue',
            'day3_premeta',
            'staff',
            'day1_intro',
            'day1_meta',
            'day2_intro',
            'day2_meta',
            'day3_intro',
            'day3_meta1',
            'day3_meta2',
            'day3_meta3',
        ]
        for puzzle_key in worker.game_nocheck.puzzles.puzzle_by_key:
            template_list.append(f'solutions/{puzzle_key}')

        result_dict = {}

        for filename in template_list:
            p = (secret.TEMPLATE_PATH / f'{filename}.md').resolve()
            if not p.is_file():
                result_dict[filename] = '暂无内容'
            else:
                with p.open('r', encoding='utf-8') as f:
                    md = f.read()
                try:
                    html = utils.render_template(md, {'group': 'player', 'tick': 9000, 'archived': True})
                    result_dict[filename] = html
                except Exception:
                    result_dict[filename] = '<i>（模板渲染失败）</i>'

        return response.text(json.dumps(result_dict, ensure_ascii=False, indent=4))

    @bp.route('/area_detail.json')
    async def area_detail_json(_req: Request, worker: Worker) -> HTTPResponse:
        user_1 = worker.game_nocheck.users.user_by_id[1]
        areas = VALID_AREA_NAMES
        result_dict = {area_name: adhoc.get_area_info(area_name, user_1, worker) for area_name in areas}
        return response.text(json.dumps(result_dict, ensure_ascii=False, indent=4))

    @bp.route('/puzzle_details.json')
    async def puzzle_details_json(_req: Request, worker: Worker) -> HTTPResponse:
        result_dict = {}

        for puzzle_key in worker.game_nocheck.puzzles.puzzle_by_key:
            puzzle = worker.game_nocheck.puzzles.puzzle_by_key[puzzle_key]
            user_1 = worker.game_nocheck.users.user_by_id[1]
            puzzle_list: list[Any] = adhoc.gen_puzzle_structure_by_puzzle(puzzle, user_1, worker)

            if puzzle_key == 'day3_premeta':
                puzzle_status = 'special'
            else:
                puzzle_status = 'untouched'

            result_dict[puzzle_key] = {
                'key': puzzle.model.key,
                'title': puzzle.model.title,
                'actions': puzzle.model.describe_actions(),
                'status': puzzle_status,
                'puzzle_list': puzzle_list,
                **adhoc.get_more_puzzle_detail(puzzle),
            }
            if len(puzzle.model.clipboard) > 0:
                result_dict[puzzle_key]['clipboard'] = [x.model_dump() for x in puzzle.model.clipboard]
            extra: tuple[tuple[str, str | int | tuple[Hashable, ...]], ...] = tuple()
            if puzzle_key == 'day2_01':
                extra = (('state_id', 1),)
            if puzzle_key == 'day3_20':
                extra = (('state_id', 1),)
            result_dict[puzzle_key]['desc'] = puzzle.render_desc_for_archive(extra)

        return response.text(json.dumps(result_dict, ensure_ascii=False, indent=4))

    @bp.route('/puzzle_hints.json')
    async def puzzle_hints_json(_req: Request, worker: Worker) -> HTTPResponse:
        result_dict = {}

        for puzzle_key in worker.game_nocheck.puzzles.puzzle_by_key:
            rst: list[Hint] = worker.game_nocheck.hints.hint_by_key.get(puzzle_key, [])
            result_dict[puzzle_key] = [
                {
                    'id': hint.model.id,
                    'question': hint.model.question,
                    'answer': hint.model.answer,
                    'type': HintStore.HintType.dict().get(hint.model.type, '未知'),
                    # "type": hint.store.type,
                    'provider': hint.model.extra.provider,
                    'price': [{'type': x.type, 'name': x.type.value, 'price': x.price} for x in hint.model.extra.price],
                    'unlock': True,
                    'effective_after_ts': hint.model.effective_after_ts,
                }
                for idx, hint in enumerate(rst)
            ]

        return response.text(json.dumps(result_dict, ensure_ascii=False, indent=4))

    @bp.route('/puzzle_triggers.json')
    async def puzzle_triggers_json(_req: Request, worker: Worker) -> HTTPResponse:
        result_dict = {}
        for puzzle_key in worker.game_nocheck.puzzles.puzzle_by_key:
            triggers = {}
            puzzle = worker.game_nocheck.puzzles.puzzle_by_key[puzzle_key]
            for trigger in puzzle.model.triggers:
                cleaned_value = utils.clean_submission(trigger.value)
                triggers[cleaned_value] = {
                    'type': trigger.type,
                    'info': trigger.info,
                }
                if triggers[cleaned_value]['type'] == 'answer' and triggers[cleaned_value]['info'] in ['答案正确', '']:
                    triggers[cleaned_value]['info'] = '答案正确！'
            result_dict[puzzle_key] = triggers

        return response.text(json.dumps(result_dict, ensure_ascii=False, indent=4))

    @bp.route('/puzzle_list.json')
    async def puzzle_list_json(_req: Request, worker: Worker) -> HTTPResponse:
        user_1 = worker.game_nocheck.users.user_by_id[1]
        area_list = PUZZLE_AREA_NAMES
        rst_data = []
        for area_name in area_list:
            rst_data.append(adhoc.get_area_info(area_name, user_1, worker))

        return response.text(json.dumps(rst_data, ensure_ascii=False, indent=4))

    @bp.route('/story_list.json')
    async def story_list_json(_req: Request, worker: Worker) -> HTTPResponse:
        user_1 = worker.game_nocheck.users.user_by_id[1]
        rst = adhoc.get_story_list(user_1)

        return response.text(json.dumps(rst, ensure_ascii=False, indent=4))
