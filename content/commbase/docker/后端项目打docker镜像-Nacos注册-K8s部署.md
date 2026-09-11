## 后端项目（Node.js）→ Docker 镜像 → Nacos 注册发现 → 网关 → K8s 部署 完整指南

> **前置条件**：K8s 集群中已有 Nacos 服务和网关服务，Node 服务本身不集成 Nacos SDK，通过 Nacos Open API 外部注册。

---

## 一、创建 Node.js 后端项目（纯 Express，无需 Nacos SDK）

### 1.1 项目初始化

```bash
mkdir node-backend-demo && cd node-backend-demo
npm init -y
npm install express
```

### 1.2 项目结构

```
node-backend-demo/
├─ app.js                  # 主入口，纯 Express 服务
├─ package.json
├─ Dockerfile
├─ .dockerignore
└─ k8s/
   ├─ namespace.yaml       # 命名空间
   ├─ secret.yaml          # Harbor 拉取凭证（或命令行创建）
   ├─ deployment.yaml      # Deployment 部署
   ├─ service.yaml         # Service 内部服务
   └─ register-nacos.sh    # 部署后向 Nacos 注册的脚本
```

### 1.3 app.js —— 纯 Express 服务

```js
const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;
const SERVICE_NAME = process.env.SERVICE_NAME || 'node-backend-demo';

app.get('/health', (req, res) => {
  res.json({ status: 'UP', service: SERVICE_NAME, timestamp: Date.now() });
});

app.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from Node.js Backend!', service: SERVICE_NAME });
});

app.get('/api/info', (req, res) => {
  res.json({ service: SERVICE_NAME, version: '1.0.0' });
});

app.listen(PORT, () => {
  console.log(`[Express] 服务启动: http://0.0.0.0:${PORT}`);
});
```

### 1.4 本地验证

```bash
node app.js

curl http://localhost:3000/api/hello
curl http://localhost:3000/health
```

---

## 二、Docker 镜像构建

### 2.1 Dockerfile（多阶段构建，推荐生产）

```dockerfile
# ---- 阶段1: 构建 ----
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --production
COPY . .

# ---- 阶段2: 运行 ----
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/app.js ./
COPY --from=builder /app/package.json ./

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

CMD ["node", "app.js"]
```

### 2.2 .dockerignore

```
node_modules
.git
.vscode
*.md
k8s/
.env*
```

### 2.3 构建镜像

```bash
docker build -t node-backend-demo:v1 .
```

### 2.4 本地运行测试

```bash
docker run -d -p 30:3000 --name node-backend-demo node-backend-demo:v1

curl http://localhost:30/health
curl http://localhost:30/api/hello
```

---

## 三、推送镜像到私有仓库（Harbor）

### 3.1 打标签

```bash
docker tag node-backend-demo:v1 shturl.cc/lSR6/agent/node-backend-demo:v1
```

### 3.2 登录 & 推送

```bash
docker login shturl.cc/lSR6
docker push shturl.cc/lSR6/agent/node-backend-demo:v1
```

> Harbor 项目名 `agent` 需提前在 Harbor 网页创建。
> 非 HTTPS 需配置 `/etc/docker/daemon.json` 中 `insecure-registries`，参考前端文档。



## 3.3 各部分含义

| 片段                                          | 说明                                                                                                                                                      |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docker tag`                                | 给本地镜像**打一个新标签（别名）**，**不会复制镜像文件，只是新增一个引用指针**，磁盘不会变大。                                                                                                     |
| `node-backend-demo:v1`                      | **本地已有镜像**：镜像名 `node-backend-demo`，版本 tag `v1`                                                                                                          |
| `shturl.cc/lSR6/agent/node-backend-demo:v1` | **目标镜像完整仓库地址**<br><br>- `shturl.cc`：私有镜像仓库域名（类似 docker.io）<br><br>- `lSR6/agent`：仓库下的命名空间 / 项目分组<br><br>- `node-backend-demo`：镜像名称<br><br>- `v1`：镜像版本标签 |

---

## 四、编写 K8s 部署文件（先创建 yaml，再部署）

> **重要**：镜像推送完成后，先编写好 K8s 的 Deployment 和 Service yaml 文件，再执行 kubectl apply 部署。

### 4.1 namespace.yaml —— 命名空间

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: agent-system
```

```bash
kubectl apply -f k8s/namespace.yaml
```

### 4.2 Secret —— Harbor 镜像拉取凭证

```bash
kubectl create secret docker-registry harbor-secret \
  --docker-server=shturl.cc/lSR6 \
  --docker-username=your-username \
  --docker-password=your-password \
  -n agent-system
```

> 也可以写成 yaml 文件，但密码会明文暴露，推荐用命令行创建。

### 4.3 deployment.yaml —— 部署 Pod

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-backend-demo
  namespace: agent-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: node-backend-demo           
  template:
    metadata:
      labels:
        app: node-backend-demo         # 必须， 运行后会自动成成pod, pod会有相同的label.内部的service会根据selector 和  pod的label匹配来匹配pod
    spec:
      imagePullSecrets:
      - name: harbor-secret
      containers:
      - name: node-backend-demo
        image: shturl.cc/lSR6/agent/node-backend-demo:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3000
        env:
        - name: PORT
          value: "3000"
        - name: SERVICE_NAME
          value: "node-backend-demo"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
      terminationGracePeriodSeconds: 15
```

**关键字段说明**：

| 字段 | 说明 |
|------|------|
| `imagePullSecrets` | 拉取私有 Harbor 镜像的凭证 |
| `image` | Harbor 上的镜像地址，与推送路径一致 |
| `imagePullPolicy: IfNotPresent` | 本地有则不拉取，无则从 Harbor 拉取 |
| `livenessProbe` | 存活探针，失败则重启容器 |
| `readinessProbe` | 就绪探针，失败则从 Service 摘除 |
| `terminationGracePeriodSeconds` | 优雅终止等待时间 |

### 4.4 service.yaml —— 内部服务发现

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: node-backend-svc
  namespace: agent-system
spec:
  selector:
    app: node-backend-demo   # 必须
  ports:
  - port: 80   # 内部服务对集群内的端口
    targetPort: 3000  # 自定义服务对外的端口
  type: ClusterIP
```

**Service 的作用**：

| 作用 | 说明 |
|------|------|
| **稳定访问入口** | 提供 `node-backend-svc.agent-system.svc.cluster.local:3000` 固定 DNS，Pod 重建不变 |
| **负载均衡** | 自动将请求分发到所有健康 Pod（replicas: 2） |
| **服务发现** | K8s 集群内其他服务（网关、Nacos 注册脚本）通过此 DNS 访问 |

> **为什么需要 Service**：Pod IP 是临时的，每次重建都会变化。Service 提供稳定的 ClusterIP 和 DNS 名称，是 Nacos 注册和网关路由的基础。

### 4.5 部署到 K8s

```bash
# 按顺序执行
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 4.6 验证部署

```bash
# 查看 Pod 状态（等待 Running + Ready 2/2）
kubectl get pods -n agent-system

# 查看 Service
kubectl get svc -n agent-system

# 查看 Pod 日志
kubectl logs -f deployment/node-backend-demo -n agent-system

# 集群内部访问测试
kubectl run curl-test --rm -it --image=curlimages/curl -- sh
curl http://node-backend-svc.agent-system.svc.cluster.local:3000/health
curl http://node-backend-svc.agent-system.svc.cluster.local:3000/api/hello
```

---

## 五、通过 Nacos Web 控制台让网关发现并转发 Node 服务

> **前提**：Node 服务已在 K8s 集群中运行，Service IP 为 `10.99.237.219`，端口为 `80`。集群中已有 Nacos 和网关服务。
>
> **目标**：通过 Nacos Web 控制台操作（不用命令行），让网关能发现 Node 服务并将请求转发过去。

### 5.1 整体流程

```
Nacos Web 控制台操作（2 步）
       │
       ├─→ 第一步：服务管理 → 注册 Node 服务实例
       │
       └─→ 第二步：配置管理 → 添加网关路由配置
                    │
                    ▼
            网关自动发现 → 转发请求到 Node 服务
```

**Nacos 控制台有两个关键功能**：

| 功能 | 作用 | 本场景用途 |
|------|------|-----------|
| **服务管理** | 注册服务实例（IP:Port） | 告诉 Nacos：「有一个叫 node-backend-demo 的服务，地址是 10.99.237.219:80」 |
| **配置管理** | 存储配置文件 | 告诉网关：「把 /api/** 的请求转发到 node-backend-demo 这个服务」 |

两步缺一不可：**注册服务**是让 Nacos 知道服务在哪里，**添加配置**是让网关知道怎么路由。

---

### 5.2 第一步：打开 Nacos 控制台

#### 如何确定控制台地址

Nacos 控制台地址取决于它在 K8s 中的暴露方式：

```bash
kubectl get svc -n agent-system | grep nacos
```

| Service 类型 | 控制台地址 | 说明 |
|-------------|-----------|------|
| **NodePort** | `http://<节点IP>:<NodePort>/nacos` | 输出中 8848 后面的端口就是 NodePort |
| **ClusterIP** | 需端口转发后访问 `http://localhost:8848/nacos` | 执行 `kubectl port-forward svc/nacos-server 8848:8848 -n agent-system` |
| **LoadBalancer** | `http://<EXTERNAL-IP>:8848/nacos` | 使用输出中的 EXTERNAL-IP |
| **Ingress** | `http://<域名>/nacos` | 执行 `kubectl get ingress -n agent-system` 查看域名 |

#### 登录

浏览器访问获取到的地址，默认账号密码：`nacos / nacos`

---

### 5.3 第二步：服务管理 — 添加实例（告诉 Nacos 服务在哪里）

> **操作位置**：左侧菜单 → **服务管理** → **服务列表**

**① 注册实例**

由于 Nacos 控制台点「创建服务」可能报 already exists，直接用 curl 注册实例（注册时服务会自动创建）：

```bash
curl -X POST "http://<nacos地址>:8848/nacos/v1/ns/instance" \
  -d "serviceName=node-backend-demo" \
  -d "groupName=DEFAULT_GROUP" \
  -d "namespaceId=public" \
  -d "ip=10.99.237.219" \
  -d "port=80" \
  -d "weight=1" \
  -d "healthy=true" \
  -d "enable=true" \
  -d "ephemeral=false"
```

**参数说明**：

| 参数 | 值 | 说明 |
|------|---|------|
| `serviceName` | `node-backend-demo` | 服务名，网关路由配置中要用这个名称 |
| `groupName` | `DEFAULT_GROUP` | 分组，必须与网关一致 |
| `namespaceId` | `public` | 命名空间，必须与网关一致 |
| `ip` | `10.99.237.219` | Node 服务的 K8s Service ClusterIP |
| `port` | `80` | Node 服务端口 |
| `ephemeral` | `false` | **必须为 false（持久实例）**，Node 无 Nacos SDK 不会发心跳，选临时实例会被剔除 |

**② 验证**

回到 Nacos 控制台 → **服务管理** → **服务列表** → 命名空间切换到 `public`，应能看到 `node-backend-demo`，实例 `10.99.237.219:80` 状态为「健康」。

---

### 5.4 第三步：配置管理 — 添加网关路由配置（告诉网关怎么转发）

> **操作位置**：左侧菜单 → **配置管理** → **配置列表**
>
> 这一步和上一步是**不同功能**：
> - 上一步「添加实例」→ Nacos 知道服务在哪里
> - 这一步「添加配置」→ 网关知道怎么路由

**① 找到网关已有的配置**

1. 左侧菜单 → **配置管理** → **配置列表**
2. 命名空间选择与网关一致的命名空间（`public`）
3. 在列表中找到网关的配置文件

> **如何确定网关的配置 Data ID？**
>
> 联系集群管理员确认，或查看网关已有的配置。Spring Cloud Gateway 的 Data ID 通常是 `${spring.application.name}.${file-extension}`，如 `gateway-server.yaml`。

**② 编辑配置，追加路由规则**

找到网关配置后，点击「**编辑**」，在路由规则中追加 Node 服务的路由。

**如果网关配置中已有 routes 列表**，在 `routes` 下追加一条：

```yaml
        - id: node-backend-route
          uri: lb://node-backend-demo
          predicates:
            - Path=/api/**
          filters:
            - StripPrefix=0
```

**如果网关配置是全新的**，完整配置内容如下：

```yaml
spring:
  cloud:
    gateway:
      discovery:
        locator:
          enabled: true
          lower-case-service-id: true
      routes:
        - id: node-backend-route
          uri: lb://node-backend-demo
          predicates:
            - Path=/api/**
          filters:
            - StripPrefix=0
```

**路由字段说明**：

| 字段 | 值 | 说明 |
|------|---|------|
| `id` | `node-backend-route` | 路由唯一标识，自定义命名 |
| `uri` | `lb://node-backend-demo` | **关键**：`lb://` 表示从 Nacos 服务发现负载均衡，`node-backend-demo` 是第二步注册的服务名，必须完全一致 |
| `predicates` | `Path=/api/**` | 匹配所有 `/api/` 开头的请求转发到此服务 |
| `filters` | `StripPrefix=0` | 不剥离路径前缀，原样转发 |

> **请求链路**：客户端请求 `/api/hello` → 网关匹配路由 → 从 Nacos 查找 `node-backend-demo` 的实例 → 转发到 `10.99.237.219:80/api/hello`

**③ 点击「发布」**

网关会自动读取新配置，无需重启。发布后路由立即生效。

---

### 5.5 验证完整链路

```bash
# 集群内部测试，通过网关访问 Node 服务
# 替换 <gateway-address> 为网关的 Service IP 或域名
curl http://<gateway-address>/api/hello

# 期望返回
{"message":"Hello from Node.js Backend!","service":"node-backend-demo"}
```

**验证清单**：

```
✅ 1. Nacos 服务列表中有 node-backend-demo（命名空间: public）
✅ 2. 实例 10.99.237.219:80 状态为「健康」
✅ 3. Nacos 配置列表中有网关路由配置
✅ 4. 路由 uri = lb://node-backend-demo（与服务名一致）
✅ 5. 路由 predicates 匹配 /api/** 路径
✅ 6. 命名空间 / Group 与网关一致
✅ 7. curl 网关地址 /api/hello 返回 Node 服务响应
```

---

### 5.6 常见问题排查

#### 创建服务报错 "already exists" 但服务列表看不到

**原因**：服务已被自动创建（注册实例时自动创建），但控制台命名空间未切换到 `public`。

**解决**：
1. 服务列表顶部命名空间下拉框切换到 `public`
2. 如果仍看不到，说明实例还没注册成功，用 5.3 的 curl 命令注册实例即可
3. 不要点「创建服务」按钮

#### 网关转发 404 或 503

**排查**：

| 现象 | 可能原因 | 检查方法 |
|------|---------|---------|
| 404 | 路由未匹配 | 确认 predicates 路径是否正确，如 `/api/**` |
| 503 | Nacos 中无健康实例 | 确认服务列表中实例状态为「健康」 |
| 503 | 网关配置未生效 | 确认配置已发布，Data ID / Group 与网关一致 |

#### 实例状态为「不健康」

Nacos 对持久实例做 TCP 健康探测。确认网关所在节点能访问 `10.99.237.219:80`：

```bash
# 在 K8s 集群内测试
kubectl run curl-test --rm -it --image=curlimages/curl -- sh
curl http://10.99.237.219:80/health
```

#### 命名空间 / Group 不一致导致网关发现不了服务

**必须三端一致**：

| 配置项 | 服务注册侧 | 网关配置侧 | 网关应用侧 |
|--------|-----------|-----------|-----------|
| 命名空间 | `public` | 配置的 namespace | spring.cloud.nacos.discovery.namespace |
| Group | `DEFAULT_GROUP` | 配置的 group | spring.cloud.nacos.discovery.group |
| 服务名 | `node-backend-demo` | `lb://node-backend-demo` | — |

---

### 5.7 下线服务时如何注销

**注销实例**（在 Nacos 控制台）：

服务列表 → 点击 `node-backend-demo` → 实例列表 → 点击实例右侧「**下线**」或「**删除**」按钮。

**删除路由配置**（在 Nacos 控制台）：

配置列表 → 找到网关配置 → 点击「编辑」→ 删除 Node 服务的路由条目 → 点击「发布」。

---

### 5.8 操作全流程对照图

```
┌──────────────────────────────────────────────────────────┐
│                    Nacos Web 控制台                        │
│                                                          │
│  【第一步】服务管理 → 注册实例                              │
│  ┌──────────────────────────────────────────────┐        │
│  │  命名空间: [public ▼]  ← 与网关一致           │        │
│  │                                              │        │
│  │  通过 curl 注册实例（不要点"创建服务"）：        │        │
│  │  serviceName:  node-backend-demo             │        │
│  │  ip:           10.99.237.219                 │        │
│  │  port:         80                            │        │
│  │  ephemeral:    false（持久实例）               │        │
│  │                                              │        │
│  │  → 注册后服务列表可见，实例状态为「健康」         │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  【第二步】配置管理 → 添加网关路由                          │
│  ┌──────────────────────────────────────────────┐        │
│  │  命名空间: [public ▼]  ← 与网关一致           │        │
│  │                                              │        │
│  │  找到网关配置 → 编辑 → 追加路由：              │        │
│  │                                              │        │
│  │  - id: node-backend-route                   │        │
│  │    uri: lb://node-backend-demo    ← 服务名    │        │
│  │    predicates:                              │        │
│  │      - Path=/api/**              ← 匹配路径  │        │
│  │                                              │        │
│  │  → 点击「发布」，网关自动生效                   │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  【验证】curl 网关地址/api/hello → 返回 Node 服务响应      │
└──────────────────────────────────────────────────────────┘
```

---

## 七、完整流程总结

```
1. 开发 Node.js 纯 Express 服务（无 Nacos 依赖）
       ↓
2. 编写 Dockerfile + .dockerignore
       ↓
3. docker build 构建镜像
       ↓
4. docker tag + push 推送到 Harbor
       ↓
5. 编写 K8s 资源清单（namespace → deployment → service）
       ↓
6. kubectl apply 依次部署到 K8s
       ↓
7. 确认 Pod Running + Service 就绪（记录 Service IP: 10.99.237.219:80）
       ↓
8. Nacos 控制台：注册服务实例（10.99.237.219:80）
       ↓
9. Nacos 控制台：添加网关路由配置（lb://node-backend-demo）
       ↓
10. 验证：curl 网关地址/api/hello → 返回 Node 服务响应
```

---

## 八、常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| Pod ImagePullBackOff | Harbor 凭证未配置或镜像路径错误 | 检查 Secret 和 image 字段 |
| Pod CrashLoopBackOff | 应用启动失败 | `kubectl logs` 查看日志，检查端口/代码 |
| 创建服务报 already exists | 服务已自动创建 | 不要点"创建服务"，直接注册实例 |
| 服务列表看不到服务 | 命名空间未切换 | 切换到 public 命名空间 |
| 网关 404 | 路由未匹配 | 确认 predicates 路径正确 |
| 网关 503 | Nacos 中无健康实例 | 确认实例状态为「健康」，namespace/group 一致 |
| 实例状态不健康 | Nacos TCP 探测不可达 | 确认 10.99.237.219:80 从集群内可达 |
| 注册 ephemeral=true 实例掉线 | 无心跳保活，Nacos 自动剔除 | 必须使用 ephemeral=false（持久实例） |
| 容器内存溢出 | Node.js 默认堆内存限制 | 设置 `--max-old-space-size=256` 或调大 limits |
