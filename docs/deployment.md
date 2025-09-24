# 部署

## 直接部署

可以先参考基于 Docker 部署的相关配置，重点关注 nginx 相关的配置。

## 使用 Docker 部署

> 注意：该部署方案尚未在正式环境中使用过，请自行测试

### 标准版

#### 配置数据库

自行选择你喜欢的配置方式，配置在宿主机上或者容器里，按需调整启动方式即可。

#### 私有镜像仓库

由于还在准备中的活动往往不便于公开发布镜像，直接在生产服务器上构建镜像可能有性能问题（这个问题加钱可以解决），因此可以考虑本地 build 好后上传到私有仓库。可以考虑[自建仓库](https://hub.docker.com/_/registry)或者使用云服务（例如阿里云的[容器镜像服务](https://help.aliyun.com/zh/acr/)）。

> 但是实测体验都不是非常稳定……

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
    -v ./secret.py:/app/secret.py \
    -v ./custom.py:/app/custom.py \
    --add-host=host.docker.internal:host-gateway \
    registry.your.domain/namespace/pnku:latest
```

这里用 `--add-host=host.docker.internal:host-gateway` 让容器可以在内部用 `host.docker.internal` 访问宿主机上的服务，例如数据库。需要注意的是，使用这种方式访问数据库并不是本地访问，而是通过网络访问，因此需要更改数据库的 `bind-address`（默认可能为`127.0.0.1`），数据库用户也需要设置合适的 `host`。一般直接设置 `bind-address = 0.0.0.0`，数据库用户为 `'username'@'%'` 即可（但是不建议直接在公网暴露数据库端口）。

当然，你也可以直接在容器里跑数据库，自行配置好 `docker` 中的网络环境即可。

#### 反向代理

容器中启动了一个 nginx，并且配置好了负载均衡和缓存，可以在外部再使用你喜欢的工具做一个反向代理，配置 https、http2 等功能。

### 青春版

如果服务器性能有限，难以直接在服务器上构建前端（最需要性能的部分），可以在其他地方构建好前端后传到项目路径下的 `frontend-build` 文件夹中（比如本地构建好 scp 传上去）。


项目中提供了一个 `Dockerfile.youth` 文件，会尝试从 `frontend-build` 路径获取构建好的前端文件，使用以下命令构建：

```bash
docker build . -t pnku:youth -f Dockerfile.youth
```

### 仅运行环境

`Dockerfile.runtime` 提供了一个仅包含运行环境（包括 nginx 配置和后端所需的依赖）的镜像版本，需要在启动的时候自己将构建好的前端文件和后端代码挂载进去，示例如下：

```bash
docker build . -t pnku:runtime -f Dockerfile.runtime

docker run -d \
    -p 8080:80 \
    -e TZ=Asia/Shanghai \
    -v /path/to/frontend-build:/app/frontend-build
    -v /path/to/backend:/app/backend
    -v ./data:/app/data \
    -v ./log:/app/log \
    -v ./secret.py:/app/secret.py \
    -v ./custom.py:/app/custom.py \
    --add-host=host.docker.internal:host-gateway \
    pnku:runtime
```

一般情况下，在没有修改后端依赖时，镜像构建好后就可以反复用，每次在服务器上更新了代码和构建好的前端后重启一次就好了。
