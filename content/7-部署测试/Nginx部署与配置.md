> 一句话：**Nginx 在前端部署里干三件事——静态文件服务（把 dist 发出去）、反向代理（把 /api 转给后端、跨域就地解决）、性能配置（gzip + 缓存策略）。**

## 一、安装与常用命令

```bash
# CentOS
yum install -y nginx
# Ubuntu
apt install -y nginx
# macOS
brew install nginx

nginx              # 启动
nginx -s reload    # 改完配置重载（不断连接，最常用）
nginx -s stop      # 停止
nginx -t           # 测试配置语法（reload 前先跑一次）
```

配置文件位置：

- Linux（yum/apt）：`/etc/nginx/nginx.conf`，站点配置放 `/etc/nginx/conf.d/*.conf`
- macOS（brew）：`/opt/homebrew/etc/nginx/nginx.conf`

## 二、配置文件结构

```nginx
http {                 # HTTP 服务都在这个块里
  server {             # 一个 server = 一个站点（域名/端口）
    listen 80;
    server_name example.com;

    location / {       # 一个 location = 一条路径规则
      root /var/www/dist;
    }
  }
}
```

> 记住三层结构 `http → server → location`，所有配置都是往这三层里塞指令。

## 三、前端部署模板（背下来）

```nginx
server {
  listen 80;
  server_name example.com;

  # 前端静态资源
  root /var/www/dist;
  index index.html;

  # gzip：文本压缩，传输体积直接降到 1/3 ~ 1/5
  gzip on;
  gzip_types text/css application/javascript application/json image/svg+xml;
  gzip_min_length 1k;

  # 带 hash 的静态资源：缓存一年（文件名变了 URL 就变了，放心长缓存）
  location /assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }

  # HTML 不缓存：保证用户每次拿到的都是最新入口，再去要新 hash 的资源
  location = /index.html {
    add_header Cache-Control "no-cache";
  }

  # SPA history 路由兜底：/xxx 服务器上没有这个文件，统统回 index.html
  location / {
    try_files $uri $uri/ /index.html;
  }

  # 反向代理后端接口：前端同源请求 /api，Nginx 转发给后端服务
  location /api/ {
    proxy_pass http://127.0.0.1:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```

四个必懂的点：

### 1. `try_files $uri $uri/ /index.html;`

SPA（history 路由）部署的**命门**：刷新 `/home` 时服务器上没有 `/home` 这个文件，最后兜底返回 `index.html`，交给前端路由接管。没有这行 → 刷新 404。原理见 [[3-1 SPA原理与前端路由]]。

### 2. `root` vs `alias`

```nginx
# root：拼接。最终路径 = root + location
location /static/ { root /var/www; }   # 请求 /static/a.js → /var/www/static/a.js

# alias：替换。最终路径 = alias
location /static/ { alias /var/www/dist/; }  # 请求 /static/a.js → /var/www/dist/a.js
```

> alias 的路径要以 `/` 结尾；用错最典型的症状是 404。

### 3. 缓存策略：index.html 不缓存 + hash 资源长缓存

打包产物文件名自带 hash（`app.a3f9c2.js`），内容变 hash 就变 → 静态资源可以"永久"缓存；但入口 `index.html` 必须每次校验，否则用户锁死在旧入口上。产物结构见 [[打包后的web内容]]。

### 4. `proxy_pass` 带不带斜杠

```nginx
location /api/ {
  proxy_pass http://127.0.0.1:3000/;   # 带 / → /api/user → /user（替换 /api/）
  proxy_pass http://127.0.0.1:3000;    # 不带 / → /api/user → /api/user（原样拼接）
}
```

> 带不带斜杠结果不同，后端路由前缀要对得上，这是反向代理最常见的 404 来源。

## 四、跨域：代理 vs CORS 响应头

前后端分离时，浏览器端同源请求 `/api/...`（同源，无跨域），Nginx 在服务器侧转发给后端——**跨域根本不发生**，这是生产环境的标准做法。

如果前端直连后端域名，则用 CORS 头放行：

```nginx
location /api/ {
  if ($http_origin ~* "^https://example\.com$") {
    add_header Access-Control-Allow-Origin $http_origin;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
    add_header Access-Control-Allow-Headers "Content-Type, Authorization";
  }
  if ($request_method = OPTIONS) { return 204; }   # 预检请求直接放行
  proxy_pass http://127.0.0.1:3000;
}
```

## 五、WebSocket 代理（对话流式接口必备）

LLM Agent 的 SSE/WebSocket 流式接口，代理时必须显式升级协议，否则连不上/流被缓冲：

```nginx
location /ws/ {
  proxy_pass http://127.0.0.1:3000;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;      # 协议升级头
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 3600s;                    # 长连接，默认 60s 会掐断
  proxy_buffering off;                         # SSE 流式响应关闭缓冲，边产边发
}
```

## 六、常用排错

| 症状 | 排查 |
| ---- | ---- |
| 改了配置没生效 | 忘了 `nginx -s reload`；或改错文件（被 conf.d 覆盖） |
| 403 Forbidden | `root` 目录权限不足（nginx 运行用户读不了）；或目录下没有 index 指定的文件 |
| 刷新 404 | 没配 `try_files ... /index.html` |
| 接口 404/502 | `proxy_pass` 斜杠问题 / 后端服务没起（502 = 转发目标不可达） |
| 资源没压缩 | 响应头看 `Content-Encoding: gzip`；类型没加进 `gzip_types`（默认只压 text/html） |
| SSE 不吐字 | 忘了 `proxy_buffering off`，Nginx 把流攒够 buffer 才发 |

## 七、关联笔记

- 打包产物长啥样 → [[打包后的web内容]]
- SPA 为什么需要 try_files → [[3-1 SPA原理与前端路由]]
- 用容器跑前端（镜像里就是这段 Nginx） → [[前端项目打docker镜像]]
