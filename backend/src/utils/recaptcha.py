import httpx

from .utils import get_traceback
from .. import secret


async def check_recaptcha_response(res: str) -> bool:
    async with httpx.AsyncClient(http2=True) as client:
        try:
            _res = await client.get(secret.RE_CAPTCHA_VERIFY_ADDR, params={
                "response": res,
                "secret": secret.RE_CAPTCHA_SECRET,
            })
            print(_res.json())
            status = _res.json().get("success", None)
            if status:
                return True
            return False
        except Exception as e:
            print('VERIFY CAPTCHA FAIL', get_traceback(e))
            return False
