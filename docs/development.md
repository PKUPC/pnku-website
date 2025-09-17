# 开发

如果您要基于此项目开发，请务必先阅读 [Guiding Star](https://github.com/pku-GeekGame/guiding-star) 项目的介绍，先理解后端的状态更新逻辑。

1. 准备数据库：数据库建议用 mariadb 或 mysql。数据库结构见 database 文件夹中的 sql 文件，里面包含了 P&KU3（上） 的题目信息。其他 P&KU3（上）中的数据文件见[这个仓库](https://github.com/PKUPC/pnku3-part1-data)。
2. 将 `frontend/src` 中的 `setup.example.ts` 复制一份，命名为 `setup.ts`，并根据自己的需要调整。
3. 将 `backend/src` 中的 `custom.example.py` 和 `secret.example.py` 分别复制一份，命名为 `custom.py` 和 `secret.py`，并根据自己的需要调整。
4. 后端配置好 python 3.11 和 poetry，前端配置好 node 和 pnpm，安装好依赖后理论上就可以跑了。