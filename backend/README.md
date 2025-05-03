# P&KU Website: The Backend

TBD

## 开发

使用 python 3.11 开发，使用 poetry 管理项目。

### 依赖

- 安装依赖：`poetry install`
- 更新依赖：`poetry update`
- 导出部署时需要的依赖：`poetry export -f requirements.txt --output requirements.txt --without-hashes`
- 导出包含 `dev` 的依赖：`poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev
`

### 运行

- 运行 reducer 和 flask admin：`python3 run_reducer_admin.py`
- 运行 worker：`run_worker_api.py`

### mypy 检查

```bash
python -m mypy.dmypy run
```

### ruff 格式化与检查
```bash
# 提交前应确保运行过下面两个命令
# 格式化
ruff format
# 代码风格检查并修复
ruff check --fix

# ci 中会使用下面的命令检查
# 代码风格检查
ruff check
# 格式检查
ruff format --check
```

TBD

## License

后端部分主要基于 [Guiding Star 的后端部分](https://github.com/PKU-GeekGame/gs-backend)
开发，原项目许可证见[这个文件](./GS_LICENSE.md)。
