from email.header import Header
from email.message import Message
from email.mime.text import MIMEText
from typing import Tuple, Union

import aiosmtplib
from aiosmtplib.errors import SMTPTimeoutError

from src import secret

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


# <class 'aiosmtplib.errors.SMTPDataError'>
# (554, 'Reject by behaviour spamANTISPAM_BAT[01201311R2268S1430114234, maildocker-behaviorspam033045086103]: too frequently sending')

async def send_email(massage: Message) -> Tuple[bool, Union[None, str]]:
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
    except SMTPTimeoutError as e:
        print(e)
        return False, "发送邮件超时，请稍后再试。"
    except Exception as e:
        print("unknown email error")
        print(type(e))
        print(e)
        return False, "内部错误，请通知网站管理员"
    return True, None


async def send_reg_email(password: str, to: str) -> Tuple[bool, Union[None, str]]:
    # msg = MIMEText(password, "plain", "utf-8")
    msg = MIMEText(_HTML_TEMPLATE.format(
        PASSWORD=password,
        EMAIL=to,
    ), "html", "utf-8")
    msg["From"] = secret.EMAIL_SENDER
    msg["To"] = to

    msg["Subject"] = Header(f"账号创建通知", "utf-8")  # type:ignore[assignment]
    return await send_email(msg)
