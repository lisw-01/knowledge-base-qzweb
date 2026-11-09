---
title: 我的知识库
---

# 我的知识库


> 一句话：**Obsidian 写笔记 → Quartz 本地构建成静态站 → 一条命令直传到自己的云服务器，公网可访问。**

```
Obsidian（本地写作，本仓库就是知识库）
        │
        ▼
双击 deploy.bat / git deploy
   │  同步笔记 → Quartz 构建 → 隐私自检 → tar over SSH → 备份+原子切换 → HTTP 自检
   ▼
http://8.140.217.146/   （自有云服务器上的 Nginx 静态目录）
```

| 环节 | 工具 | 干什么 |
| ---- | ---- | ---- |
| ① 写 | Obsidian | 编辑 Markdown 笔记，wikilink 互链 |
| ② 建 | Quartz v5（Node ≥ 22） | 把知识库渲染成静态站点 `public/` |
| ③ 发 | `deploy.bat` / `git deploy` | 一次直传到自己的服务器，链接不变 |

发布过程完全可见：服务器上就是一个普通 HTML 目录，能 `ls`、能 `nginx -t`、能回滚；没有构建服务、没有 CI、没有黑盒平台。

> 📌 **三～六节是历史方案资料（GitHub Pages 与其他托管平台），已停用，原文保留备查；当前实际发布链路见「七、发布端：自有云服务器」。** 这些章节里的操作命令与「见第七节」等交叉引用按当时状态记录，不再适用，一律以第七节为准。知识库本体的 Git 备份见 7.5，与网站发布无关。

***

## 内容目录

| 目录 | 内容 |
| ---- | ---- |
| [[1-1 演变历史]] | 前端技术演变历史（虚拟 DOM、打包工具、模块化、元框架） |
| 2-html-css-js | CSS 渲染（重排重绘/Composite）、JS 基础（[[事件循环]]、[[闭包与作用域链]]） |
| 3-spa框架 | [[3-1 SPA原理与前端路由]]、[[3-2 Vue核心原理]]、[[3-3 React核心原理]] |
| 4-工程化 | Docker 镜像、K8s 部署、Git/Docker/Linux/Npm 指令、环境变量 |
| 5-部署测试 | [[打包后的web内容]]、[[Nginx部署与配置]] |
| 6-数据库 | [[数据库安装]]、[[MySQL索引与SQL优化]] |
| 7-python | 待补充 |
| 8-java | 待补充 |
| 9-agent | LLM、Agent 开发、RAG、向量库、agent 框架 |
| 10-AIGC | 待补充 |

> 私密笔记放 `private/` 文件夹，Quartz 构建时直接忽略，不会发布。

***

## 一、Obsidian：本地知识库（写作端）

**这个仓库（`E:\本地笔记本\knowledge-base`）本身就是 Obsidian 仓库**，日常只需要：

1. 用 Obsidian 打开本目录，正常新建/编辑 `.md` 笔记
2. 约定：
   - 内部链接用 `[[笔记名]]`（Quartz 的 obsidian 模板原生支持）
   - 图片等附件放 `attachments/`
   - 不想发布的笔记放 `private/`（或 front matter 加 `draft: true`）
3. 笔记顶部可加 front matter 控制发布行为：

```yaml
---
title: 笔记标题
tags:
  - 标签
draft: false    # true 则不发布
---
```

> ⚠️ 仓库根目录必须保留本文件 `index.md`，Quartz 用它作为网站首页（`/` 路径）。

Obsidian 端没有其他要做的事——写完笔记，进入第二步构建。

***

## 二、Quartz：把知识库变成静态网站（构建端）

### 2.1 前置要求

```bash
node -v   # 必须 ≥ 22，低了先用 nvm 升级
git --version
```

### 2.2 初始化 Quartz 项目（一次性，已完成）

> ⚠️ 以下是 GitHub Template 的历史做法。本机 `github.com` 主站不通，实际改用「quartz源码包 + 国内 npm 镜像」初始化，见第六节。

推荐用 GitHub Template 方式，免手动配置 remote：

1. 打开 <https://github.com/jackyzha0/quartz>，点 **Use this template → Create a new repository**，建一个自己的仓库（如 `knowledge-base-site`）
2. 克隆**你自己的新仓库**并初始化：

```bash
git clone https://github.com/<你的用户名>/knowledge-base-site.git my-quartz
cd my-quartz
npm install
```

3. 初始化内容源（把 Obsidian 仓库接进来）：

```bash
npx quartz create --template obsidian --strategy symlink --source "F:\knowledge-base" --baseUrl <你的用户名>.github.io/knowledge-base-site
```

| 参数 | 说明 |
| ---- | ---- |
| `--template obsidian` | 开启 wikilink / callout / mermaid 等 Obsidian 语法支持 |
| `--strategy symlink` | **符号链接**到知识库目录，Obsidian 一改，构建立即生效（不想链接可换 `copy`） |
| `--baseUrl` | GitHub Pages 项目站点格式：`用户名.github.io/仓库名`，**不带 `https://`、不带尾斜杠** |

### 2.3 安装社区插件（⚠️ 必须执行）

```bash
npx quartz plugin install --from-config
```

模板配置里引用的社区插件靠这一步下载，漏了会构建报错。部分失败就再跑：

```bash
npx quartz plugin install --latest
```

### 2.4 修改 `quartz.config.yaml`（只改 configuration 段）

```yaml
configuration:
  pageTitle: "我的知识库"
  locale: "zh-CN"
  baseUrl: "<你的用户名>.github.io/knowledge-base-site"   # 见 2.2 的格式要求
  ignorePatterns:
    - private        # 私密笔记不发布
    - .obsidian
```

> ⚠️ `baseUrl` 不能为空字符串，也不能带 `https://` 前缀和尾斜杠，配错会导致 404 或样式加载失败。`plugins:` 段由模板生成，**不要手写重写**。

### 2.5 本地预览

```bash
npx quartz build --serve
```

浏览器打开 <http://localhost:8080>，检查无误后进入第三步部署。

***

## 三、GitHub：发布到公网（历史方案，已停用）

> 本机 `github.com` 主站无法访问，此链路仅作回退参考。实际发布方式见第七节。

### 3.1 准备 Actions 部署文件

仓库自带的 `.github/workflows/deploy.yml` 核对即可，关键内容：

```yaml
on:
  push:
    branches:
      - v5            # Quartz 主线分支

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v6
        with:
          node-version: 24
      - run: npm ci
      - run: npx quartz plugin install   # CI 上也必须装社区插件
      - run: npx quartz build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: public
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
    steps:
      - uses: actions/deploy-pages@v4
```

> `quartz.lock.json` 必须提交到仓库，CI 靠它锁定插件版本。

### 3.2 开启 GitHub Pages（一次性）

GitHub 仓库 → **Settings → Pages** → **Source 选 GitHub Actions**（不是 Deploy from branch）。

### 3.3 推送上线

```bash
# 首次推送（远端还没有提交时）
npx quartz sync --no-pull

# 之后日常更新只需要
npx quartz sync
```

`npx quartz sync` 自动完成：拉取远端 → 构建 → 提交 → 推送 → 触发 Actions 部署。

### 3.4 访问

部署成功后（2~3 分钟），站点地址：

```
https://<你的用户名>.github.io/<仓库名>/
```

与 `quartz.config.yaml` 里的 `baseUrl` 保持一致。

***

## 四、日常更新（唯一要记的工作流）

> ⚠️ 历史工作流，已停用（`site.bat` 已移除）；当前更新方式见 7.3。

```
1. Obsidian 里写/改笔记（本仓库）
2. 双击 site.bat，或任意终端执行 git site
   → 同步内容到 ../my-quartz/content 并构建出 public/
3. 在 WorkBuddy 里说「更新网站」
   → 覆盖发布，分享链接不变
```

> 不需要 git push、不需要 Actions、不需要访问 GitHub。

***

## 五、常见问题排查（仅本链路）

| 症状 | 原因 | 解决 |
| ---- | ---- | ---- |
| 构建报 `Cannot parse plugin source: builtin:xxx` | 手写了 `plugins:` 段，插件源格式错误 | 恢复模板配置；正确格式是 `@quartz-community/xxx` |
| `Plugin Xxx failed to build` | 社区插件没装/编译失败 | `npx quartz plugin install --from-config`，再不行 `--latest` |
| `Error: Node vX is not supported` | Node < 22 | nvm 升级到 22+ |
| 首页报 "Either this page is private or doesn't exist." | 仓库根目录缺 `index.md` | 保留本文件 |
| 页面 404 / 路径多一层 | `baseUrl` 与实际地址不匹配 | 改成 `用户名.github.io/仓库名`，不带 https:// 和尾斜杠 |
| Actions 报不允许部署到 github-pages | 旧环境保护规则残留 | Settings → Environments 删除 `github-pages`，下次自动重建 |
| `npx quartz sync` 推送失败 | upstream 变更未合并 | 确认在 `v5` 分支；手动 `git pull` 解决冲突后再 sync |
| 页面空白 / 构建 0 页 | 符号链接损坏或 ignorePatterns 过宽 | Windows 用管理员权限重建链接，或改 `--strategy copy` |
| 笔记里有 Dataview / Canvas / Excalidraw | Quartz 不支持 | Dataview 换成静态结果；Canvas/Excalidraw 导出为图片 |

***


## 六、发布端：自有云服务器（当前唯一方案）

### 6.1 实际配置（2026-11-08 起）

| 项      | 值                                                             |
| ------ | ------------------------------------------------------------- |
| 服务器    | 阿里云 ECS `8.140.217.146` / Alibaba Cloud Linux 3.2104 LTS 64 位 |
| 访问地址   | `http://8.140.217.146/`（80 与 8080 端口均可）                       |
| SSH    | `root` / 22 / 专用密钥 `~/.ssh/id_ed25519_kbdeploy`（免密）           |
| Web 服务 | Nginx 1.24，站点根目录 `/var/www/knowledge-base`                    |
| 安全组    | 入方向放行 TCP 80、8080                                             |
| 本机配置   | `my-quartz/deploy/deploy.conf`                                |
| 入口     | 双击 `knowledge-base/deploy.bat`，或任意终端 `git deploy`             |

服务器**不需要** Node、Git、rsync 或 CI；本机 Windows 也没有 rsync，用 `tar over SSH` 一条管道直传（产物压缩后约 4 MB）。

### 6.2 一次性准备（已完成）

两件事必须在阿里云侧人工做，脚本代劳不了：

1. 把部署公钥加进服务器 `~/.ssh/authorized_keys`（控制台「远程连接 / Workbench」粘贴一行即可），私钥只留在本机。
2. ECS 安全组 → 入方向放行 TCP 80 / 8080。云厂商安全组在服务器外面，服务器里开防火墙不算数。

其余全部由 `git deploy --init` 完成：`dnf` 安装 Nginx、建站点目录、写 `/etc/nginx/conf.d/knowledge-base.conf`、禁用发行版 `default.conf` 避免 `default_server` 冲突、`nginx -t` 校验、处理 SELinux / firewalld、`systemctl enable --now nginx`。该命令幂等，可重复执行。

### 6.3 日常用法

| 动作 | 怎么做 |
| ---- | ---- |
| 更新并上线 | 双击 `deploy.bat`，或终端 `git deploy` |
| 只校验配置 | `git deploy --dry-run` |
| 新服务器 / 重装 | `git deploy --init` |
| 看发了什么 | 终端输出文件数、体积、SSH 结果；服务器上 `ls /var/www/knowledge-base`、`nginx -t` |
| 回滚 | 把 `/root/kb-deploy/backups/` 里最近的 tar.gz 解回站点目录（自动保留最近 5 份） |

`git deploy` 内部依次执行：同步 `baseUrl` → 同步笔记 → Quartz 构建 → 隐私自检 → `tar over SSH` 直传 → 服务器端校验 `index.html` + 备份旧版 + 原子切换 → `curl` 线上自检。任何一步失败都会中止，不会留下半个站点。

### 6.4 关键坑

1. **`baseUrl` 自动改写**成 `SITE_URL` 的主机名部分；换域名只改 `deploy.conf` 一处（设 `SYNC_BASEURL=0` 可关闭自动同步）。
2. **Nginx 必须 `try_files $uri $uri.html $uri/ =404;`**：Quartz 的站内链接不带 `.html`，照搬 SPA 的 `/index.html` 兜底会全站跳首页。见 [[Nginx部署与配置]]。
3. **Quartz v5 硬编码 `https://${baseUrl}`** 生成 canonical / `og:url` / sitemap / RSS。纯 HTTP 站点会指向并不存在的 443，因此 `remote-receive.sh` 在切换前把产物里的绝对 URL 归一化成 `SITE_URL` 的实际协议（每次约 127 个文件）；将来换成 HTTPS 则自动不改动。
4. **隐私责任在自己**：`deploy.sh` 每次发布前检查 `private/`、`.workbuddy/`、`.obsidian/`、账号文件与配置是否混进产物，发现即中止。`deploy.conf` 含服务器信息，只放本地，不写进会被发布的笔记。
5. **备案**：用公网 IP 直访 80 端口通常不触发域名备案拦截（校验针对未备案域名作为 Host 的请求）；换成域名 + 80/443 则必须先完成 ICP 备案，否则走 8080 等非标端口。
6. `git deploy` 是仓库级 alias；换机器或重建仓库后需重新配置。
7. 初始化时的 `conflicting server name "_"` 警告无害——发行版主配置里的同名 server 被忽略，实测 80/8080 都返回本知识库页面。

### 6.5 Git 源码备份（与网站发布无关）

知识库本体仍是一个 Git 仓库，远程在 Gitee，**只用于笔记内容的版本备份**，与上面的发布链路完全独立：`git deploy` 只发网站、不推 Git；`git sync` 只推笔记、不更新网站。

| 动作    | 怎么做                                                                               |
| ----- | --------------------------------------------------------------------------------- |
| 备份并推送 | 双击 `sync.bat`，或终端 `git sync "本次改了什么"`                                             |
| 内部流程  | `git add -A` → 有改动才 commit → `pull --rebase origin master` → `push origin master` |

注意 `add -A` 会提交仓库内所有改动，包括 `private/` 与 `.workbuddy/` 等本地文件；推送前确认远程仓库可见性，敏感内容请自行加进 `.gitignore`。

***

## 参考链接

- Obsidian: <https://obsidian.md>
- Quartz 官方文档: <https://quartz.jzhao.xyz>
- Quartz 官方 Hosting 文档: <https://quartz.jzhao.xyz/hosting>
- Quartz GitHub: <https://github.com/jackyzha0/quartz>
- GitHub Pages: <https://pages.github.com>
- Cloudflare Pages: <https://pages.cloudflare.com>
- 腾讯云 EdgeOne Pages: <https://edgeone.cloud.tencent.com/pages>
- [[Nginx部署与配置]]
