from collections.abc import Awaitable, Callable
from functools import wraps
from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field
from sanic import Blueprint, HTTPResponse, Request, response
from sanic.blueprints import BlueprintGroup
from sanic.models.handler_types import RouteHandler

from src.custom import store_user_log
from src.state import User


if TYPE_CHECKING:
    from src.logic import Worker


ACCEPTED_WISH_VERS = ['wish.2023.v6', 'wish.sp.2023.v1']

WishHandler = Callable[..., dict[str, Any] | Awaitable[dict[str, Any]]]


def wish_response(fn: WishHandler) -> RouteHandler:
    @wraps(fn)
    async def wrapper(req: Request, *args: Any, **kwargs: Any) -> HTTPResponse:
        v = req.headers.get('X-Wish-Version', '(none)')
        if v not in ACCEPTED_WISH_VERS:
            return response.json(
                {'status': 'error', 'title': 'WISH_VERSION_MISMATCH', 'message': f'前端版本 {v} 不是最新'}
            )

        if 'worker' not in kwargs:
            response.json({'status': 'error', 'title': 'NO_WORKER', 'message': '服务暂时不可用，请稍候再来吧。'})

        retval_ = fn(req, *args, **kwargs)
        retval = (await retval_) if isawaitable(retval_) else retval_

        res = response.json(
            {
                'status': 'success',  # may be overridden by retval
                **retval,
            }
        )

        if 'user' in kwargs and kwargs['user'] is not None and isinstance(kwargs['user'], User):
            cur_user: User = kwargs['user']
            cur_user.update_cookie(res)

        return res

    return wrapper


CHECK_ORDER = ['user_login', 'user_is_staff', 'player_in_team', 'team_is_gaming', 'intro_unlock', 'game_start']


def wish_checker(
    check_list: list[
        Literal['user_login', 'player_in_team', 'user_is_staff', 'team_is_gaming', 'game_start', 'intro_unlock']
    ],
) -> Callable[[WishHandler], WishHandler]:
    if check_list is None:
        check_list = []
    check_set = set()
    if 'user_login' in check_list:
        check_set.add('user_login')
    if 'player_in_team' in check_list:
        check_set.add('user_login')
        check_set.add('player_in_team')
    if 'user_is_staff' in check_list:
        check_set.add('user_login')
        check_set.add('user_is_staff')
    if 'team_is_gaming' in check_list:
        check_set.add('user_login')
        check_set.add('player_in_team')
        check_set.add('team_is_gaming')
    if 'intro_unlock' in check_list:
        check_set.add('user_login')
        check_set.add('intro_unlock')
    if 'game_start' in check_list:
        check_set.add('user_login')
        check_set.add('game_start')

    inner_check_list = [x for x in CHECK_ORDER if x in check_set]

    # print(inner_check_list)

    def decorator(fn: WishHandler) -> WishHandler:
        @wraps(fn)
        async def wrapped(req: Request, *args: Any, **kwargs: Any) -> dict[str, Any]:
            if 'worker' not in kwargs:
                return {'status': 'error', 'title': 'NO_GAME', 'message': '服务暂时不可用'}
            worker: Worker = kwargs['worker']
            if worker.game is None:
                return {'status': 'error', 'title': 'NO_GAME', 'message': '服务暂时不可用'}

            for check in inner_check_list:
                if check == 'user_login':
                    if 'user' not in kwargs or kwargs['user'] is None:
                        return {'status': 'error', 'title': 'NO_USER', 'message': '未登录'}
                    user: User = kwargs['user']
                    err = user.check_play_game()
                    if err is not None:
                        return {'status': 'error', 'title': err[0], 'message': err[1]}
                elif check == 'player_in_team':
                    # 顺序保证了这里 user 一定存在
                    user: User = kwargs['user']  # type: ignore[no-redef]
                    if user.model.group != 'staff':
                        if user.team is None:
                            return {'status': 'error', 'title': 'NO_TEAM', 'message': '用户不在队伍中'}
                        elif user.team.is_banned:
                            return {'status': 'error', 'title': 'BAD_TEAM', 'message': '队伍已经被封禁，请联系工作人员'}
                elif check == 'game_start':
                    # 顺序保证了这里 user 一定存在
                    user: User = kwargs['user']  # type: ignore[no-redef]
                    if not user.is_staff and not worker.game_nocheck.is_game_begin():
                        store_user_log(
                            req,
                            'api.wish_checker.game_start',
                            'abnormal',
                            '在游戏开始前调用了禁止的 API。',
                            {'req_url': req.url},
                        )
                        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '游戏未开始！'}
                elif check == 'intro_unlock':
                    # 顺序保证了这里 user 一定存在
                    user: User = kwargs['user']  # type: ignore[no-redef]
                    if not user.is_staff and not worker.game_nocheck.is_intro_unlock():
                        store_user_log(
                            req,
                            'api.wish_checker.intro_unlock',
                            'abnormal',
                            '在游戏开始前调用了禁止的 API。',
                            {'req_url': req.url},
                        )
                        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '游戏未开始！'}
                elif check == 'user_is_staff':
                    # 顺序保证了这里 user 一定存在
                    user: User = kwargs['user']  # type: ignore[no-redef]
                    if not user.is_staff:
                        store_user_log(
                            req,
                            'api.wish_checker.user_is_staff',
                            'abnormal',
                            '非工作人员访问了工作人员 API。',
                            {'req_url': req.url},
                        )
                        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你不是工作人员！'}
                elif check == 'team_is_gaming':
                    # 顺序保证了这里 user 一定存在
                    user: User = kwargs['user']  # type: ignore[no-redef]
                    if not user.is_staff:
                        assert user.team is not None  # 顺序保证
                        if not user.team.gaming:
                            store_user_log(
                                req, 'api.wish_checker', 'abnormal', '队伍没在游戏中。', {'req_url': req.url}
                            )
                            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你不是工作人员！'}

            retval_ = fn(req, *args, **kwargs)
            retval = (await retval_) if isawaitable(retval_) else retval_

            return retval

        return wrapped

    return decorator


class BaseWishResponse(BaseModel):
    status: str = Field(description='状态，可以是 success error info')
    title: str | None = Field(description='info 或 error 的种类或者用于显示的标题')
    message: str | None = Field(description='success info 或 error 的返回信息，info 和 error 必须要有')


from . import game, message, puzzle, special, staff, team, ticket, upload, user


bp: BlueprintGroup = Blueprint.group(
    team.bp,
    message.bp,
    puzzle.bp,
    staff.bp,
    game.bp,
    user.bp,
    special.bp,
    ticket.bp,
    upload.bp,
    url_prefix='',
)
