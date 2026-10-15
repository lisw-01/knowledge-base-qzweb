# Linux 常用指令

> 按使用场景分类整理，`file` / `dir` / `src` / `dst` 为占位符，替换为实际文件/目录名。

***

## 文件与目录操作

### ls — 列出目录内容

| 命令 | 说明 |
|------|------|
| `ls` | 列出当前目录文件 |
| `ls -l` | 长格式（权限、大小、时间） |
| `ls -a` | 显示隐藏文件（含 `.` 开头） |
| `ls -lh` | 长格式 + 人类可读大小（K/M/G） |
| `ls -lt` | 按修改时间排序（新在前） |
| `ls -R` | 递归列出子目录 |
| `ll` | `ls -alF` 的别名（多数发行版自带） |

### cd — 切换目录

| 命令 | 说明 |
|------|------|
| `cd /path/to/dir` | 切换到指定目录 |
| `cd ~` 或 `cd` | 回到家目录 |
| `cd -` | 回到上一次所在目录 |
| `cd ..` | 回到上级目录 |
| `cd ../..` | 回到上两级目录 |

### pwd — 显示当前路径

```bash
pwd        # 打印当前工作目录的绝对路径
```

### mkdir — 创建目录

| 命令 | 说明 |
|------|------|
| `mkdir dir` | 创建目录 |
| `mkdir -p a/b/c` | 递归创建多级目录（已存在不报错） |

### cp — 复制

| 命令 | 说明 |
|------|------|
| `cp src dst` | 复制文件 |
| `cp -r dir1 dir2` | 递归复制目录 |
| `cp -i src dst` | 覆盖前确认 |
| `cp -u src dst` | 只在源比目标新时复制 |
| `cp -a src dst` | 归档复制（保留权限、时间戳等属性） |

### mv — 移动 / 重命名

| 命令 | 说明 |
|------|------|
| `mv src dst` | 移动文件或重命名 |
| `mv -i src dst` | 覆盖前确认 |
| `mv dir1 dir2` | 移动目录（无需 `-r`） |
| `mv a.txt b.txt` | 重命名 |

### touch — 创建空文件 / 更新时间戳

```bash
touch file          # 文件不存在则创建空文件，存在则更新修改时间
```

***

## 删除文件

| 命令 | 说明 |
|------|------|
| `rm file` | 删除文件，有提示 |
| `rm -f file` | 强制删文件，无提示 |
| `rm -i file` | 删除前逐个确认 |
| `rm -r dir` | 删除目录，会提示 |
| `rm -rf dir` | 强制递归删除目录，无提示 |

## 删除文件夹

| 命令 | 说明 |
|------|------|
| `rm -rf dir` | 强制删除文件夹（有内容也删） |
| `rm -ri dir` | 删除前交互确认 |
| `rmdir dir` | 仅删除空文件夹 |

## 清空当前目录下的所有文件

```bash
rm -rf ./*
```

> ⚠️ **高危操作**：执行前务必用 `pwd` 确认当前目录，`rm -rf` 无法恢复。

***

## 查看文件内容

| 命令 | 说明 |
|------|------|
| `cat file` | 输出全部内容 |
| `cat -n file` | 带行号输出 |
| `head -n 20 file` | 看前 20 行 |
| `tail -n 20 file` | 看后 20 行 |
| `tail -f file` | 实时追踪文件末尾（看日志必备） |
| `less file` | 分页浏览（`q` 退出，`/关键词` 搜索，`n` 下一个） |
| `wc -l file` | 统计行数 |

***

## 查找文件

| 命令 | 说明 |
|------|------|
| `find /path -name "*.log"` | 按名字查找 |
| `find /path -iname "*.Log"` | 忽略大小写查找 |
| `find /path -type d -name dir` | 只找目录 |
| `find /path -size +100M` | 找大于 100M 的文件 |
| `find /path -mtime -7` | 找 7 天内修改过的文件 |
| `find /path -name "*.tmp" -delete` | 找到并删除 |
| `locate file` | 从索引数据库快速查找（先 `updatedb`） |
| `which cmd` | 查命令的可执行文件位置 |
| `whereis cmd` | 查二进制、源码、手册位置 |

### grep — 文本搜索

| 命令 | 说明 |
|------|------|
| `grep "text" file` | 在文件中搜索 |
| `grep -i "text" file` | 忽略大小写 |
| `grep -r "text" dir/` | 递归搜索目录下所有文件 |
| `grep -n "text" file` | 显示行号 |
| `grep -v "text" file` | 反向匹配（排除含 text 的行） |
| `grep -c "text" file` | 只统计匹配行数 |
| `ps aux \| grep nginx` | 配合管道过滤进程 |

***

## 链接

| 命令 | 说明 |
|------|------|
| `ln -s target linkname` | 创建软链接（符号链接） |
| `ln target linkname` | 创建硬链接 |

> 软链接指向路径，可跨分区；硬链接指向 inode，不可跨分区、不能链接目录。

***

## 压缩与解压

| 命令 | 说明 |
|------|------|
| `unzip test.zip` | 解压 .zip 到当前目录 |
| `unzip test.zip -d dir/` | 解压 .zip 到指定目录 |
| `zip -r out.zip dir/` | 压缩目录为 .zip |
| `tar -czf out.tar.gz dir/` | 压缩为 .tar.gz |
| `tar -xzf out.tar.gz` | 解压 .tar.gz |
| `tar -xzf out.tar.gz -C dir/` | 解压到指定目录 |
| `tar -cjf out.tar.bz2 dir/` | 压缩为 .tar.bz2 |
| `tar -xjf out.tar.bz2` | 解压 .tar.bz2 |
| `tar -tf out.tar.gz` | 只查看压缩包内容，不解压 |

> 记忆技巧：`-c` create 压缩，`-x` extract 解压，`-z` gzip 格式，`-j` bzip2 格式，`-f` 指定文件名（必须放最后）。

***

## 用户与权限

### chmod — 修改权限

| 命令 | 说明 |
|------|------|
| `chmod +x file` | 给文件加执行权限 |
| `chmod 755 file` | rwxr-xr-x（所有者全权，其他人读+执行） |
| `chmod 644 file` | rw-r--r--（所有者读写，其他人只读） |
| `chmod -R 755 dir/` | 递归修改目录权限 |
| `chmod u+x file` | 只给所有者加执行权限 |

> 数字含义：`r=4, w=2, x=1`。`755 = 7(4+2+1) + 5(4+1) + 5(4+1)`。

### chown — 修改所有者

| 命令 | 说明 |
|------|------|
| `chown user file` | 改所有者 |
| `chown user:group file` | 改所有者和组 |
| `chown -R user:group dir/` | 递归修改 |

### 用户操作

| 命令 | 说明 |
|------|------|
| `whoami` | 当前用户名 |
| `sudo cmd` | 以 root 权限执行 |
| `su - user` | 切换用户 |
| `useradd user` | 创建用户 |
| `passwd user` | 改密码 |
| `userdel -r user` | 删除用户及家目录 |

***

## 进程管理

| 命令 | 说明 |
|------|------|
| `ps aux` | 查看所有进程 |
| `ps aux \| grep name` | 过滤指定进程 |
| `top` | 实时进程监控（`q` 退出） |
| `htop` | 增强版 top（需安装） |
| `kill pid` | 正常结束进程 |
| `kill -9 pid` | 强制杀死进程 |
| `killall name` | 按名字杀进程 |
| `jobs` | 查看后台任务 |
| `bg` / `fg` | 任务放后台 / 调回前台 |
| `nohup cmd &` | 后台运行且退出终端不中断 |

***

## 系统信息

| 命令 | 说明 |
|------|------|
| `uname -a` | 内核与系统信息 |
| `df -h` | 磁盘使用情况 |
| `du -sh dir/` | 目录总大小 |
| `du -h --max-depth=1` | 当前目录下各子目录大小 |
| `free -h` | 内存使用 |
| `uptime` | 运行时间与负载 |
| `cat /etc/os-release` | 发行版信息 |
| `date` | 当前时间 |

***

## 网络

| 命令 | 说明 |
|------|------|
| `ip addr` 或 `ifconfig` | 查看网卡与 IP |
| `ping host` | 测试连通性 |
| `curl url` | 发 HTTP 请求 |
| `curl -O url` | 下载文件 |
| `wget url` | 下载文件 |
| `netstat -tlnp` | 查看监听端口与进程 |
| `ss -tlnp` | 同上（更现代，替代 netstat） |
| `scp file user@host:/path/` | 远程复制到服务器 |
| `scp user@host:/path/file .` | 从服务器复制回来 |
| `ssh user@host` | 远程登录 |

***

## 软件包管理

### Debian / Ubuntu（apt）

| 命令 | 说明 |
|------|------|
| `apt update` | 更新软件源索引 |
| `apt install pkg` | 安装软件 |
| `apt remove pkg` | 卸载（保留配置） |
| `apt purge pkg` | 卸载（含配置） |
| `apt search keyword` | 搜索软件 |

### CentOS / RHEL（yum / dnf）

| 命令 | 说明 |
|------|------|
| `yum install pkg` | 安装软件 |
| `yum remove pkg` | 卸载软件 |
| `yum search keyword` | 搜索软件 |

***

## 管道与重定向

| 命令 | 说明 |
|------|------|
| `cmd1 \| cmd2` | 管道：cmd1 的输出作为 cmd2 的输入 |
| `cmd > file` | 输出重定向（覆盖） |
| `cmd >> file` | 输出重定向（追加） |
| `cmd 2> file` | 错误输出重定向 |
| `cmd &> file` | 标准输出+错误都重定向 |
| `cmd < file` | 输入重定向 |

***

## 快捷键与技巧

| 快捷键 | 说明 |
|--------|------|
| `Tab` | 自动补全（连按两次显示所有候选） |
| `Ctrl + C` | 终止当前命令 |
| `Ctrl + Z` | 挂起到后台 |
| `Ctrl + L` | 清屏 |
| `Ctrl + R` | 搜索历史命令 |
| `Ctrl + A` / `Ctrl + E` | 光标跳到行首 / 行尾 |
| `!!` | 上一条命令（`sudo !!` 补权限） |
| `history` | 查看历史命令 |
| `alias ll='ls -alF'` | 设置别名 |

***

## 相关笔记

- 原始笔记中的删除、解压部分已合并到本文档对应章节
