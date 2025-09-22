# 开发

如果您要基于此项目开发，请务必先阅读 [Guiding Star](https://github.com/pku-GeekGame/guiding-star) 项目的介绍，先理解后端的状态更新逻辑。

1. 准备数据库：数据库建议用 mariadb（兼容 mysql）。数据库结构见 database 文件夹中的 sql 文件，包括以下内容：
   - `structure.sql`: 数据库基础结构
   - `puzzle.sql`: P&KU3（上）的题目数据
   - `hint.sql`: P&KU3（上）的提示数据
   - `init_dev_data.sql`: 基础的开发数据，包括初始化的 trigger、game_policy 数据等
2. 将 `frontend/src` 中的 `setup.example.ts` 复制一份，命名为 `setup.ts`，并根据自己的需要调整。
3. 将 `backend/src` 中的 `custom.example.py` 和 `secret.example.py` 分别复制一份，命名为 `custom.py` 和 `secret.py`，并根据自己的需要调整。
4. 准备其他数据文件，P&KU3（上）中的数据文件见[这个仓库](https://github.com/PKUPC/pnku3-part1-data)，直接在项目根目录下运行 `git clone https://github.com/PKUPC/pnku3-part1-data data` 即可，然后在 backend/secret.py 下配置好路径。
5. 后端配置好 python 3.11 和 uv，前端配置好 node 和 pnpm，安装好依赖后理论上就可以跑了。
