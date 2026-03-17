from collections.abc import Callable
from functools import cache

import httpx

from alibabacloud_captcha20230305 import models as captcha_20230305_models  # type: ignore[import-untyped]
from alibabacloud_captcha20230305.client import Client as captcha20230305Client  # type: ignore[import-untyped]
from alibabacloud_credentials.client import Client as CredentialClient  # type: ignore[import-untyped]
from alibabacloud_credentials.models import Config as CredentialConfig  # type: ignore[import-untyped]
from alibabacloud_tea_openapi import models as open_api_models  # type: ignore[import-untyped]
from alibabacloud_tea_util import models as util_models  # type: ignore[import-untyped]

from src import secret

from .logging import LogLevel
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


@cache
def create_aliyun_client() -> captcha20230305Client:
    credential = CredentialClient(
        CredentialConfig(
            type='access_key',
            access_key_id=secret.CAPTCHA_CONFIG['access_key_id'],
            access_key_secret=secret.CAPTCHA_CONFIG['access_key_secret'],
        )
    )
    config = open_api_models.Config(credential=credential)
    config.endpoint = secret.CAPTCHA_CONFIG['endpoint']
    return captcha20230305Client(config)


async def check_aliyun_captcha_response(res: str, logger: None | Callable[[LogLevel, str, str], None] = None) -> bool:
    client = create_aliyun_client()
    verify_intelligent_captcha_request = captcha_20230305_models.VerifyIntelligentCaptchaRequest(
        captcha_verify_param=res, scene_id=secret.CAPTCHA_CONFIG['scence_id']
    )
    try:
        result = await client.verify_intelligent_captcha_with_options_async(
            verify_intelligent_captcha_request, util_models.RuntimeOptions()
        )
        if result.status_code != 200:
            if logger:
                logger(
                    'warning',
                    'captcha.check_aliyun_captcha_response',
                    f'res: {res}, status_code: {result.status_code}, message: {result.body.message}, request_id: {result.body.request_id}',
                )
            return False
        verify_code = result.body.result.verify_code
        verify_result = result.body.result.verify_result

        if verify_result:
            return True

        if logger:
            logger(
                'warning',
                'captcha.check_aliyun_captcha_response',
                f'res: {res}, verify_code: {verify_code}, verify_result: {verify_result}',
            )

        return False
    except Exception as error:
        if hasattr(error, 'message') and isinstance(error.message, str):
            error_message: str = f'res: {res}, error: {error.message}'
        else:
            error_message = f'res: {res}, unknown error: {get_traceback(error)}'
        if logger:
            logger('error', 'captcha.check_aliyun_captcha_response', error_message)
        return False
