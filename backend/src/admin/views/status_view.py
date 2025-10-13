import asyncio
import time

from typing import Any

from flask import current_app, flash, redirect, url_for
from flask.typing import ResponseReturnValue
from flask_admin import AdminIndexView, expose

from src import secret, utils
from src.logic.reducer import Reducer

from ..utils import run_reducer_callback


USER_STATUS = {
    'total': '总数',
    'disabled': '已禁用',
    'have_team': '已组队',
    'not_have_team': '未组队',
}

TEAM_STATUS = {
    'total': '总数',
    'dissolved': '已解散',
    'disabled': '已禁用',
    'hide': '已隐藏',
    'preparing': '准备中',
    'gaming': '游戏中',
}

TEAM_STATISTICS = {f'count_{i}': f'{i} 人' for i in range(1, secret.TEAM_MAX_MEMBER + 1)}
TEAM_STATISTICS['average'] = '平均人数'

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
        def get_received_telemetries(reducer: Reducer) -> list[tuple[str, tuple[float, dict[str, Any]]]]:
            reducer.received_telemetries[reducer.process_name] = (time.time(), reducer.collect_telemetry())
            return list(reducer.received_telemetries.items())

        received_telemetries = run_reducer_callback(get_received_telemetries)

        users_cnt_by_group, teams_cnt, teams_statistic_cnt = run_reducer_callback(
            lambda reducer: reducer.collect_game_stat()
        )

        st = utils.sys_status()
        sys_status = {
            'process': f'{st["process"]}',
            'load': f'{st["load_1"]} {st["load_5"]} {st["load_15"]}',
            'ram': f'used={st["ram_used"]:.2f}G, free={st["ram_free"]:.2f}G',
            'swap': f'used={st["swap_used"]:.2f}G, free={st["swap_free"]:.2f}G',
            'disk': f'used={st["disk_used"]:.2f}G, free={st["disk_free"]:.2f}G',
        }

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
                }
                for worker_name, (last_update, tel_dict) in sorted(received_telemetries)
            },
        )

    @expose('/clear_telemetry')
    def clear_telemetry(self) -> ResponseReturnValue:
        run_reducer_callback(lambda reducer: reducer.received_telemetries.clear())

        flash('已清空遥测数据', 'success')
        return redirect(url_for('.index'))

    @expose('/test_push')
    def test_push(self) -> ResponseReturnValue:
        run_reducer_callback(lambda reducer: reducer.log('error', 'admin.test_push', '这是一条测试消息'))

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
