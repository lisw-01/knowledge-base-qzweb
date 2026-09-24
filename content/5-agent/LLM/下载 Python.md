## 一、安装 Python

### Windows

1. 官网下载：[https://www.python.org/downloads/release/python-311/](https://www.python.org/downloads/release/python-311/)
    
    往下滑找到 Files → Windows Installer (64-bit)    
1. ⚠️ **安装界面一定要勾选：Add Python to PATH**（非常关键，不勾选 cmd 识别不到 python），  只有.exe才有。
2. 选择 Install Now 默认安装，或者自定义路径（记住安装位置）
3. 验证是否安装成功
    
    打开 `cmd`（Win+R，输入 cmd 回车）
    
    bash
    
    ```
    python --version
    pip --version
    ```
    
    输出版本号就成功；提示不是命令，就是没勾选 PATH。




## ！！ 新版官网页面改版，**老的 exe 离线包入口藏起来了**，而且新版本主推 MSI/MSIX，没有带勾选框的 exe。需要配置环境变量：

1. 找到 python 文件夹
    
    开始菜单搜索 `Python 3.11`，右键 → **打开文件所在位置**
    
    这是一个快捷方式，**再次右键这个快捷方式 → 属性**
    
    看【目标】，类似：

plaintext

```
C:\Users\张三\AppData\Local\Programs\Python\Python311\python.exe
```

提取两个路径（**只复制文件夹，不要 python.exe**）

- 主目录：`C:\Users\张三\AppData\Local\Programs\Python\Python311`
- Scripts 目录：`C:\Users\张三\AppData\Local\Programs\Python\Python311\Scripts`

2. Win+R，输入 `sysdm.cpl` →回车
    
3. 高级 → 右下角【环境变量】
    
4. 在**用户变量**列表找到 `Path`，选中，点【编辑】
    
5. 点【新建】，粘贴上面两行目录，两个都要加
    
6. 全部窗口点确定保存
    
7. 关闭微软商店 python 劫持（必做！）
    
    Win+i 设置 → 搜索：**应用执行别名**
    
    把 `python.exe`、`python3.exe` **关闭**
    
8. 关闭全部 CMD/PowerShell，新开 CMD 测试
    

cmd

```
python --version
pip --version
```


### Mac

1. 方案 1 官网下载 3.11 安装包；或者用 Homebrew

bash

```
brew install python@3.11
```

2. 打开终端验证

bash

```
python3 --version
pip3 --version
```

> Mac 默认 python 指向 python2，后面命令你要用 `python3` / `pip3`