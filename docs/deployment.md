# 部署

## 直接部署

可以先参考基于 Docker 部署的相关配置。

## 使用 Docker 部署（待测试）

> 注意：该部署方案尚未在正式环境中使用过

### 配置数据库

数据库部分并没有容器化，需要单独配置。

### 私有仓库

由于还在准备中的活动往往不便于公开发布镜像，直接在生产服务器上构建镜像有时又不太方便，最好是使用私有仓库。可以考虑[自建仓库](https://hub.docker.com/_/registry)或者使用云服务（例如阿里云的[容器镜像服务](https://help.aliyun.com/zh/acr/)）。

### 构建镜像

前端会在这个阶段直接构建，因此 `frontend/src/setup.ts` 需要在此时就准备好，同时需要注意前端构建时的环境变量配置。

```bash
docker build . -t registry.your.domain/namespace/pnku:latest
```

### 推送镜像

```bash
docker push registry.your.domain/namespace/pnku:latest
```

### 启动容器

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

### 反向代理

容器中启动了一个 nginx，并且配置好了负载均衡和缓存，可以在外部再使用你喜欢的工具做一个反向代理，配置 https、http2 等功能。
