import asyncio
import time

from flask import current_app, flash, redirect, url_for
from flask.typing import ResponseReturnValue
from flask_admin import AdminIndexView, expose

from src import utils
from src.logic.reducer import Reducer

USER_STATUS = {
    "total": "总数",
    "disabled": "已禁用",
    "have_team": "已组队",
    "not_have_team": "未组队",
}

TEAM_STATUS = {
    "total": "总数",
    "dissolved": "已解散",
    "disabled": "已禁用",
    "hide": "已隐藏",
    "preparing": "准备中",
    "gaming": "游戏中",
}

TEAM_STATISTICS = {
    "count_1": "1 人",
    "count_2": "2 人",
    "count_3": "3 人",
    "count_4": "4 人",
    "count_5": "5 人",
    "average": "平均人数",
}

TELEMETRY_FIELDS = {
    'last_update': '更新时间',
    'ws_online_clients': '在线连接',
    'ws_online_uids': '在线用户',
    'state_counter': '状态编号',
    'game_available': '比赛可用',
    'cur_tick': 'Tick',
    'n_users': '用户数',
    'n_submissions': '提交数',
}


class StatusView(AdminIndexView):  # type: ignore[misc]
    @expose('/')
    def index(self) -> ResponseReturnValue:
        reducer: Reducer = current_app.config['reducer_obj']
        reducer.received_telemetries[reducer.process_name] = (time.time(), reducer.collect_telemetry())

        st = utils.sys_status()
        sys_status = {
            'process': f'{st["process"]}',
            'load': f'{st["load_1"]} {st["load_5"]} {st["load_15"]}',
            'ram': f'used={st["ram_used"]:.2f}G, free={st["ram_free"]:.2f}G',
            'swap': f'used={st["swap_used"]:.2f}G, free={st["swap_free"]:.2f}G',
            'disk': f'used={st["disk_used"]:.2f}G, free={st["disk_free"]:.2f}G',
        }

        users_cnt_by_group, teams_cnt, teams_statistic_cnt = reducer.collect_game_stat()

        return self.render(  # type: ignore[no-any-return]
            'status.html',

            sys_status=sys_status,

            user_fields=USER_STATUS,
            user_data=users_cnt_by_group,

            team_fields=TEAM_STATUS,
            team_data=teams_cnt,

            teams_statistic_fields=TEAM_STATISTICS,
            teams_statistic_data=teams_statistic_cnt,

            tel_fields=TELEMETRY_FIELDS,
            tel_data={
                worker_name: {
                    'last_update': f'{int(time.time() - last_update):d}s',
                    **tel_dict,
                } for worker_name, (last_update, tel_dict) in sorted(reducer.received_telemetries.items())
            },
        )

    @expose('/clear_telemetry')
    def clear_telemetry(self) -> ResponseReturnValue:
        reducer: Reducer = current_app.config['reducer_obj']
        reducer.received_telemetries.clear()

        flash('已清空遥测数据', 'success')
        return redirect(url_for('.index'))

    @expose('/test_push')
    def test_push(self) -> ResponseReturnValue:
        loop: asyncio.AbstractEventLoop = current_app.config['reducer_loop']
        reducer: Reducer = current_app.config['reducer_obj']

        async def run_push() -> None:
            reducer.log('error', 'admin.test_push', '这是一条测试消息')

        asyncio.run_coroutine_threadsafe(run_push(), loop)

        flash('已发送测试消息', 'success')
        return redirect(url_for('.index'))

    @expose('/update_media')
    def update_media(self) -> ResponseReturnValue:
        loop: asyncio.AbstractEventLoop = current_app.config['reducer_loop']

        asyncio.run_coroutine_threadsafe(utils.update_media_files(), loop)

        flash('已更新图片', 'success')
        return redirect(url_for('.index'))

    @expose('/prepare_media')
    def prepare_media(self) -> ResponseReturnValue:
        loop: asyncio.AbstractEventLoop = current_app.config['reducer_loop']

        asyncio.run_coroutine_threadsafe(utils.prepare_media_files(), loop)

        flash('已更新图片', 'success')
        return redirect(url_for('.index'))
