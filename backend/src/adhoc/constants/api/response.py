from typing import Any, Final


GAME_MESSAGES: Final[dict[str, str]] = {
    # error
    'AREA_NOT_FOUND': '区域不存在！',
    'BOARD_NOT_FOUND': '排行榜不存在！',
    'NO_GAME': '服务暂时不可用',
    'GAME_NOT_START': '游戏未开始！',
    'TEAM_NOT_START': '队伍未开始游戏！',
    'INTRO_LOCK': '序章尚未开放!',
}

MESSAGE_MESSAGES: Final[dict[str, str]] = {
    # error
    'PLAYGROUND_BAD_REQUEST': '在目前的游戏模式下无法使用此操作！',
    'BANNED': '您已被禁用该功能！',
    'GAME_END': '游戏已结束！',
    'WRONG_TEAM_ID': '队伍 id 出错！',
    'TEAM_ID_NOT_FOUND': '队伍id不存在！',
    'WRONG_TYPE': 'content type 错误',
    'INVALID_LENGTH': '消息长度错误，消息长度应在1到400之间',
    'SEND_MSG_TO_STAFF': '不能给 staff 队伍发消息，别捣乱了！',
    'STAFF_INVALID_API': 'staff 不能调这个接口',
    'WRONG_MSG_ID': '消息 id 出错！',
}

PUZZLE_MESSAGES: Final[dict[str, str]] = {
    # error
    'GAME_END': '游戏已结束！',
    'ANSWER_TOO_LONG': '答案长度应在1到100之间。',
    'PUZZLE_NOT_FOUND': '谜题不存在！',
    'STAFF_INVALID_API': 'staff 不能调这个接口',
}

USER_MESSAGES: Final[dict[str, str]] = {
    # error
    'GAME_END': '游戏已结束！',
    'RATE_LIMIT': '提交太频繁，请等待 {seconds:.1f} 秒',
    'INVALID_PARAM_MISSING_NICKNAME': '缺少昵称信息',
    'INVALID_PARAM_EMPTY_NICKNAME': '昵称不能为空',
    'INVALID_OPERATION_CHANGE_PASSWORD': '测试用户不能更改密码',
    'WRONG_PASSWORD': '原始密码错误',
    'REDUCER_ERROR': '{error}',
}

TICKET_MESSAGES: Final[dict[str, str]] = {
    'SUCCESS': '完成！',
    'SEND_SUCCESS': '发送成功！',
    'BAD_REQUEST': '请求不合法！',
    'BANNED': '您已被禁用该功能！',
    'GAME_END': '活动已结束！',
    'ABNORMAL': '提问内容的长度应当在1到400字之间。',
    'PLAYGROUND_FORBIDDEN': '在目前的游戏模式下无法使用此操作！',
    'PUZZLE_NOT_FOUND': '谜题不存在！',
    'PUZZLE_NOT_UNLOCKED': '题目未解锁！',
    'TICKET_NOT_FOUND': '不存在的数据！',
    'TICKET_FORBIDDEN': '你无法使用这个操作！',
    'TICKET_ALREADY_OPEN': '你不能重新打开工单！异常行为已记录！',
    'MANUAL_HINT_BANNED': '你的队伍被禁止发送站内信！',
    'MANUAL_HINT_DISABLED': '你和芈雨还有未完成的神谕请求，现在不能发起新请求。',
    'MANUAL_HINT_COOLDOWN': '题目解锁 2 个小时后才能申请神谕。',
    'STAFF_FORBIDDEN': 'staff 不支持该请求。',
    'DISABLED_BY_STAFF': '芈雨还没有回复你的请求，你暂时无法和芈雨继续交流。',
    'CLOSED_TICKET': '该会话已关闭，你无法再发送新的信息。',
}


def response_message(title: str, status: str = 'success', **kwargs: Any) -> dict[str, Any]:
    template = TICKET_MESSAGES.get(title, title)
    message = template.format(**kwargs)
    return {'status': status, 'title': title, 'message': message}
