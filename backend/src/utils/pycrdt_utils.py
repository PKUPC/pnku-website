import json

from typing import Any

import pycrdt


def print_doc_state(doc: pycrdt.Doc[Any]) -> None:
    data = {}
    for key in doc.keys():
        if key.endswith('_text'):
            data[key] = doc.get(key, type=pycrdt.Text).to_py()
        elif key.endswith('_array'):
            data[key] = doc.get(key, type=pycrdt.Array).to_py()
        elif key.endswith('_map'):
            data[key] = doc.get(key, type=pycrdt.Map).to_py()

    # 构建调试信息字典
    debug_info = {
        'guid': doc.guid,
        'client_id': doc.client_id,
        'data': data,
    }

    # 打印格式化的 JSON
    print(json.dumps(debug_info, indent=4, ensure_ascii=False))
