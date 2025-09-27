# P&KU Website

## 简介

P&KU Website（暂定）是为 P&KU 这一 Puzzle Hunt 活动开发的比赛平台，目前已经基于这一平台成功举办了以下活动：
- [P&KU2](https://pnku2.pkupuzzle.art/)
- [MiaoHunt 2023](https://mh2023.puzzlehunt.cn/)
- [P&KU3（上）](https://pnku3.pkupuzzle.art/)
- [Golden Puzzle Hunt](https://goldenph.art/)*

其中标 * 的活动是活动组织方自行基于本项目开发的。

本项目的核心架构设计源自 [Guiding Star](https://github.com/pku-GeekGame/guiding-star)，Guiding Star 是为了 PKU GeekGame 而开发的 CTF 比赛平台，提供了一种基于状态机的后端架构，方便实现各种奇怪需求，非常适合 Puzzle Hunt 这一场景（出题人总是有一些妙妙点子）。

由于开发者的时间和精力有限，目前开源的代码中还有很多历史遗留问题，没有完全整理好（每次办完活动后都说要整理下……然后就拖到了下次活动前，开始堆新的屎山orz）。

**注意：** 本项目并非是开箱即用的，还有很多需要完善的功能，并且实现思路可能和通常的服务端不一样，有一定的理解成本。建议在决定基于本项目开发前慎重考虑，如果有什么疑问或者建议，欢迎直接与我们交流。

## 开发状态

本项目的开发周期主要取决于项目维护者参与举办的活动周期（主要是 P&KU，有空的时候也会参与其他活动，例如 MiaoHunt、[数据删除] 等）。

在一个活动结束后，相关改动会合并到该仓库的主分支中，之后会以此为蓝本进行 bug 修复或者一些小功能更新，在未来也许会专门设计一套题来做这个事。

在下次活动之前，可能会进行一些重构和基建建设的工作，会有较多的改动，但是仍然基于上次活动开发。这一阶段的代码可能没有经过完整的测试和上线验证，在这些改动开始之前会将上次活动内容存档到 archive/ 下的分支。在建设到一定程度之后，会基于此时的版本进行封闭开发，期间大概率不会更新本仓库，直到下次活动结束。

目前本项目正在为下次活动做准备中，**当前主分支上的版本几乎没有进行过完整的测试**，过往活动的存档见以下分支：
- [archive/pnku3-part1](https://github.com/PKUPC/pnku-website/tree/archive/pnku3-part1)

## 相关文档

目前文档极为欠缺，欢迎 Pull Request。

- [开发](docs/development.md)
- [部署](docs/deployment.md)

## License

本项目基于 MIT 开放源代码许可证开源，参见[这个文件](./LICENSE.md)

后端部分主要基于 [Guiding Star 的后端部分](https://github.com/PKU-GeekGame/gs-backend)
开发，原项目许可证见[这个文件](./backend/GS_LICENSE.md)。

