# Obsidian + Syncthing + Quartz 完整搭建指南

> 本地笔记 → 多端同步 → 静态网站发布，全流程零费用、数据自主可控。

***

## 一、架构概览

```
Obsidian (编辑) ──本地仓库──→ Syncthing (同步) ──→ 其他设备
                                   │
                                   ▼
                            Quartz (生成静态站) ──→ 部署到 Cloudflare Pages / Vercel / GitHub Pages
```

| 组件        | 角色                         | 平台                                      |
| --------- | -------------------------- | --------------------------------------- |
| Obsidian  | Markdown 笔记编辑器             | Windows / macOS / Linux / iOS / Android |
| Syncthing | 去中心化文件同步                   | Windows / macOS / Linux / Android / NAS |
| Quartz    | 静态站点生成器（基于 Obsidian vault） | Node.js ≥ 22                            |

***

## 二、Obsidian 安装与配置

### 2.1 下载安装

官网：<https://obsidian.md/download>

安装后首次启动，选择 **"创建新仓库"**，路径建议：

```
# Windows 示例
D:\ObsidianVault

# macOS / Linux 示例
~/ObsidianVault
```

> 此路径同时是 Syncthing 同步目录和 Quartz 内容源。

### 2.2 核心配置

1. **设置 → 编辑器**

   * 关闭"严格换行"（Strict Line Breaks），保留 Markdown 原生换行

   * 开启"自动配对括号"

2. **设置 → 文件与链接**

   * 新建笔记存放位置：`/`

   * 内部链接类型：最短路径

   * 附件默认存放路径：`attachments`

3. **设置 → 外观**

   * 自定义 CSS（可选）

### 2.3 推荐插件（社区插件）

| 插件                            | 用途        |
| ----------------------------- | --------- |
| Templater                     | 模板管理      |
| Dataview                      | 数据查询与动态视图 |
| Calendar                      | 日历视图      |
| Tag Wrangler                  | 标签管理      |
| Ozan's Image in Editor Plugin | 编辑器内图片预览  |

安装方式：设置 → 第三方插件 → 关闭安全模式 → 浏览 → 安装

***

## 三、Syncthing 多端同步

### 3.1 安装

| 平台      | 安装方式                                                                                                                        |
| ------- | --------------------------------------------------------------------------------------------------------------------------- |
| Windows | [Syncthing \| Downloads](https://syncthing.net/downloads/) 下载 `syncthing-windows-amd64-xxx.zip`，解压运行；或用 SyncTrayzor（GUI 封装） |
| macOS   | `brew install --cask syncthing`                                                                                             |
| Linux   | `sudo apt install syncthing` / `sudo pacman -S syncthing`                                                                   |
| Android | Google Play / F-Droid 搜索 Syncthing                                                                                          |
| NAS     | 群晖：社区源 `syncthing`；威联通：Container Station 部署                                                                                 |

### 3.2 启动与 Web UI

```bash
# 首次启动（所有平台）
syncthing

# 浏览器自动打开 http://localhost:8384
```

### 3.3 设备互联

1. **设备 A**：操作 → 显示 ID → 复制设备 ID
2. **设备 B**：添加远程设备 → 粘贴设备 A 的 ID → 保存
3. **设备 A**：弹出提示"设备 B 想要连接"→ 允许

> 两台设备需在同一网络或配置公网发现/中继。默认启用全球发现服务器，也可配置自建发现服务器。

### 3.4 共享文件夹（同步 Obsidian 仓库）

1. 设备 A 上：添加文件夹

   * 文件夹 ID：`obsidian-vault`

   * 文件夹路径：`D:\ObsidianVault`（与 Obsidian 仓库路径一致）
2. 共享给：勾选设备 B
3. 设备 B 上：弹出提示"想共享文件夹"→ 接受

   * 本地路径设为：`/home/user/ObsidianVault`

### 3.5 忽略规则

在共享文件夹设置 → 忽略模式 中添加：

```
// 忽略 Obsidian 工作区配置（每台设备独立）
.obsidian/workspace.json
.obsidian/workspace-mobile.json

// 忽略 Quartz 构建产物与插件
.quartz-cache/
.quartz/
public/

// 忽略系统文件
.DS_Store
Thumbs.db
desktop.ini
```

### 3.6 版本控制（防误删）

文件夹设置 → 文件版本控制 → 选择策略：

| 策略     | 说明                                  |
| ------ | ----------------------------------- |
| 简单文件暂存 | 删除/覆盖的文件移到 `.stversions/` 目录，保留所有版本 |
| 交错文件暂存 | 按时间间隔保留版本，节省空间                      |

推荐"简单文件暂存"，路径 `.stversions`。

***

## 四、Quartz 静态站点搭建

### 4.1 前置要求

* **Node.js ≥ 22**（CI 环境推荐 24）

* Git ≥ 2.x

* npm ≥ 10.9

```bash
node -v   # 必须输出 v22.x 或更高，低于则升级
npm -v
git --version
```

> 版本不符时，Windows 推荐 [nvm-windows](https://github.com/coreybutler/nvm-windows)，macOS/Linux 用 `nvm`：
>
> ```bash
> nvm install 22
> nvm use 22
> ```

### 4.2 获取 Quartz（两种方式选其一）

#### 方案 A：使用 GitHub Template（✅ 推荐）

一键生成你的独立仓库，不需要手动改 Git remote。

1. 打开 <https://github.com/jackyzha0/quartz>，点击右上角 **Use this template → Create a new repository**
2. 填写仓库名（如 `my-quartz`、`notes`、`knowledge-base`），选择 Public/Private，点 **Create repository**
3. 克隆**你自己的新仓库**：

```bash
git clone https://github.com/<你的用户名>/<你的仓库名>.git my-quartz
cd my-quartz
```

#### 方案 B：直接克隆官方仓库

如果不用 GitHub 或偏好手动配置：

```bash
git clone https://github.com/jackyzha0/quartz.git my-quartz
cd my-quartz
```

> 此方式后续需要自己把 `origin` 指到你的仓库（见 5.1 节）。

### 4.3 安装依赖

```bash
npm install
# 或简写：npm i
```

> 之后在新机器上重新拉取自己的仓库时，用 `npm ci`（更快，基于 lockfile 精确还原）。

### 4.4 交互式初始化（核心步骤）

```bash
npx quartz create
```

向导会依次询问以下问题，请按提示选择：

| 步骤 | 问题                         | 推荐选择                                                           | 说明                                                                                                       |
| -- | -------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 1  | Choose a template          | **Obsidian**                                                   | 模板：`default` / `obsidian` / `ttrpg` / `blog`。Obsidian 模板自动开启 OFM 支持、wikilink、callouts 等，并跳过链接解析提示        |
| 2  | How to handle content      | **symlink**（推荐） 或 **copy**                                     | 策略：• `new` = 空 content 文件夹• `copy` = 把源文件夹**复制**一份到 content• `symlink` = 建**符号链接**到源目录，Obsidian 修改即时生效 ✅ |
| 3  | Enter the source directory | 填入你的 Obsidian 仓库路径，如 `D:\ObsidianVault`                        | 仅选择 copy/symlink 时出现                                                                                     |
| 4  | Enter base URL             | 如 `yourname.github.io/knowledge-base` 或 `notes.yourdomain.com` | **不要**加 `https://` 和尾斜杠；部署到子路径必须包含子路径部分                                                                  |
| 5  | Choose link resolution     | （选 Obsidian 模板时自动跳过）                                           | `shortest`（Obsidian 默认）/ `absolute` / `relative`                                                         |

**非交互式等价命令**（一步完成，推荐直接用这个）：

```bash
# Windows 示例
npx quartz create --template obsidian --strategy symlink --source "D:\ObsidianVault" --baseUrl yourname.github.io/knowledge-base

# macOS / Linux 示例
npx quartz create --template obsidian --strategy symlink --source ~/ObsidianVault --baseUrl yourname.github.io/knowledge-base
```

> ⚠️ **创建后必须确保 Obsidian 仓库根目录有一个 `index.md` 文件**（即 Obsidian 中名为 `index` 的笔记）。Quartz 用它作为网站首页（`/` 路径）。如果没有，访问首页会报 "Either this page is private or doesn't exist."。
>
> 在 Obsidian 中新建一个笔记，命名为 `index`，内容示例：
> ```markdown
> ---
> title: 我的知识库
> ---
>
> 欢迎来到我的知识库。
> ```

### 4.5 安装社区插件（⚠️ 必须执行）

模板配置中引用了社区插件，需要单独下载：

```bash
npx quartz plugin install --from-config
```

该命令会读取 `quartz.config.yaml` 中的插件列表，下载并编译到 `.quartz/plugins/` 目录。

> 如果部分插件构建失败，尝试刷新到最新版本：
>
> ```bash
> npx quartz plugin install --latest
> ```

### 4.6 配置 Quartz（`quartz.config.yaml`）

Quartz 的主配置文件是 **YAML 格式**（不再是旧版的 `.ts` 文件）。文件路径：`quartz.config.yaml`。

> ⚠️ **重要**：`npx quartz create --template obsidian` 已经自动生成了完整的、可用的 `quartz.config.yaml`，包含所有插件和布局配置。**不建议手动重写整个文件**，只需修改 `configuration:` 段中的站点信息即可。插件源格式、布局结构等由模板管理，手动修改容易出错（如插件源名写错导致 `Cannot parse plugin source` 错误）。

#### 4.6.1 需要修改的部分（`configuration` 段）

打开 `quartz.config.yaml`，只修改 `configuration:` 下的字段：

```yaml
configuration:
  pageTitle: "我的知识库"                    # 站点标题
  pageTitleSuffix: ""                       # 浏览器标签页后缀（可选）
  enableSPA: true                            # SPA 路由（保持 true）
  enablePopovers: true                      # 悬停链接弹出预览（保持 true）
  analytics:                                 # 分析工具，null = 不用
    provider: plausible                      # 或 google / umami / goatcounter 等
  locale: "zh-CN"                            # 日期和国际化语言
  baseUrl: "yourname.github.io/knowledge-base"  # ⚠️ 不含 https://，与 create 时一致
  ignorePatterns:
    - private                                # 忽略 private 文件夹（敏感笔记）
    - templates                              # 忽略 Obsidian 模板文件夹
    - .obsidian                              # Obsidian 配置目录
    - .stversions                            # Syncthing 版本历史
    - .stfolder
    - "*.sync-conflict-*"                    # Syncthing 冲突文件
  theme:
    fontOrigin: googleFonts                  # googleFonts 或 local
    cdnCaching: true
    typography:
      header: "Schibsted Grotesk"
      body: "Source Sans Pro"
      code: "IBM Plex Mono"
    colors:
      lightMode:                             # ⚠️ 浅色主题（注意是嵌套对象）
        light: "#faf8f8"
        lightgray: "#e5e5e5"
        gray: "#b8b8b8"
        darkgray: "#4e4e4e"
        dark: "#2b2b2b"
        secondary: "#284b63"
        tertiary: "#84a59d"
        highlight: "rgba(143, 159, 169, 0.15)"
        textHighlight: "#fff23688"
      darkMode:                              # ⚠️ 深色主题（注意是嵌套对象）
        light: "#161618"
        lightgray: "#393639"
        gray: "#646464"
        darkgray: "#d4d4d4"
        dark: "#ebebec"
        secondary: "#7b97aa"
        tertiary: "#84a59d"
        highlight: "rgba(143, 159, 169, 0.15)"
        textHighlight: "#b3aa0288"
```

> 以上 `theme.colors` 的 `lightMode` / `darkMode` 双主题结构是 Quartz v5 的标准格式。如果只想要单一主题，可以只保留一个。

#### 4.6.2 插件配置说明（`plugins` 段）

模板生成的 `plugins:` 段已经包含全部所需插件，**一般不需要手动修改**。了解格式即可：

```yaml
plugins:
  - source: "@quartz-community/created-modified-date"   # ⚠️ 格式：@scope/name
    enabled: true
    order: 10                                            # 执行顺序（数字越小越先执行）
    options:                                              # 插件选项（可选）
      defaultDateType: modified

  - source: "@quartz-community/obsidian-flavored-markdown"
    enabled: true
    order: 30
    options:
      wikilinks: true
      callouts: true
      mermaid: true
      parseTags: true

  # ... 其他插件，模板已自动配置
```

**插件源格式**：`@quartz-community/插件名`（npm scope 风格，不是 `github:xxx` 也不是 `builtin:xxx`）

**Obsidian 模板自带的核心插件对照表**：

| 插件源 (`@quartz-community/xxx`) | 作用                                      | 旧名（v4）                   |
| ----------------------------- | --------------------------------------- | ------------------------ |
| `note-properties`             | 解析 frontmatter + 属性面板                   | FrontMatter              |
| `created-modified-date`       | 创建/修改日期                                 | CreatedModifiedDate      |
| `obsidian-flavored-markdown`  | Obsidian 语法支持（wikilink/callout/mermaid） | ObsidianFlavoredMarkdown |
| `syntax-highlighting`         | 代码高亮                                    | SyntaxHighlighting       |
| `crawl-links`                 | 链接解析                                    | CrawlLinks               |
| `description`                 | 自动摘要                                    | Description              |
| `latex`                       | LaTeX 公式（KaTeX）                         | Latex                    |
| `table-of-contents`           | 目录                                      | TableOfContents          |
| `remove-draft`                | 过滤草稿                                    | RemoveDrafts             |
| `alias-redirects`             | 别名重定向                                   | AliasRedirects           |
| `content-index`               | RSS / Sitemap                           | ContentIndex             |
| `content-page`                | 内容页面渲染                                  | ContentPage              |
| `folder-page`                 | 文件夹列表页                                  | FolderPage               |
| `tag-page`                    | 标签列表页                                   | TagPage                  |
| `explorer`                    | 文件树导航                                   | Explorer                 |
| `search`                      | 全文搜索                                    | Search                   |
| `graph`                       | 关系图谱                                    | Graph                    |
| `backlinks`                   | 反向链接                                    | Backlinks                |
| `page-title`                  | 页面标题                                    | PageTitle                |
| `darkmode`                    | 深色模式切换                                  | Darkmode                 |
| `spacer`                      | 间距占位                                    | Spacer                   |

> 完整插件列表见 <https://quartz.jzhao.xyz/plugins>

#### 4.6.3 布局配置说明（`layout` 段）

Quartz v5 的布局配置也合并到 `quartz.config.yaml` 中（不再有独立的 `quartz.layout.ts`）。每个插件通过其 `layout` 字段指定位置：

```yaml
plugins:
  - source: "@quartz-community/explorer"
    enabled: true
    layout:
      position: left       # 位置：left / right / beforeBody / afterBody / footer
      priority: 50          # 优先级（数字越大越靠前）

  - source: "@quartz-community/graph"
    enabled: true
    layout:
      position: right
      priority: 10

  - source: "@quartz-community/spacer"
    enabled: true
    layout:
      position: left
      priority: 25
      display: mobile-only   # 可选：all / mobile-only / desktop-only
```

模板已自动配置好所有布局，一般不需要手动修改。如需调整某个组件的位置或显示条件，修改对应插件的 `layout` 字段即可。

#### 4.6.4 高级覆盖

若某些插件选项需要 JS 回调函数（YAML 无法表达），编辑根目录的 `quartz.ts`，通过 `loadQuartzConfig()` 做覆盖。见 [官方 Configuration 文档](https://quartz.jzhao.xyz/configuration)。

### 4.7 Front Matter 模板

在 Obsidian 笔记的顶部添加 YAML front matter 控制发布行为：

```yaml
---
title: 笔记标题
date: 2025-01-01
tags:
  - 标签1
  - 标签2
draft: false       # true 则不发布（配合 remove-draft 插件）
aliases:
  - 别名1
description: "摘要，用于搜索结果和 SEO（可选）"
---
```

**不发布特定笔记**的方式：

1. `draft: true` — 通过 `remove-draft` 插件过滤
2. 放入 `private/` 文件夹 — 通过 `ignorePatterns` 忽略（建议）
3. 文件名以 `_` 开头 — 可追加到 ignorePatterns

### 4.8 本地预览

```bash
npx quartz build --serve
```

访问 <http://localhost:8080> 查看效果。开发服务器监听文件变更并自动热更新。

> 若只想构建不启动服务：`npx quartz build`，产物输出到 `public/` 目录。

### 4.9 自定义样式

**方式 1（推荐）**：编辑 `quartz.config.yaml` 中的 `configuration.theme` 部分调整配色和字体。

**方式 2**：在 `quartz/styles/` 目录下创建/编辑 `custom.scss`，添加自定义 CSS/SCSS 覆盖：

```scss
// quartz/styles/custom.scss
body {
  // 全局样式覆盖
}

// 示例：调整标题样式
.page-title {
  font-weight: 700;
}
```

***

## 五、部署到 GitHub Pages

### 5.1 设置 GitHub 仓库

#### 情况 A：使用了 Template（4.2 方案 A）

✅ 仓库已准备好，`origin` 已自动指向你自己的仓库，跳过直接看 5.2。

#### 情况 B：直接克隆官方仓库（4.2 方案 B）

1. 在 [GitHub 新建仓库](https://github.com/new)

   * ⚠️ **不要**勾选 Initialize with README / LICENSE / `.gitignore`（Quartz 自带，重复会冲突）
2. 回到本地 Quartz 目录设置 remote：

```bash
# 查看当前 remote
git remote -v

# 把 origin 指到你的新仓库（替换 URL）
git remote set-url origin https://github.com/<你的用户名>/<你的仓库名>.git
```

> `npx quartz create` 已经自动配置好了 `upstream` remote（用于后续 `npx quartz upgrade` 升级 Quartz），不需要手动添加。

### 5.2 自动部署（GitHub Actions）

创建/编辑 `.github/workflows/deploy.yml`（Quartz 可能已自带，核对内容即可）：

```yaml
name: Deploy Quartz site to GitHub Pages

on:
  push:
    branches:
      - v5      # ⚠️ 当前 Quartz 主线为 v5（稳定版仍可用 v4）

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0    # 拉取完整历史，供 git 日期信息使用

      - uses: actions/setup-node@v6
        with:
          node-version: 24  # 与本地 Node 22 兼容

      # 缓存 npm 依赖（加速构建）
      - name: Cache dependencies
        uses: actions/cache@v5
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-

      # 缓存 Quartz 社区插件
      - name: Cache Quartz plugins
        uses: actions/cache@v5
        with:
          path: .quartz/plugins
          key: ${{ runner.os }}-plugins-${{ hashFiles('quartz.lock.json') }}
          restore-keys: |
            ${{ runner.os }}-plugins-

      - name: Install Dependencies
        run: npm ci

      # ⚠️ 关键：安装社区插件（官方文档要求）
      - name: Install Quartz plugins
        run: npx quartz plugin install
        # 如果有人会改 yaml 但不更新 lockfile，换成：
        # run: npx quartz plugin install --from-config

      - name: Build Quartz
        run: npx quartz build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 5.3 启用 GitHub Pages 并推送

1. GitHub 仓库 → **Settings → Pages**
2. **Source** 选择 **GitHub Actions**（不是 Deploy from branch）
3. 回到本地，首次推送用：

```bash
# 确保当前在 v5 分支（Quartz 克隆后默认就是 v5）
git branch
# 若不在 v5，执行：git checkout -b v5

# 首次提交推送（--no-pull = 不拉取远端变更）
npx quartz sync --no-pull
```

`npx quartz sync` 会自动：构建 → 提交所有变更 → 推送到仓库 → 触发 Actions 部署。

**后续日常更新只需要**：

```bash
npx quartz sync
```

> 如果遇到环境保护规则报错「不允许部署到 github-pages」：到 **仓库 Settings → Environments**，删除旧的 `github-pages` 环境，下次 Actions 运行会自动重建。

部署成功后，你的站点地址为：`https://<你的用户名>.github.io/<仓库名>/`（与 `baseUrl` 保持一致）。

### 5.4 自定义域名（可选）

1. **在 GitHub Pages 设置中配置**（推荐，不再用 CNAME 文件方式）：

   * 仓库 → **Settings → Pages → Custom domain**

   * 填入域名（如 `notes.yourdomain.com`），点击 **Save**
2. 在 DNS 服务商添加解析：

   * **子域名**（如 notes.example.com）：添加 `CNAME` 记录指向 `<你的用户名>.github.io`

   * **顶级域名**（如 example.com）：添加 4 条 `A` 记录分别指向：

     ```
     185.199.108.153
     185.199.109.153
     185.199.110.153
     185.199.111.153
     ```
3. 勾选 **Enforce HTTPS**（DNS 生效后才可选）

***

## 六、部署到国内可访问的平台（替代方案）

> ⚠️ **重要提醒**：GitHub Pages 和 Vercel 的默认域名（`*.github.io`、`*.vercel.app`）在国内访问极不稳定，经常超时或无法打开。如果你在国内使用，**强烈推荐使用 Cloudflare Pages**（`*.pages.dev` 域名国内访问稳定），或给 Vercel 绑定自定义域名。

### 6.0 部署平台对比

| 平台 | 国内访问速度 | 免费额度 | 域名 | 推荐度 |
|------|-----------|---------|------|-------|
| **Cloudflare Pages** | ⭐⭐⭐⭐ 稳定 | 无限流量 | `*.pages.dev` | ✅ 国内首选 |
| **Vercel** + 自定义域名 | ⭐⭐⭐⭐ 快 | 100GB/月 | 自定义域名 | ✅ 有域名时推荐 |
| **Vercel** 默认域名 | ⭐❌ 经常被墙 | 100GB/月 | `*.vercel.app` | ❌ 不推荐国内使用 |
| **Netlify** | ⭐⭐⭐ 较稳定 | 100GB/月 | `*.netlify.app` | ⚠️ 可选 |
| GitHub Pages | ⭐⭐ 不稳定 | 100GB/月 | `*.github.io` | ❌ 不推荐国内使用 |

### 6.1 部署到 Cloudflare Pages（⭐ 国内推荐）

Cloudflare Pages 的 `*.pages.dev` 域名在国内访问稳定，且免费额度无限流量，是国内用户的首选方案。

#### 步骤

1. 打开 <https://pages.cloudflare.com>，用 GitHub 账号登录
2. 点 **Create a project → Connect to Git**
3. 选择你的 Quartz 仓库（如 `knowledge-base`）
4. 配置构建参数：

   | 配置项 | 值 |
   |-------|---|
   | Framework preset | `None` |
   | Root directory | （留空） |
   | Build command | `npm ci && npx quartz plugin install && npx quartz build` |
   | Build output directory | `public` |

5. 展开 **Environment variables**，添加：

   | 变量名 | 值 |
   |-------|---|
   | `NODE_VERSION` | `24` |

6. 点 **Save and Deploy**，等待 2-3 分钟
7. 部署完成后获得 `xxx.pages.dev` 访问地址

#### 注意事项

- **不需要 `vercel.json`**，Cloudflare Pages 默认支持 clean URLs
- ⚠️ **必须创建 `wrangler.toml`**：Cloudflare Pages 构建后会执行 `npx wrangler deploy`，需要 `wrangler.toml` 告诉 Wrangler 静态文件在 `public/` 目录。在项目根目录创建：

  ```toml
  name = "knowledge-base"
  pages_build_output_dir = "public"
  compatibility_date = "2026-08-31"
  ```

  否则报错 `Could not detect a directory containing static files`。

- 如需修改 `baseUrl`：如果部署到 `xxx.pages.dev` 根路径，`baseUrl` 设为空字符串 `""` 或你的 `xxx.pages.dev` 域名（不含 `https://`）
- 每次推送到 GitHub 会自动触发重新部署

#### 自定义域名（可选）

1. Cloudflare Pages 项目 → **Custom domains → Set up a domain**
2. 输入你的域名（如 `notes.yourdomain.com`）
3. 按提示在 DNS 服务商添加 `CNAME` 记录指向 `xxx.pages.dev`
4. 如果域名也在 Cloudflare 管理，会自动配置 DNS

---

### 6.2 部署到 Vercel（有自定义域名时可用）

> ⚠️ Vercel 的 `*.vercel.app` 默认域名在国内经常被墙，**必须绑定自定义域名才能正常访问**。如果你没有域名，请使用上面的 Cloudflare Pages。

### 6.2.1 必要配置文件（⚠️ 必须创建）

Quartz 生成的 URL **不带** **`.html`** **后缀**（如 `/notes/my-post`），Vercel 默认不会自动补后缀，会导致除首页外全部 404。在项目根目录创建 `vercel.json`：

```json
{
  "cleanUrls": true
}
```

### 6.2.2 通过 Vercel Dashboard 部署

1. 打开 <https://vercel.com/dashboard>，点击 **Add New… → Project**
2. 选择包含 Quartz 项目的 GitHub 仓库 → **Import**
3. 填写项目名（小写字母和短横线），确认以下配置：

| 配置项              | 值                                               |
| ---------------- | ----------------------------------------------- |
| Framework Preset | `Other`                                         |
| Root Directory   | `./`                                            |
| Build Command    | `npm ci && npx quartz plugin install && npx quartz build` |
| Output Directory | `public`                                        |

4. 点击 **Deploy**。部署完成后获得 `*.vercel.app` 访问地址。

> ⚠️ 部署成功后，`*.vercel.app` 域名在国内大概率无法访问。必须按 6.2.4 绑定自定义域名。

### 6.2.3 命令行方式（备选）

```bash
# 安装 Vercel CLI
npm i -g vercel

# 首次部署（交互式）
vercel

# 后续生产部署
npx quartz plugin install
npx quartz build
vercel --prod
```

### 6.2.4 自定义域名（国内访问必须）

1. 如有必要，更新 `quartz.config.yaml` 中的 `baseUrl` 为新域名（不含 https\://）
2. Vercel → **Dashboard → Domains** 页面添加域名，按指引连接到你的 Quartz 项目
3. 根据页面给出的提示，在 DNS 服务商添加解析记录（CNAME 或 A 记录）
4. 等待 DNS 生效后，Vercel 自动颁发 HTTPS 证书

***

## 七、日常工作流

```
1. 在任意设备用 Obsidian 编辑 / 新建笔记
2. Syncthing 自动同步到所有设备（含你的构建主机）
3. 构建主机上：
   cd my-quartz
   npx quartz sync          # 自动：拉取远端 → 构建 → 提交 → 推送
4. Cloudflare Pages / GitHub Actions / Vercel 自动构建部署，网站几分钟内更新
```

> **`npx quartz sync`** **等效于**：`git pull && npx quartz build && git add . && git commit -m 'update' && git push`，但更智能（处理上游 Quartz 升级冲突、插件 lockfile 等）。

**首次同步**（远端还没有任何提交时）：

```bash
npx quartz sync --no-pull
```

**进阶自动部署**：在服务器上配置 Syncthing + 监听脚本，Syncthing 检测到文件变更后自动构建推送，实现完全无人值守：

```bash
#!/bin/bash
# /usr/local/bin/quartz-rebuild.sh
cd /path/to/my-quartz
npx quartz sync
```

配合 Syncthing 的 **Folder Watcher** 或 `cron`（每 5 分钟执行一次）：

```
*/5 * * * * /usr/local/bin/quartz-rebuild.sh >> /var/log/quartz.log 2>&1
```

***

## 八、常见问题排查

### Syncthing 同步冲突

* 冲突文件命名格式：`filename.sync-conflict-20250101-120000-DEVICEID.md`

* 解决：手动合并内容后删除冲突文件

* 预防：避免同时在多设备编辑同一文件

### Quartz 构建报错

| 错误 / 现象                               | 常见原因                              | 解决方法                                                                                   |
| ------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------- |
| `Cannot find module`                  | npm 依赖缺失                          | 执行 `npm i`，新机器上用 `npm ci`                                                              |
| `Error: Node vX.X.X is not supported` | Node 版本过旧（< 22）                   | 升级 Node 到 22+（推荐 nvm/nvm-windows）                                                      |
| `Cannot parse plugin source: builtin:xxx` | 插件源格式写错（用了 `builtin:` 或 `github:` 前缀） | 改为 `@quartz-community/xxx`；或直接用模板生成的配置，不要手写插件列表（见 4.6 节） |
| `Failed to install plugin: builtin:FrontMatter` | 同上，`FrontMatter` 的正确源是 `@quartz-community/note-properties` | 同上：恢复模板生成的 `quartz.config.yaml`，不要手动重写 `plugins:` 段 |
| `Plugin Xxx failed to build`          | 社区插件编译失败，或未安装                     | 执行 `npx quartz plugin install --from-config`；仍失败用 `--latest`                           |
| `No files found under content/`       | content 为空，或 ignorePatterns 过滤了全部 | 检查 content/ 是否有 md 文件；检查 ignorePatterns 是否过于宽泛                                         |
| 页面空白 / 构建出 0 页                        | 同上，或符号链接损坏                        | Windows 管理员权限重建符号链接；或改用 `--strategy copy`                                              |
| 内部链接返回 404                            | 链接解析策略不匹配，或 OFM 插件未启用             | 确认使用 `obsidian` 模板，或在 yaml 中确认 `@quartz-community/obsidian-flavored-markdown` 已启用 |
| Vercel 除首页外全 404                      | 缺少 URL clean 配置                   | 添加 `vercel.json` 并设置 `"cleanUrls": true`（见 6.1 节）                                      |
| Front matter 解析失败                     | YAML 缩进或语法错误                      | 用 VSCode YAML 插件校验；注意冒号后必须有空格                                                          |
| GitHub Actions 报 environment 保护       | 旧环境残留冲突                           | 仓库 **Settings → Environments** 删除 `github-pages`，下次运行自动重建                              |
| `npx quartz sync` 推送失败                | upstream 变更未合并，或分支不对              | 确认当前分支是 `v5`；或手动 `git pull` 解决冲突后再 sync                                                |
| 首页显示 "Either this page is private or doesn't exist." | `content/` 目录下缺少 `index.md` 首页文件 | 在 Obsidian 仓库根目录创建一个 `index.md`（即名为 `index` 的笔记），Quartz 会用它作为 `/` 路径的首页 |

### Obsidian 与 Quartz 的兼容性

| Obsidian 语法                    | Quartz 支持 | 备注                                               |
| ------------------------------ | --------- | ------------------------------------------------ |
| `[[wikilink]]` 内部链接            | ✅ 是       | `obsidian-flavored-markdown` 插件（Obsidian 模板默认开启） |
| `![[embed]]` 嵌入                | ✅ 是       | 同上                                               |
| Callout `> [!note]`            | ✅ 是       | 同上                                               |
| Mermaid 图表 ` ```mermaid `      | ✅ 是       | OFM 插件 `parseMermaid: true`                      |
| 标签 `#tag`                      | ✅ 是       | OFM 插件 + tag-list / tag-page 插件                  |
| LaTeX 公式 `$...$`               | ✅ 是       | `latex` 插件（KaTeX 引擎）                             |
| Dataview ` ```dataview `       | ❌ 否       | 静态渲染时无法执行查询，需手动替换结果                              |
| Canvas（.canvas）                | ❌ 否       | 暂不支持                                             |
| Excalidraw                     | ❌ 否       | 需导出为图片再发布                                        |
| Properties（Obsidian 1.4+ 属性面板） | ✅ 是       | 等价于 Front Matter，原生兼容                            |

***

## 九、安全与隐私建议

1. **`.gitignore`** **配置**（Quartz 项目根目录）：

   ```
   # 构建产物与缓存
   public/
   .quartz-cache/

   # 社区插件（可忽略，CI 会安装；建议提交以便 lockfile 追踪）
   # .quartz/plugins/

   # Obsidian & Syncthing
   .obsidian/
   .stversions/
   .stfolder/
   *.sync-conflict-*

   # 敏感内容目录（建议在 .gitignore 和 ignorePatterns 双保险）
   attachments/
   private/
   templates/

   # 系统文件
   .DS_Store
   Thumbs.db
   desktop.ini
   ```

   > **注意**：`quartz.lock.json` **必须提交**到 Git，CI 上 `npx quartz plugin install` 依赖它锁定插件版本。

2. **敏感笔记隔离**：放入 `private/` 文件夹，同时在 `ignorePatterns`（Quartz 配置）和 `.gitignore` 两处都过滤，避免意外发布。

3. **Git 仓库可见性**：

   * GitHub Pages 发布功能：**Public** 仓库免费；**Private** 仓库需要 Pro 账户才能启用 Pages。

   * 如果代码要保持私有但公开 Pages：建议升级 GitHub Pro，或改用 Cloudflare Pages / Vercel / Netlify（免费版支持私有仓库）。

4. **Syncthing 加密**：启用 TLS 传输加密（默认已开启）。在不可信网络中，可额外配置「允许的网络」白名单。

5. **访问控制**：如需公开站点但部分页面私密，使用 `draft: true` 或把敏感笔记放在 `private/` 下（Quartz 不会构建）；不要依赖「未被链接就没人看到」的安全模型。

***

## 十、参考链接

* Obsidian: <https://obsidian.md>

* Syncthing: <https://syncthing.net>

* Syncthing 忽略规则文档: <https://docs.syncthing.net/users/ignoring.html>

* Quartz 官网 / 文档: <https://quartz.jzhao.xyz>

  * 安装指南: <https://quartz.jzhao.xyz/getting-started/installation>

  * `quartz create` CLI: <https://quartz.jzhao.xyz/cli/create>

  * 配置说明 (quartz.config.yaml): <https://quartz.jzhao.xyz/configuration>

  * 部署托管: <https://quartz.jzhao.xyz/hosting>

  * 故障排查: <https://quartz.jzhao.xyz/troubleshooting>

* Quartz GitHub: <https://github.com/jackyzha0/quartz>

* GitHub Pages: <https://pages.github.com>

* Vercel: <https://vercel.com>

* Cloudflare Pages: <https://pages.cloudflare.com>

* nvm-windows (Windows Node 版本管理): <https://github.com/coreybutler/nvm-windows>

* nvm (macOS/Linux Node 版本管理): <https://github.com/nvm-sh/nvm>

