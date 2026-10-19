---
title: 我的知识库
---

# 我的知识库

> 一句话：**Obsidian 负责创建和维护本地知识库 → Quartz 把这个仓库编译成静态 Web 站点 → 部署到 GitHub Pages，公网可访问。**

```
Obsidian（本地写作，本仓库就是知识库）
        │
        ▼
Quartz（编译仓库 → 静态网站，本地可预览）
        │
        ▼
GitHub Pages（推送到 GitHub 自动构建发布，公网访问）
```

| 环节 | 工具 | 干什么 |
| ---- | ---- | ---- |
| ① 写 | Obsidian | 编辑 Markdown 笔记，wikilink 互链 |
| ② 建 | Quartz (Node.js ≥ 22) | 把 Obsidian 仓库渲染成静态站点 |
| ③ 发 | GitHub Actions + GitHub Pages | 推送即自动构建上线 |

***

## 内容目录

| 目录 | 内容 |
| ---- | ---- |
| [[1-1 演变历史]] | 前端技术演变历史（虚拟 DOM、打包工具、模块化、元框架） |
| 2-html-css-js | CSS 渲染（重排重绘/Composite）、JS 基础（[[事件循环]]、[[闭包与作用域链]]） |
| 3-spa框架 | [[3-1 SPA原理与前端路由]]、[[3-2 Vue核心原理]]、[[3-3 React核心原理]] |
| 4-工程化 | Docker 镜像、K8s 部署、Git/Docker/Linux/Npm 指令、环境变量 |
| 5-agent | LLM、Agent 开发、RAG、向量库、agent 框架 |
| 6-数据库 | [[数据库安装]]、[[MySQL索引与SQL优化]] |
| 7-部署测试 | [[打包后的web内容]]、[[Nginx部署与配置]] |

> 私密笔记放 `private/` 文件夹，Quartz 构建时直接忽略，不会发布。

***

## 一、Obsidian：本地知识库（写作端）

**这个仓库（`F:\knowledge-base`）本身就是 Obsidian 仓库**，日常只需要：

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

### 2.2 初始化 Quartz 项目（一次性）

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

## 三、GitHub：发布到公网（部署端）

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

```
1. Obsidian 里写/改笔记（本仓库）
2. cd my-quartz
3. npx quartz sync        # 构建 + 提交 + 推送，Actions 自动发布
4. 几分钟后网站更新
```

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

## 参考链接

- Obsidian: <https://obsidian.md>
- Quartz 官方文档: <https://quartz.jzhao.xyz>
- Quartz GitHub: <https://github.com/jackyzha0/quartz>
- GitHub Pages: <https://pages.github.com>
