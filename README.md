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
2. 将 `frontend/src` 中的 `setup.example.ts` 复制一份，命名为 `setup.ts`，并根据自己的需要调整。
3. 将 `backend/src` 中的 `custom.example.py` 和 `secret.example.py` 分别复制一份，命名为 `custom.py` 和 `secret.py`，并根据自己的需要调整。
4. 后端配置好 python 3.11 和 poetry，前端配置好 node 和 pnpm，安装好依赖后理论上就可以跑了。

## 部署

### 直接部署

可以参考基于 Docker 部署的相关配置。

### 使用 Docker 部署（待测试）

> 注意：该部署方案尚未在正式环境中使用过

#### 配置数据库

数据库部分并没有容器化，需要单独配置。

#### 私有仓库

由于还在准备中的活动往往不便于公开发布镜像，直接在生产服务器上构建镜像有时又不太方便，最好是使用私有仓库。可以考虑[自建仓库](https://hub.docker.com/_/registry)或者使用云服务（例如阿里云的[容器镜像服务](https://help.aliyun.com/zh/acr/)）。

#### 构建镜像

前端会在这个阶段直接构建，因此 `frontend/src/setup.ts` 需要在此时就准备好，同时需要注意前端构建时的环境变量配置。

```bash
docker build . -t registry.your.domain/namespace/pnku:latest
```

#### 推送镜像

```bash
docker push registry.your.domain/namespace/pnku:latest
```

#### 启动容器

`./data` 文件夹对应 `secret.py` 中的 `BASE_PATH`，存放数据文件。`secret.py` 中的 `BASE_PATH` 也应该相应的设置为 `/app/data`。

一个示例如下：

```bash
docker run -d \
    -p 8080:80 \
    -e TZ=Asia/Shanghai \
    -v ./data:/app/data \
    -v ./log:/app/log \
    -v ./secret.py:/app/backend/src/secret.py \
    -v ./custom.py:/app/backend/src/custom.py \
    --add-host=host.docker.internal:host-gateway \
    registry.your.domain/namespace/pnku:latest
```

这里用 `--add-host=host.docker.internal:host-gateway` 让容器可以在内部用 `host.docker.internal` 访问宿主机上的服务，例如数据库。需要注意的是，使用这种方式访问数据库并不是本地访问，而是通过网络访问，因此需要更改数据库的 `bind-address`（默认可能为`127.0.0.1`），数据库用户也需要设置合适的 `host`。一般直接设置 `bind-address = 0.0.0.0`，数据库用户为 `'username'@'%'` 即可（但是不建议直接在公网暴露数据库端口）。

当然，你也可以直接在容器里跑数据库，自行配置好 `docker` 中的网络环境即可。


#### 反向代理

容器中启动了一个 nginx，并且配置好了负载均衡和缓存，可以在外部再使用你喜欢的工具做一个反向代理，配置 https、http2 等功能。

## License

本项目基于 MIT 开放源代码许可证开源，参见[这个文件](./LICENSE.md)

后端部分主要基于 [Guiding Star 的后端部分](https://github.com/PKU-GeekGame/gs-backend)
开发，原项目许可证见[这个文件](./backend/GS_LICENSE.md)。

