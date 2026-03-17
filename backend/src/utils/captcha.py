import httpx

from src import secret

from .system import get_traceback


async def check_recaptcha_response(res: str) -> bool:
    async with httpx.AsyncClient(http2=True) as client:
        try:
            _res = await client.get(
                secret.CAPTCHA_CONFIG['verify_addr'],
                params={
                    'response': res,
                    'secret': secret.CAPTCHA_CONFIG['secret'],
                },
            )
            print(_res.json())
            status = _res.json().get('success', None)
            if status:
                return True
            return False
        except Exception as e:
            print('VERIFY CAPTCHA FAIL', get_traceback(e))
            return False
