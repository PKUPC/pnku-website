from collections.abc import Callable
from email.header import Header
from email.message import Message
from email.mime.text import MIMEText

import aiosmtplib

from aiosmtplib.errors import (
    SMTPRecipientRefused,
    SMTPTimeoutError,
)

from src import secret
from src.utils.logging import LogLevel


_HTML_TEMPLATE = """
<html>
<head></head>
<body>
<div style="color:#31353B; font-size:14px; text-align:left; background:#FFFFFF; max-width: 480px; margin: auto; border-radius: 8px; box-shadow: 8px rgba(0, 0, 0, 0.1); padding: 20px;">

    <div style="font-size:18px; margin-top: 20px;">
        <p>感谢您注册!</p>
        <p>请到 <a href="https://pnku3.pkupuzzle.art" style="color: #007BFF;" target="_self" rel="noopener noreferrer">https://pnku3.pkupuzzle.art</a> 登录。</p>
        <p>如果您有任何问题或需要进一步的帮助，请随时联系我们。</p>
        <p>您的密码是：</p>
        <p style="background-color: #F5F5F5; padding: 10px; border-radius: 5px; text-align: center;"><span style="color:#565A5C;font-size:32px;">{PASSWORD}</span></p>
        <p>如果你错误地收到了此电子邮件，你可以放心的无需执行任何操作！</p>
        <p style="color: #ABADAE; font-size: 12px;">此为系统邮件，请勿回复。</p>
    </div>

    <div style="margin:20px auto; text-align: center;">
        <div style="color:#ABADAE; font-size:14px; margin:10px 0;">
            P&KU &copy; 2024 - All Rights Reserved.<br />
            This message was sent to <a style="color: #007BFF;">{EMAIL}</a>.
        </div>
    </div>
</div>
</body>
</html>

"""


def exception_handler(exception: Exception, logger: Callable[[LogLevel, str, str], None]) -> str:
    """
    处理邮件发送异常，记录日志并返回用户友好的错误消息。

    Args:
        exception: 捕获的异常对象
        logger: 日志记录函数，格式为 log(level: str, module: str, message: str)

    Returns:
        返回给用户看的错误消息字符串
    """
    exception_type = type(exception).__name__
    exception_msg = str(exception)

    # 记录异常详细信息
    logger('error', 'email.exception_handler', f'邮件发送异常: {exception_type} - {exception_msg}')

    # 超时错误 - 可以给用户看
    if isinstance(exception, SMTPTimeoutError):
        return '邮件发送超时，请稍后再试。如果您反复遇到此问题，请联系工作人员。'

    # 收件人被拒绝 - 可以给用户看
    if isinstance(exception, SMTPRecipientRefused):
        recipient = getattr(exception, 'recipient', '未知')
        return f'邮箱地址 {recipient} 无效或被拒绝，请检查邮箱地址是否正确。'

    return '内部错误，请联系工作人员。'


async def send_email(massage: Message) -> tuple[bool, None | Exception]:
    """
    发送邮件。

    Returns:
        (成功标志, None或异常对象): 成功时返回 (True, None)，失败时返回 (False, Exception)
    """
    try:
        await aiosmtplib.send(
            massage,
            sender=secret.EMAIL_SENDER,
            hostname=secret.EMAIL_HOSTNAME,
            port=secret.EMAIL_PORT,
            username=secret.EMAIL_USERNAME,
            password=secret.EMAIL_PASSWORD,
            timeout=secret.EMAIL_TIMEOUT,
            use_tls=secret.EMAIL_USE_TLS,
        )
    except Exception as e:
        return False, e
    return True, None


async def send_reg_email(password: str, to: str) -> tuple[bool, None | Exception]:
    msg = MIMEText(
        _HTML_TEMPLATE.format(
            PASSWORD=password,
            EMAIL=to,
        ),
        'html',
        'utf-8',
    )
    msg['From'] = secret.EMAIL_SENDER
    msg['To'] = to

    msg['Subject'] = Header('账号创建通知', 'utf-8')  # type:ignore[assignment]
    return await send_email(msg)
