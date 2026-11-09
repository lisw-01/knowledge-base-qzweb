# Windows 最新可靠 Python3.11 安装方案（优先顺序：方案 1 > 方案 2 > 方案 3）

> 目标：**装好后自动配置 PATH、自带 pip、自带 Scripts 文件夹，装好直接 `python / py / pip` 命令可用，适合 LLM/Agent 开发**
> 

## 方案 1｜winget 一键安装【首推！最简单，不用下载任何文件】

Windows10 2020 后版本、Win11 自带 winget。自动配置环境变量，自带 pip，装好直接用。

1. 右键开始菜单 → **Windows PowerShell（管理员）**
2. 复制粘贴下面命令，回车

powershell

```
winget install Python.Python.3.11
```

3. 等待下载 + 自动安装，全程不用点下一步
4. **⚠️ 全部关闭所有终端窗口！重新打开 CMD/PowerShell 测试**

cmd

```
python --version
py --version
pip --version
```

> 正常输出版本号，成功！Scripts 文件夹自动生成。

> 如果提示 winget 不是命令：微软商店搜索「**应用安装程序**」安装。

### 必做额外一步（防止微软商店劫持 python 命令）

Win+i 设置 → 搜索 **应用执行别名**

把 `python.exe`、`python3.exe` 两个开关**关闭**

---

## 方案 2｜微软商店安装（备选，winget 失效时用）

1. 打开微软商店，搜索：`Python 3.11`，认准发布者：**Python Software Foundation**
2. 点安装
3. 安装完成，新开 CMD 测试

cmd

```
python --version
pip --version
```

✅ 商店版自动配置 PATH，自带 pip，开箱即用，非常稳定。

> 缺点：会自动后台更新 python 小版本；做学习 Agent 完全没问题。

---

## 方案 3｜官网 MSIX 安装包（官网现在主推，替代旧 exe 离线包）

> [python.org](https://python.org)新版不再提供传统 exe 离线包，换成 MSIX，和旧 exe 不一样，但能自动配置 PATH

1. 访问 [https://www.python.org/downloads/release/python-3119/](https://www.python.org/downloads/release/python-3119/)
2. 页面 Files 区域，下载：`Windows Installer (64-bit)`（后缀 MSIX）
3. 双击 MSIX 安装，一路下一步
4. 装好，关闭全部终端，新开 CMD 验证

cmd

```
python --version
pip --version
```


**MSIX 不是直接把 Python 文件夹写入 PATH。它靠 WindowsApps 的应用别名机制，让 `python` / `py` / `pip` 命令全局可用。正常安装成功，不用手动添加环境变量。但有前提，存在失败风险。**

## MSIX 原理

MSIX 安装的是【Python 安装管理器】，不是传统程序。

- 安装成功后：WindowsApps 里注册别名，终端直接识别`python`、`py`、`pip`，自带 pip、Scripts。
- 前提条件：系统 PATH 里面**必须保留** `%UserProfile%\AppData\Local\Microsoft\WindowsApps`（Windows 默认自带）。
- 如果这条被你删掉 → `python`命令直接失效，就会遇到你前面那种识别不到的情况。

## MSIX 的坑（重点，为什么我优先推荐 winget）

1. 如果你之前装过 MSI 版本 Python，残留配置冲突，MSIX 装好后**命令可能识别失败**。
2. 如果手动清理过 PATH，删掉 WindowsApps 那一行，直接失效。
3. 权限 / 杀毒软件拦截，别名注册失败，命令找不到。

> ⚠️ MSIX **不是 100% 稳**，有可能装好后命令无效，这时还是需要排查 PATH。

## winget / 微软商店版本（和 MSIX 底层一样，但更稳）

winget 安装的 Python，本质就是拉取同一份 MSIX 包，**自动处理注册**，出错概率更低。