## 1） 前端 Docker 单阶段构建完整步骤
> 适用场景：**本地电脑先执行打包，生成 dist，再把 dist 打进 nginx 镜像**。
> 
> 特点：Docker 内部不执行 npm install /npm run build，build 在本机完成。
> 
> 适合本地调试；CI 流水线不推荐（优先多阶段构建【推荐生产】）。

## 前提

你的前端项目（Vue/Vite/React）本地环境正常，能 npm run build。

### 步骤 1：本地执行打包

进入前端项目根目录

bash

```
# 安装依赖（首次）
npm install

# 执行打包，输出 dist 文件夹
npm run build
```

执行完毕，项目根目录会出现 `dist` 文件夹，里面是 index.html、js、css 静态资源。

> ✅ 确认：dist/index.html 文件存在，这是关键。

### 步骤 2：在项目根目录新建 3 个文件

#### ① Dockerfile（文件名就叫 Dockerfile，无后缀）

dockerfile

```
# 基础镜像，轻量nginx
FROM nginx:alpine

# 删除nginx默认网页
RUN rm -rf /usr/share/nginx/html/*

# 将本机的dist目录复制到nginx静态目录
COPY ./dist /usr/share/nginx/html

# 复制自定义nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# nginx前台运行
CMD ["nginx", "-g", "daemon off;"]
```

#### ② nginx.conf 同目录新建

> 解决 history 路由刷新 404 问题

nginx

```
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

#### ③ .dockerignore（可选，建议加上）

dockerignore

```
node_modules
.git
.vscode
*.md
.env*
```

> 目录结构：

plaintext

```
你的前端项目/
├─ dist/              # 本地npm run build生成
├─ src/
├─ package.json
├─ Dockerfile         # 新建
├─ nginx.conf         # 新建
└─ .dockerignore      # 新建
```

### 步骤 3：构建 docker 镜像

**当前工作目录必须在 Dockerfile 所在的项目根目录**

bash

```
docker build -t agent-webui:v1 .
```

- `-t agent-webui:v1`：镜像名字：版本号
- 末尾的 `.` 代表当前目录，不要漏掉！

构建成功提示：`Successfully built ...`

### 步骤 4：本地运行镜像测试

bash

```
docker run -d -p 8080:80 --name agent-webui-demo agent-webui:v1
```

- `-d`：后台运行
- `-p 8080:80`：宿主机 8080 端口映射容器 80 端口

浏览器访问：`http://127.0.0.1:8080`，页面打开正常即为成功。

查看容器日志：

bash

```
docker logs -f agent-webui-demo
```

### 步骤 5：停止、清理

bash

```
# 停止容器
docker stop agent-webui-demo
# 删除容器
docker rm agent-webui-demo
# 删除镜像（需要）
docker rmi agent-webui:v1
```



## 2）  推镜像仓库 + K8s 部署完整流程

> 承接上一步：已经本地构建好镜像 `agent-webui:v1`
> 
> 整体流程：**本地打镜像 → 打仓库标签 → push 镜像仓库 → 编写 k8s yaml → apply 部署 → 访问验证**

> 镜像仓库：一般使用 Harbor（企业私有镜像仓库），也可以 DockerHub。下面以私有 Harbor 举例。

## 一、推送镜像到私有镜像仓库

### 1. 镜像打标签（关键）

格式：`镜像仓库地址/项目名/镜像名:版本`

bash

```
#示例harbor地址 shturl.cc/lSR6，项目名：agent
docker tag agent-webui:v1 shturl.cc/lSR6/agent/agent-webui:v1
```

> 说明：
> 
> - `shturl.cc/lSR6`：你的 harbor 域名
> - `agent`：harbor 里面的项目名称，要提前在 harbor 网页建好
> - `agent-webui:v1`：镜像名称版本

### 2. 登录镜像仓库

bash

```
docker login shturl.cc/lSR6
```

输入 harbor 用户名、密码。

> ⚠️ 如果 harbor 是 http 非 https，docker 需要配置 insecure-registries，否则登录失败。
> 
> 编辑 `/etc/docker/daemon.json`

json

```
{
  "insecure-registries": ["shturl.cc/lSR6"]
}
```

修改后重启 docker：

bash

```
systemctl daemon-reload
systemctl restart docker
```

### 3. 推送镜像

bash

```
docker push shturl.cc/lSR6/agent/agent-webui:v1
```

推送完成后，去 harbor 网页查看，确认镜像已经存在。




## 3）  K8s 部署

K8s 标准最小资源：

1. **Deployment**：管理 Pod，运行容器，副本管理、滚动更新
2. **Service**：内部服务访问
3. **Ingress**：对外暴露 http 访问入口（替代 NodePort，生产推荐）

> 前端是静态 nginx 页面，不需要持久化存储。

新建文件 `agent-webui.yaml`

yaml

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-webui
  namespace: agent-system # 使用自己的命名空间，提前创建
spec:
  replicas: 2 # 副本数，可以多实例
  selector:
    matchLabels:
      app: agent-webui
  template:
    metadata:
      labels:
        app: agent-webui
    spec:
      containers:
      - name: agent-webui
        image: shturl.cc/lSR6/agent/agent-webui:v1 # 刚刚推送到仓库镜像地址
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80 #容器内部nginx端口
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 300m
            memory: 256Mi
---
# Service 内部服务
apiVersion: v1
kind: Service
metadata:
  name: agent-webui-svc
  namespace: agent-system
spec:
  selector:
    app: agent-webui
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP #集群内部访问，由Ingress对外
---
# Ingress 对外暴露访问地址
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-webui-ingress
  namespace: agent-system
  annotations:
    # nginx ingress控制器注解
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: shturl.cc/fLj49CQ8p # 访问域名，配置DNS解析到ingress controller
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agent-webui-svc
            port:
              number: 80
```