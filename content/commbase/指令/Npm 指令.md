# npm 常用指令

> 按使用场景分类整理。`pkg` 为包名占位符，替换为实际包名。

***

## 初始化项目

| 命令                     | 说明                                         |
| ---------------------- | ------------------------------------------ |
| `npm init`             | 交互式创建 package.json                         |
| `npm init -y`          | 跳过提问，快速创建默认 package.json                   |
| `npm init vite@latest` | 用 create-xxx 脚手架创建项目（如 vite / react / vue） |

***

## 安装依赖

| 命令                                    | 说明                                                 |
| ------------------------------------- | -------------------------------------------------- |
| `npm install` 或 `npm i`               | 安装 package.json 中所有依赖                              |
| `npm install pkg`                     | 安装包并写入 dependencies                                |
| `npm install -D pkg`                  | 安装开发依赖（devDependencies）                            |
| `npm install -g pkg`                  | 全局安装                                               |
| `npm install pkg@1.2.3`               | 安装指定版本                                             |
| `npm install pkg@latest`              | 安装最新版                                              |
| `npm install --save-exact pkg` 或 `-E` | 精确锁定版本（写入 package.json 不带 `^`）                     |
| `npm ci`                              | 按 package-lock.json **精确还原**安装（CI / 新机器拉项目用，更快更严格） |
| `npm install --legacy-peer-deps`      | 忽略 peerDependencies 冲突                             |
| `npm install --ignore-scripts`        | 跳过依赖的生命周期脚本（供应链安全加固）                               |

> ⚠️ `npm install` vs `npm ci`：`install` 可能更新 lockfile，`ci` 严格按 lockfile 安装且要求 lockfile 与 package.json 一致，CI 环境必用 `ci`。

***

## 卸载与更新

| 命令                      | 说明                    |
| ----------------------- | --------------------- |
| `npm uninstall pkg`     | 卸载包并从 package.json 移除 |
| `npm uninstall -g pkg`  | 卸载全局包                 |
| `npm update`            | 更新所有依赖（在 semver 范围内）  |
| `npm update pkg`        | 更新指定包                 |
| `npm outdated`          | 列出过期的依赖               |
| `npm ls` 或 `npm ls pkg` | 查看依赖树                 |
| `npm ls -g --depth=0`   | 列出全局安装的包              |
| `npm dedupe`            | 去重依赖树，减少重复包           |

***

## 运行脚本

| 命令                      | 说明                      |
| ----------------------- | ----------------------- |
| `npm run`               | 列出 package.json 中所有可用脚本 |
| `npm run dev`           | 运行 dev 脚本               |
| `npm run build`         | 运行 build 脚本             |
| `npm test` 或 `npm t`    | 运行 test 脚本的简写           |
| `npm start`             | 运行 start 脚本的简写          |
| `npm run dev -- --host` | 向脚本传递参数（`--` 后接参数）      |

package.json 中的 scripts 示例：

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run",
    "check": "npm run lint && npm run test"
  }
}
```

***

## 查看包信息

| 命令                          | 说明               |
| --------------------------- | ---------------- |
| `npm search 关键词`            | 搜索包              |
| `npm view pkg`              | 查看包的详细信息（版本、依赖等） |
| `npm view pkg versions`     | 查看包的所有历史版本       |
| `npm view pkg version`      | 查看包的最新版本号        |
| `npm view pkg dependencies` | 查看包的依赖           |
| `npm info pkg`              | 同 `npm view`     |
| `npm owner ls pkg`          | 查看包的维护者          |

***

## 发布与管理包

| 命令                             | 说明                       |
| ------------------------------ | ------------------------ |
| `npm whoami`                   | 查看当前登录的 npm 账号           |
| `npm login`                    | 登录 npm 账号                |
| `npm logout`                   | 退出登录                     |
| `npm publish`                  | 发布包到 npm 仓库              |
| `npm publish --access public`  | 发布 scoped 包（@xxx/yyy）为公开 |
| `npm version patch`            | 版本号 +0.0.1 并打 git tag    |
| `npm version minor`            | 版本号 +0.1.0               |
| `npm version major`            | 版本号 +1.0.0               |
| `npm deprecate pkg@1.0.0 "说明"` | 标记某版本已废弃                 |
| `npm unpublish pkg@1.0.0`      | 撤销发布（72 小时内）             |

***

## 缓存与清理

| 命令                        | 说明                                                        |
| ------------------------- | --------------------------------------------------------- |
| `npm cache verify`        | 校验缓存完整性                                                   |
| `npm cache clean --force` | 清空 npm 缓存                                                 |
| `npm cache ls`            | 列出缓存内容                                                    |
| `npm cache`               | 缓存目录位置：Windows 在 `C:\Users\<用户名>\AppData\Local\npm-cache` |
| `npm prune`               | 删除 package.json 中未列出的多余包                                  |

> 依赖装坏了排查三板斧：删 `node_modules` → 删 `package-lock.json` → `npm cache clean --force` → 重新 `npm install`。

***

## 配置与镜像源

| 命令                              | 说明      |
| ------------------------------- | ------- |
| `npm config list`               | 查看当前配置  |
| `npm config get registry`       | 查看当前镜像源 |
| `npm config set registry <url>` | 切换镜像源   |
| `npm config delete key`         | 删除某项配置  |

国内常用镜像源：

```bash
# 淘宝镜像（国内加速，最常用）
npm config set registry https://registry.npmmirror.com

# 恢复官方源
npm config set registry https://registry.npmjs.org
```

项目级镜像源：在项目根目录创建 `.npmrc` 文件：

```
registry=https://registry.npmmirror.com
```

***

## npx — 执行包命令

### npm 与 npx 的区别

| 维度 | npm | npx |
|------|-----|-----|
| 本质 | 包**管理**器：安装、卸载、更新、发布包 | 包**执行**器：直接运行包里的命令（npm 5.2+ 自带） |
| 是否写入项目依赖 | 会写入 package.json | 不写入，用完即走 |
| 本地没装该包时 | 报错 | **临时下载到缓存执行**，不装进项目 |

> 💡 **核心记忆点**：`npx` 优先找**本地 node_modules**，找不到才临时下载执行——所以项目里装过的工具用 `npx` 调用永远是本地版本，比全局命令更安全（避免版本不一致）。

**典型例子**——脚手架等只用一次的工具：

```bash
# 老方法：全局装一次，以后一直占着
npm install -g create-vite
create-vite my-app

# npx 方法：临时执行，不留痕迹
npx create-vite my-app
```

**使用建议**：

| 场景 | 用哪个 |
|------|-------|
| 脚手架、只用一次的工具（create-vite、degit） | `npx` |
| 项目长期依赖（vite、eslint、typescript） | `npm install -D` |
| 执行 package.json 里的 scripts | `npm run dev` |

### 常用命令

| 命令                            | 说明                |
| ----------------------------- | ----------------- |
| `npx pkg`                     | 执行包的命令，未安装则临时下载运行 |
| `npx create-react-app my-app` | 典型用法：脚手架创建项目      |
| `npx --yes pkg`               | 跳过"是否安装"确认        |
| `npx --no-install pkg`        | 本地没有就不下载，直接报错     |

***

## 安全审计

| 命令                      | 说明                 |
| ----------------------- | ------------------ |
| `npm audit`             | 检查依赖中的安全漏洞         |
| `npm audit fix`         | 自动修复可修复的漏洞         |
| `npm audit fix --force` | 强制修复（可能引入破坏性变更 ⚠️） |
| `npm fund`              | 查看依赖的资助信息          |

***

## 常见场景速查

### 场景 1：接手一个新项目

```bash
npm ci          # 按 lockfile 精确还原依赖
```

### 场景 2：删除 node\_modules 重装

```powershell
# Windows PowerShell
Remove-Item -Recurse -Force node_modules
npm install
```

```bash
# macOS / Linux
rm -rf node_modules
npm install
```

### 场景 3：查看包为什么被安装

```bash
npm ls pkg           # 查看依赖链
npm why pkg          # 同上（别名）
```

### 场景 4：全局安装的命令找不到

```bash
npm ls -g --depth=0          # 确认已安装
npm bin -g                   # 查看全局 bin 目录是否在 PATH 中
```

### 场景 5：锁定依赖给同事/CI 用

```bash
# 提交 package.json + package-lock.json 到 Git
# 其他人克隆后：
npm ci
```

***

## package.json 依赖版本号说明

| 符号            | 含义                 | 示例             |
| ------------- | ------------------ | -------------- |
| `^1.2.3`      | 允许小版本和补丁更新（默认）     | 1.2.3 \~ 1.x.x |
| `~1.2.3`      | 只允许补丁更新            | 1.2.3 \~ 1.2.x |
| `1.2.3`       | 精确锁定此版本            | 仅 1.2.3        |
| `>=1.2.0`     | 大于等于此版本            | 1.2.0 及以上      |
| `*`           | 任意版本               | 全部             |
| `workspace:*` | monorepo 中指向本地工作区包 | 本地链接           |

***

## 相关笔记

* \[\[Linux 指令]]

* \[\[Git 指令]]

