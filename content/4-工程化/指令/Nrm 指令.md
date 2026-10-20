# nrm 常用指令

> NPM Registry Manager——npm 镜像源管理工具。一条命令在多个 registry（官方源、淘宝源、公司私有源）之间切换，解决手动 `npm config set registry` 的麻烦。

***

## nrm 是什么

`npm config set registry <url>` 每次切换都要记长地址，nrm 把常用镜像源做成列表，一键切换、测速对比。

* 仓库：<https://github.com/Pana/nrm>

* 安装后全局可用，与 npm/yarn/pnpm 配合使用

***

## 安装

```bash
npm install -g nrm
```

> ⚠️ Node 17+ 若报错（ERR\_REQUIRE\_ESM 等），装新版：
>
> ```bash
> npm install -g nrm@latest
> ```

验证：

```bash
nrm --version
```

***

## 常用命令

### 查看镜像源列表

| 命令            | 说明                      |
| ------------- | ----------------------- |
| `nrm ls`      | 列出所有镜像源（当前使用的源带 `*` 标记） |
| `nrm current` | 显示当前使用的镜像源              |

`nrm ls` 输出示例：

```
  npm ---------- https://registry.npmjs.org/
  yarn --------- https://registry.yarnpkg.com/
  tencent ------ https://mirrors.cloud.tencent.com/npm/
* cnpm --------- https://r.cnpmjs.org/
  taobao ------- https://registry.npmmirror.com/
```

### 切换镜像源

| 命令               | 说明     |
| ---------------- | ------ |
| `nrm use taobao` | 切换到淘宝源 |
| `nrm use npm`    | 切回官方源  |

> 切换只影响 npm 的 registry 配置，等效于 `npm config set registry <url>`，但不用记地址。

### 测速对比

| 命令                | 说明              |
| ----------------- | --------------- |
| `nrm test`        | 测试所有镜像源的响应速度并排序 |
| `nrm test taobao` | 只测试指定源          |

输出示例：

```
* taobao ---- 120ms
  npm ------- 1850ms
  cnpm ------ 310ms
```

### 增删自定义镜像源

公司私有源 / 自建 Verdaccio 源需要手动添加：

| 命令                                                  | 说明       |
| --------------------------------------------------- | -------- |
| `nrm add <名称> <url>`                                | 添加镜像源    |
| `nrm add company http://registry.company.internal/` | 示例       |
| `nrm del <名称>`                                      | 删除自定义镜像源 |

### 登录管理（配合发布包）

| 命令                | 说明               |
| ----------------- | ---------------- |
| `nrm login <名称>`  | 在指定源登录（发布包到私有源前） |
| `nrm whoami <名称>` | 查看指定源的登录身份       |

***

## 使用场景

### 场景 1：国内安装依赖慢

```bash
nrm use taobao        # 切到淘宝源
npm install           # 速度明显提升

# 用完切回（发布包必须用官方源或已 login 的源）
nrm use npm
```

### 场景 2：公司私有 npm 源

```bash
# 添加公司源（运维提供的地址）
nrm add company http://npm.company.internal/

# 安装公司内部包时切换
nrm use company
npm install @company/utils
```

### 场景 3：发布自己的包

```bash
# ⚠️ 发布必须切回官方源（或已登录的源），淘宝源是只读镜像
nrm use npm
npm login
npm publish
```

### 场景 4：不确定哪个源快

```bash
nrm test              # 测速后选最快的
nrm use tencent
```

***

## 内置镜像源一览

| 名称        | 地址                                       | 说明                                   |
| --------- | ---------------------------------------- | ------------------------------------ |
| `npm`     | <https://registry.npmjs.org/>            | 官方源                                  |
| `taobao`  | <https://registry.npmmirror.com/>        | 淘宝源（原 registry.npm.taobao.org，国内最常用） |
| `tencent` | <https://mirrors.cloud.tencent.com/npm/> | 腾讯云源                                 |
| `cnpm`    | <https://r.cnpmjs.org/>                  | cnpm 源                               |
| `yarn`    | <https://registry.yarnpkg.com/>          | yarn 官方源                             |

> 淘宝旧地址 `registry.npm.taobao.org` 已于 2022 年停用，旧项目中的 `.npmrc` 需更新为 `https://registry.npmmirror.com`。

***

## 常见问题

### 切换了源但安装还是慢

检查项目根目录是否有 `.npmrc` 文件——**项目级配置优先级高于 nrm 的全局配置**，删掉或修改其中的 registry 即可。

### 发布包时报 401/403

* 确认 `nrm current` 是官方源或已 `nrm login` 的私有源

* 淘宝等镜像源**只读**，不能发布

### nrm 与 .npmrc 的关系

| 层级       | 位置                     | 优先级 |
| -------- | ---------------------- | --- |
| 项目级      | `<项目>/.npmrc`          | 最高  |
| 用户级      | `~/.npmrc`（nrm 改的就是这里） | 中   |
| nrm 内置默认 | 无                      | 低   |

> nrm 本质就是帮你改 `~/.npmrc` 中的 `registry` 字段，项目级 `.npmrc` 会覆盖它。

***

## 相关笔记

* \[\[Npm 指令]]

* \[\[Nvm 指令]]

