# P&KU Website: The Backend

TBD

## 开发

使用 python 3.11 开发，使用 poetry 管理项目。

### 依赖

- 安装依赖：`poetry install`
- 更新依赖：`poetry update`
- 导出部署时需要的依赖：`poetry export -f requirements.txt --output requirements.txt --without-hashes`

### 运行

- 运行 reducer 和 flask admin：`python3 run_reducer_admin.py`
- 运行 worker：`run_worker_api.py`

### mypy 检查

```bash
python3 -m mypy.dmypy run
```

TBD

## License

后端部分主要基于 [Guiding Star 的后端部分](https://github.com/PKU-GeekGame/gs-backend)
开发，原项目许可证见[这个文件](./GS_LICENSE.md)。
