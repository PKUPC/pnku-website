import ast

from typing import Any


def pack_rep(data: dict[str, Any]) -> str:
    return 'DICT' + str(data)


def unpack_rep(data: str) -> dict[str, Any]:
    if data.startswith('DICT'):
        res_dict: dict[str, Any] = ast.literal_eval(data[4:])
        return res_dict
    return {'status': 'error', 'title': '出错了！', 'message': data}
