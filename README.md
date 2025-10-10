# P&KU Website

## 简介

P&KU Website（~~说不定以后会改名为 Ether Strike~~）是为 P&KU 这一 Puzzle Hunt 活动开发的网站。目前已经基于这一平台成功举办了以下活动：

- [P&KU2](https://pnku2.pkupuzzle.art/)
- [MiaoHunt 2023](https://mh2023.puzzlehunt.cn/)
- [P&KU3（上）](https://pnku3.pkupuzzle.art/)
- [Golden Puzzle Hunt](https://goldenph.art/)\*

其中标 \* 的活动是活动组织方自行基于本项目开发的。


本项目服务端的设计思路源自 [Guiding Star](https://github.com/pku-GeekGame/guiding-star) 平台，实现较为特殊。本质是将服务端实现为了一个状态机，数据库中只存储操作，所有状态都由计算得到，并且仅保存在内存中。因此在开发时很少需要关注对数据库的操作，只需要编写状态转移逻辑，并且可以自由地增添状态（可以参考[后端的活动逻辑实现代码](backend/src/adhoc/state)）。

目前本项目的主要设计目标为极致的灵活性而非易用性，目标是熟悉代码的开发者可以快速地开发各种灵活的需求，具有较高的学习成本。并且目前这套完全使用状态机的设计也较为激进，可以说是一个较为实验性的项目，<strong>不建议在不完全了解代码的情况下选择本项目，请优先选择更加完善和成熟的 [gph-site](https://github.com/galacticpuzzlehunt/gph-site) 或者 [CCXC Engine](https://engine.ccbcarchive.com/)。</strong>如果您确实对本项目感兴趣，欢迎直接与开发者交流。

由于开发者的时间和精力有限，目前开源的代码中还有很多历史遗留问题，没有完全整理好（每次办完活动后都说要整理下……然后就拖到了下次活动前，开始堆新的屎山 orz）。

## 开发状态说明

本项目的开发周期主要取决于项目维护者参与举办的活动周期（主要是 P&KU，有空的时候也会参与其他活动，例如 MiaoHunt、[数据删除] 等）。

在一个活动结束后，相关改动会合并到该仓库的主分支中，之后会以此为蓝本进行 bug 修复或者一些小功能更新。在未来也许会专门设计一套题来做这个事，**但是由于时间和精力的限制，在功能完善前，本项目将会长期处于此状态——代码中会包含很多上次活动遗留的特殊逻辑**。目前在迭代中会逐步将活动的特殊逻辑收敛到 `backend/src/adhoc` 下。

在下次活动之前，可能会进行一些重构和基建建设的工作，会有较多的改动，但是仍然基于上次活动开发。这一阶段的代码可能没有经过完整的测试和上线验证，在这些改动开始之前会将上次活动内容存档到 archive/ 下的分支。在建设到一定程度之后，会基于此时的版本进行封闭开发，期间大概率不会更新本仓库，直到下次活动结束。

目前本项目正在为下次活动做准备中，**当前主分支上的版本几乎没有进行过完整的测试**，过往活动的存档见以下分支：

- [archive/pnku3-part1](https://github.com/PKUPC/pnku-website/tree/archive/pnku3-part1)

## 相关文档

目前文档约等于没有，欢迎 Pull Request。

- [开发](docs/development.md)
- [部署](docs/deployment.md)

## License

本项目基于 MIT 开放源代码许可证开源，参见[这个文件](./LICENSE.md)

后端部分主要基于 [Guiding Star 的后端部分](https://github.com/PKU-GeekGame/gs-backend)
开发，原项目许可证见[这个文件](./backend/GS_LICENSE.md)。
