from datetime import datetime


def validate_time_minute_str(time_str: str) -> str:
    """
    验证时间字符串是否为 %Y-%m-%d %H:%M 格式
    """
    try:
        datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        return time_str
    except ValueError as e:
        raise ValueError(f'Invalid datetime format. Expected format: YYYY-MM-DD HH:MM, got: {time_str}') from e


def validate_time_second_str(time_str: str) -> str:
    """
    验证时间字符串是否为 %Y-%m-%d %H:%M:%S 格式
    """
    try:
        datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return time_str
    except ValueError as e:
        raise ValueError(f'Invalid datetime format. Expected format: YYYY-MM-DD HH:MM:SS, got: {time_str}') from e
