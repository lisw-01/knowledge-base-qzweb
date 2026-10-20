# Docker 常用指令

> 按使用场景分类整理，`容器名` / `镜像名` / `标签` / `端口` 为占位符，替换为实际值。

***

## 系统信息

| 命令 | 说明 |
|------|------|
| `docker version` | 查看 Docker 版本 |
| `docker info` | 查看 Docker 系统信息（存储驱动、镜像数、容器数等） |
| `docker system df` | 查看 Docker 磁盘占用（镜像/容器/卷） |
| `docker system prune` | 清理无用数据（停止的容器、悬空镜像、未用网络） |
| `docker system prune -a` | 清理所有未使用资源（包括未运行的镜像） |

***

## 镜像操作

### 查找与拉取

| 命令 | 说明 |
|------|------|
| `docker search 关键词` | 在 Docker Hub 搜索镜像 |
| `docker pull 镜像名:标签` | 拉取镜像（默认 latest） |
| `docker pull nginx:1.25-alpine` | 拉取指定版本 |

### 查看

| 命令 | 说明 |
|------|------|
| `docker images` | 列出本地所有镜像 |
| `docker images -a` | 包含中间层镜像 |
| `docker images -q` | 只显示镜像 ID |
| `docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}"` | 自定义格式输出 |
| `docker inspect 镜像名:标签` | 查看镜像详细信息（JSON） |
| `docker history 镜像名:标签` | 查看镜像构建历史（各层命令） |

### 构建

| 命令 | 说明 |
|------|------|
| `docker build -t 镜像名:标签 .` | 根据当前目录 Dockerfile 构建镜像 |
| `docker build -t 镜像名:标签 -f Dockerfile.prod .` | 指定 Dockerfile 文件 |
| `docker build --no-cache -t 镜像名:标签 .` | 不使用缓存构建 |
| `docker build --build-arg VERSION=1.0 -t 镜像名:标签 .` | 传入构建参数 |

### 打标签与推送

| 命令 | 说明 |
|------|------|
| `docker tag 镜像名:标签 仓库地址/项目名/镜像名:标签` | 给镜像打仓库标签 |
| `docker login 仓库地址` | 登录镜像仓库 |
| `docker logout 仓库地址` | 退出登录 |
| `docker push 仓库地址/项目名/镜像名:标签` | 推送镜像到仓库 |

### 导入导出

| 命令 | 说明 |
|------|------|
| `docker save -o file.tar 镜像名:标签` | 导出镜像为 tar 文件 |
| `docker save 镜像名:标签 \| gzip > file.tar.gz` | 导出并压缩 |
| `docker load -i file.tar` | 从 tar 文件导入镜像 |
| `docker load < file.tar.gz` | 从压缩文件导入 |

### 删除

| 命令 | 说明 |
|------|------|
| `docker rmi 镜像名:标签` | 删除镜像 |
| `docker rmi -f 镜像名:标签` | 强制删除 |
| `docker rmi $(docker images -q)` | 删除所有镜像 |
| `docker image prune` | 删除悬空镜像（无标签的） |
| `docker image prune -a` | 删除所有未使用的镜像 |

***

## 容器操作

### 创建与启动

| 命令 | 说明 |
|------|------|
| `docker run 镜像名:标签` | 创建并启动容器 |
| `docker run -d 镜像名:标签` | 后台运行（detached） |
| `docker run -d -p 8080:80 镜像名:标签` | 映射端口（宿主机:容器） |
| `docker run -d -p 127.0.0.1:8080:80 镜像名:标签` | 绑定指定 IP |
| `docker run -d --name myapp 镜像名:标签` | 指定容器名 |
| `docker run -d -e KEY=VALUE 镜像名:标签` | 设置环境变量 |
| `docker run -d -v /host/path:/container/path 镜像名:标签` | 挂载目录（数据卷） |
| `docker run -d -v 数据卷名:/container/path 镜像名:标签` | 使用命名数据卷 |
| `docker run -d --restart=always 镜像名:标签` | 设置重启策略 |
| `docker run -d --network 网络名 镜像名:标签` | 指定网络 |
| `docker run -d --add-host=host.docker.internal:host-gateway 镜像名:标签` | 添加 host 映射（Linux 访问宿主机） |
| `docker run -it 镜像名:标签 /bin/sh` | 交互式启动（进入容器） |
| `docker run --rm 镜像名:标签` | 容器退出后自动删除 |

**重启策略**：

| 策略 | 说明 |
|------|------|
| `--restart=no` | 不自动重启（默认） |
| `--restart=always` | 总是重启（包括 Docker 重启后） |
| `--restart=on-failure:5` | 非零退出时重启，最多 5 次 |
| `--restart=unless-stopped` | 除非手动停止，否则总是重启 |

### 查看

| 命令 | 说明 |
|------|------|
| `docker ps` | 查看运行中的容器 |
| `docker ps -a` | 查看所有容器（包括已停止） |
| `docker ps -q` | 只显示容器 ID |
| `docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"` | 自定义格式 |
| `docker inspect 容器名` | 查看容器详细信息（JSON） |
| `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 容器名` | 查看容器 IP |
| `docker stats` | 实时监控所有容器资源占用（CPU/内存/网络） |
| `docker stats 容器名` | 监控指定容器 |
| `docker top 容器名` | 查看容器内进程 |
| `docker diff 容器名` | 查看容器文件系统变更 |

### 启停与重启

| 命令 | 说明 |
|------|------|
| `docker start 容器名` | 启动已停止的容器 |
| `docker stop 容器名` | 优雅停止容器（发 SIGTERM，10 秒后 SIGKILL） |
| `docker stop -t 30 容器名` | 指定超时时间（秒） |
| `docker restart 容器名` | 重启容器 |
| `docker kill 容器名` | 强制终止容器（SIGKILL） |
| `docker pause 容器名` | 暂停容器（冻结进程） |
| `docker unpause 容器名` | 恢复暂停 |

### 日志与调试

| 命令 | 说明 |
|------|------|
| `docker logs 容器名` | 查看容器日志 |
| `docker logs -f 容器名` | 实时跟踪日志 |
| `docker logs --tail 100 容器名` | 查看最后 100 行 |
| `docker logs -f --tail 50 容器名` | 实时跟踪最后 50 行起 |
| `docker logs --since 30m 容器名` | 查看最近 30 分钟的日志 |
| `docker logs 容器名 2>&1 \| grep "error"` | 过滤错误日志 |

### 进入容器

| 命令 | 说明 |
|------|------|
| `docker exec -it 容器名 /bin/sh` | 进入运行中的容器（推荐） |
| `docker exec -it 容器名 /bin/bash` | 进入容器（有 bash 时） |
| `docker exec 容器名 命令` | 在容器中执行命令（不进入） |
| `docker exec 容器名 cat /etc/hosts` | 示例：查看容器 hosts |

### 文件拷贝

| 命令 | 说明 |
|------|------|
| `docker cp 容器名:/容器路径 /宿主机路径` | 从容器拷贝到宿主机 |
| `docker cp /宿主机路径 容器名:/容器路径` | 从宿主机拷贝到容器 |

### 删除

| 命令 | 说明 |
|------|------|
| `docker rm 容器名` | 删除已停止的容器 |
| `docker rm -f 容器名` | 强制删除运行中的容器 |
| `docker rm $(docker ps -aq)` | 删除所有容器 |
| `docker container prune` | 删除所有已停止的容器 |

***

## 数据卷

| 命令 | 说明 |
|------|------|
| `docker volume create 数据卷名` | 创建数据卷 |
| `docker volume ls` | 列出所有数据卷 |
| `docker volume inspect 数据卷名` | 查看数据卷详情 |
| `docker volume rm 数据卷名` | 删除数据卷 |
| `docker volume prune` | 删除未使用的数据卷 |

***

## 网络

| 命令 | 说明 |
|------|------|
| `docker network ls` | 列出所有网络 |
| `docker network create 网络名` | 创建自定义网络 |
| `docker network create --driver bridge 网络名` | 指定驱动创建 |
| `docker network inspect 网络名` | 查看网络详情 |
| `docker network connect 网络名 容器名` | 将容器加入网络 |
| `docker network disconnect 网络名 容器名` | 将容器移出网络 |
| `docker network rm 网络名` | 删除网络 |
| `docker network prune` | 删除未使用的网络 |

**默认网络类型**：

| 类型 | 说明 |
|------|------|
| `bridge` | 默认，容器间通过虚拟网桥通信 |
| `host` | 容器与宿主机共享网络，无端口映射 |
| `none` | 无网络 |
| `overlay` | 跨主机通信（Swarm） |

***

## Docker Compose

| 命令 | 说明 |
|------|------|
| `docker compose up -d` | 后台启动所有服务 |
| `docker compose up -d --build` | 重新构建镜像后启动 |
| `docker compose down` | 停止并删除容器、网络 |
| `docker compose down -v` | 同时删除数据卷 |
| `docker compose ps` | 查看服务状态 |
| `docker compose logs -f 服务名` | 查看服务日志 |
| `docker compose exec 服务名 /bin/sh` | 进入服务容器 |
| `docker compose restart 服务名` | 重启服务 |
| `docker compose build` | 构建或重建服务镜像 |
| `docker compose pull` | 拉取服务镜像 |
| `docker compose config` | 验证并查看合并后的配置 |

***

## 常用组合场景

### 镜像构建 → 推送全流程

```bash
docker build -t myapp:v1 .
docker tag myapp:v1 registry.example.com/project/myapp:v1
docker login registry.example.com
docker push registry.example.com/project/myapp:v1
```

### 容器调试

```bash
docker ps -a                          # 找到容器
docker logs -f --tail 100 容器名       # 看日志
docker exec -it 容器名 /bin/sh         # 进入容器
docker inspect 容器名                  # 查详细信息
```

### 清理空间

```bash
docker system df                       # 查看占用
docker system prune -a                 # 一键清理
docker volume prune                    # 清理无用卷
docker builder prune                   # 清理构建缓存
```

### 查看容器 IP

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 容器名
```

### 批量停止/删除

```bash
docker stop $(docker ps -q)            # 停止所有运行中容器
docker rm $(docker ps -aq)             # 删除所有容器
docker rmi $(docker images -q)         # 删除所有镜像
```
