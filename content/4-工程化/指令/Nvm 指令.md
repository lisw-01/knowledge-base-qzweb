# nvm 常用指令

> Node Version Manager——Node.js 多版本管理工具。同一台机器上安装、切换多个 Node 版本。
>
> ⚠️ **Windows 用户注意**：nvm 原版只支持 macOS/Linux，Windows 需用 [nvm-windows](https://github.com/coreybutler/nvm-windows)（独立项目，命令基本一致）。

***

## 版本区分（重要）

| 工具 | 平台 | 仓库 |
|------|------|------|
| `nvm` | macOS / Linux | https://github.com/nvm-sh/nvm |
| `nvm-windows` | Windows | https://github.com/coreybutler/nvm-windows |

> 两者命令大体相同，但底层实现不同、配置不互通。本文标注了两者的差异点。

***

## 安装

### macOS / Linux

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 重开终端或执行
source ~/.bashrc   # 或 ~/.zshrc

# 验证
nvm --version
```

### Windows（nvm-windows）

1. 下载 [nvm-setup.exe](https://github.com/coreybutler/nvm-windows/releases)
2. 安装时**卸载已有的 Node.js**（避免路径冲突）
3. 验证：

```powershell
nvm version
```

***

## 常用命令

### 查看版本

| 命令 | 说明 |
|------|------|
| `nvm --version` | 查看 nvm 自身版本 |
| `nvm current` | 当前使用的 Node 版本 |
| `node -v` | 验证当前 Node 版本（切换后确认） |

### 安装 Node 版本

| 命令 | 说明 |
|------|------|
| `nvm install 22` | 安装 Node 22 的最新小版本 |
| `nvm install 22.11.0` | 安装指定精确版本 |
| `nvm install --lts` | 安装最新 LTS（长期支持）版本 |
| `nvm install latest` | 安装最新版 |

> 推荐使用 **LTS 版本**（偶数大版本号，如 20 / 22 / 24），生产项目更稳定。

### 查看已安装/可安装的版本

| 命令 | 说明 |
|------|------|
| `nvm ls` | 列出本地已安装的所有版本（当前版本带箭头） |
| `nvm ls-remote` | 列出远程所有可安装版本 |
| `nvm ls-remote --lts` | 只列 LTS 版本 |

Windows（nvm-windows）的差异：

| 命令 | 说明 |
|------|------|
| `nvm list available` | 列出远程可安装版本 |
| `nvm list` | 列出本地已安装版本 |

### 切换版本

| 命令 | 说明 |
|------|------|
| `nvm use 22` | 切换到 Node 22（当前 shell 生效） |
| `nvm use 22.11.0` | 切换到指定精确版本 |
| `nvm use --lts` | 切换到最新 LTS |
| `nvm use default` | 切换到默认版本（nvm 原版） |
| `nvm alias default 22` | 设置默认版本（新开终端自动用这个） |
| `nvm alias default` | 取消默认版本设置 |

> ⚠️ Windows 下切换版本需要**管理员权限**运行终端，否则报 `exit status 1` / 权限错误。

### 卸载版本

| 命令 | 说明 |
|------|------|
| `nvm uninstall 22.11.0` | 卸载指定版本 |

> 卸载前先 `nvm use` 切到其他版本，不能卸载当前正在使用的版本。

***

## 进阶用法

### 项目级自动切换（.nvmrc）

在项目根目录创建 `.nvmrc` 文件，写入项目所需的 Node 版本：

```
22.11.0
```

使用：

```bash
nvm use          # 自动读取 .nvmrc 并切换（nvm 原版）
```

> nvm-windows 不支持 `nvm use` 自动读 `.nvmrc`，需手动 `nvm use 22.11.0`。
>
> 可配合 [avn](https://github.com/wbyoung/avn) 等 shell 插件实现 cd 进目录自动切换。

### 一次性使用某版本运行命令

```bash
nvm exec 22 node app.js      # 用 Node 22 运行
nvm run 22 --version          # 用 Node 22 查询其版本
```

### 迁移全局包（切版本后重装全局工具）

```bash
nvm install 24 --reinstall-packages-from 22   # 装 24 并把 22 的全局包迁移过来
nvm install 24 --copy-packages-from 22        # 复制而不删除源版本的全局包
```

> ⚠️ nvm-windows **不支持**此命令，需手动记录全局包：`npm ls -g --depth=0` 后逐个重装。

### 查看某版本安装路径

| 命令 | 说明 |
|------|------|
| `nvm which 22` | 查看指定版本的安装路径 |
| `nvm root` | 查看 nvm 存放所有版本的目录 |

***

## nvm-windows 特有命令

| 命令 | 说明 |
|------|------|
| `nvm on` | 启用 node.js 版本管理 |
| `nvm off` | 禁用 node.js 版本管理 |
| `nvm proxy [url]` | 设置/查看下载代理 |
| `nvm arch [32\|64]` | 显示/切换架构 |

### 国内加速（nvm-windows）

设置 Node 下载镜像：

```powershell
nvm node_mirror https://npmmirror.com/mirrors/node/
nvm npm_mirror https://npmmirror.com/mirrors/npm/
```

### 国内加速（macOS/Linux nvm）

```bash
export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node
```

***

## 安装目录

| 平台 | 路径 |
|------|------|
| Windows | `C:\Users\<用户名>\AppData\Roaming\nvm`（各版本在 `C:\Program Files\nodejs` 通过 symlink 指向） |
| macOS / Linux | `~/.nvm/versions/node/v<版本号>` |

***

## 常见问题

### 切换后 node -v 没变化

- **Windows**：用**管理员权限**重开终端再 `nvm use`
- 确认没有其他 Node 安装（如官网安装包装的），卸载后重装 nvm

### nvm install 下载慢/失败

- Windows：设置国内镜像（见上）
- macOS/Linux：设置 `NVM_NODEJS_ORG_MIRROR` 环境变量

### 全局安装的包切换版本后不见了

nvm 的每个版本有**独立**的全局包目录，切换版本后需重装全局工具（或用 `--reinstall-packages-from` 迁移）。

### nvm 命令找不到（command not found）

- 检查 shell 配置文件（`~/.bashrc` / `~/.zshrc`）中是否有 nvm 初始化代码
- 重开终端或 `source` 配置文件

***

## 常见场景速查

### 场景 1：新项目要求 Node 22，本机是 18

```bash
nvm install 22
nvm use 22
node -v          # v22.x
```

### 场景 2：多个项目用不同 Node 版本

```bash
# 项目 A（Node 20）
cd project-a
echo "20.18.0" > .nvmrc
nvm use

# 项目 B（Node 22）
cd project-b
echo "22.11.0" > .nvmrc
nvm use
```

### 场景 3：升级 Node 并保留全局工具

```bash
nvm install 24 --reinstall-packages-from 22
nvm use 24
nvm alias default 24
```

***

## 相关笔记

- [[Npm 指令]]
- [[Linux 指令]]
- [[Git 指令]]
