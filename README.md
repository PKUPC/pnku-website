# P&KU Website

## 简介

P&KU Website（暂定）是为 P&KU 这一 Puzzle Hunt 活动开发的比赛平台，目前已经基于这一平台成功举办了以下活动：
- [P&KU2](https://pnku2.pkupuzzle.art/)
- [MiaoHunt 2023](https://mh2023.puzzlehunt.cn/)
- [P&KU3（上）](https://pnku3.pkupuzzle.art/)

本项目基于 [Guiding Star](https://github.com/pku-GeekGame/guiding-star) 开发，Guiding Star 是为了 PKU GeekGame 而开发的 CTF 比赛平台，提供了一种灵活的后端架构，方便实现各种奇怪需求，非常适合 Puzzle Hunt 这一场景（出题人总是有一些妙妙点子）。

该仓库的主分支的代码一般是上次举办的活动的内容（目前是 P&KU3（上）），在活动结束后会以此为蓝本进行 bug 修复或者功能更新，在未来也许会专门设计一套题来做这个事。

由于开发者的时间和精力有限，目前开源的代码中还有很多历史遗留问题，没有完全整理好（每次办完活动后都说要整理下……然后就拖到了下次活动前，开始堆新的屎山orz）。

## 开发

如果您要基于此项目开发，请务必先阅读 [Guiding Star](https://github.com/pku-GeekGame/guiding-star) 项目的介绍，先理解后端的状态更新逻辑。

1. 准备数据库：数据库建议用 mariadb 或 mysql。数据库结构见 database 文件夹中的 sql 文件，里面包含了 P&KU3（上） 的题目信息。其他 P&KU3（上）中的数据文件见[这个仓库](https://github.com/PKUPC/pnku3-part1-data)。
2. 将 `backend/src` 中的 `custom.example.py` 和 `secret.example.py` 分别复制一份，命名为 `custom.py` 和 `secret.py`，并根据自己的需要调整。
3. 后端配置好 python 3.11 和 poetry，前端配置好 node 和 pnpm，安装好依赖后理论上就可以跑了。

## 部署

TBD

## License

本项目基于 MIT 开放源代码许可证开源，参见[这个文件](./LICENSE.md)

后端部分主要基于 [Guiding Star 的后端部分](https://github.com/PKU-GeekGame/gs-backend)
开发，原项目许可证见[这个文件](./backend/GS_LICENSE.md)。





