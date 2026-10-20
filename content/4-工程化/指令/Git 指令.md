# Git 常用指令

> 按使用场景分类整理，`file` / `branch` / `commit-id` / `remote` 为占位符，替换为实际值。

***

## 初始配置

| 命令 | 说明 |
|------|------|
| `git config --global user.name "名字"` | 设置用户名 |
| `git config --global user.email "邮箱"` | 设置邮箱 |
| `git config --global core.editor "vim"` | 设置默认编辑器 |
| `git config --global init.defaultBranch main` | 设置默认分支名 |
| `git config --list` | 查看所有配置 |
| `git config --global alias.st status` | 设置别名（`git st` = `git status`） |

***

## 仓库操作

| 命令 | 说明 |
|------|------|
| `git init` | 当前目录初始化为 Git 仓库 |
| `git init dir` | 在指定目录初始化 |
| `git clone url` | 克隆远程仓库 |
| `git clone url dir` | 克隆到指定目录 |
| `git clone -b branch url` | 克隆指定分支 |
| `git clone --depth 1 url` | 浅克隆（只拉最新一次提交，大仓库提速） |

***

## 基本操作（日常提交流程）

| 命令 | 说明 |
|------|------|
| `git status` | 查看工作区状态（最常用） |
| `git status -s` | 简短格式 |
| `git add file` | 添加指定文件到暂存区 |
| `git add .` | 添加当前目录所有变更 |
| `git add -u` | 添加已跟踪文件的修改（不含新文件） |
| `git restore file` | 撤销工作区修改（旧版 `git checkout -- file`） |
| `git restore --staged file` | 取消暂存（保留工作区修改） |
| `git commit -m "信息"` | 提交暂存区 |
| `git commit -am "信息"` | 添加已跟踪文件并提交（跳过 add） |
| `git commit --amend` | 修改最近一次提交（追加变更或改信息） |

> 日常流程：`git add .` → `git commit -m "信息"` → `git push`

***

## 查看历史与差异

| 命令 | 说明 |
|------|------|
| `git log` | 查看提交历史 |
| `git log --oneline` | 单行简洁格式 |
| `git log --oneline -5` | 最近 5 条 |
| `git log --graph --oneline` | 图形化显示分支（看合并结构） |
| `git log -p file` | 查看某文件的历史修改 |
| `git log --author="名字"` | 按作者过滤 |
| `git diff` | 工作区 vs 暂存区的差异 |
| `git diff --staged` | 暂存区 vs 最近提交的差异 |
| `git diff branch1 branch2` | 比较两个分支 |
| `git show commit-id` | 查看某次提交的详细内容 |
| `git blame file` | 逐行显示修改人与提交 |

***

## 撤销与回退

| 命令 | 说明 |
|------|------|
| `git restore file` | 丢弃工作区修改（未 add 的） |
| `git restore --staged file` | 取消暂存（已 add 未 commit 的） |
| `git reset --soft commit-id` | 回退提交，保留修改在暂存区 |
| `git reset --mixed commit-id` | 回退提交，保留修改在工作区（默认） |
| `git reset --hard commit-id` | 回退提交，**丢弃所有修改** ⚠️ 高危 |
| `git revert commit-id` | 生成一次反向提交（安全，适合已推送的） |
| `git checkout commit-id -- file` | 恢复某文件到指定提交的版本 |

> ⚠️ `reset --hard` 会丢弃未提交修改；对已推送的提交用 `revert`，不要用 `reset`。

***

## 分支操作

| 命令 | 说明 |
|------|------|
| `git branch` | 列出本地分支 |
| `git branch -a` | 列出所有分支（含远程） |
| `git branch name` | 创建分支 |
| `git branch -d name` | 删除分支（已合并才能删） |
| `git branch -D name` | 强制删除分支 ⚠️ |
| `git branch -m old new` | 重命名分支 |
| `git switch branch` | 切换分支（新版，替代 checkout） |
| `git switch -c name` | 创建并切换分支 |
| `git checkout branch` | 切换分支（传统方式） |
| `git checkout -b name` | 创建并切换（传统方式） |
| `git checkout -b name origin/name` | 基于远程分支创建本地分支 |
| `git merge branch` | 把指定分支合并到当前分支 |
| `git merge --abort` | 合并冲突时放弃合并 |
| `git rebase branch` | 变基（把当前分支的提交移到目标分支之后） |

> `merge` 保留分支历史，`rebase` 历史更线性。团队协作时遵循仓库的既定策略。

***

## 远程操作

| 命令 | 说明 |
|------|------|
| `git remote -v` | 查看远程仓库地址 |
| `git remote add origin url` | 添加远程仓库 |
| `git remote set-url origin url` | 修改远程仓库地址 |
| `git remote remove origin` | 移除远程仓库 |
| `git fetch` | 拉取远程更新（不合并） |
| `git fetch origin branch` | 拉取指定分支 |
| `git pull` | 拉取并合并（= fetch + merge） |
| `git pull --rebase` | 拉取并变基（避免多余 merge 提交） |
| `git push` | 推送当前分支 |
| `git push -u origin branch` | 首次推送并建立跟踪关系 |
| `git push origin branch` | 推送指定分支 |
| `git push origin --delete branch` | 删除远程分支 |
| `git push --force` | 强制推送 ⚠️ 会覆盖远程历史 |

> ⚠️ 永远不要对公共分支（main/master）使用 `--force`。

***

## 储藏（stash）

临时保存工作现场，切去干别的事再回来：

| 命令 | 说明 |
|------|------|
| `git stash` | 把当前修改存入储藏区 |
| `git stash save "说明"` | 带说明储藏 |
| `git stash list` | 查看储藏列表 |
| `git stash pop` | 恢复最近一次储藏并删除它 |
| `git stash apply` | 恢复最近一次储藏但保留它 |
| `git stash drop` | 删除最近一次储藏 |
| `git stash clear` | 清空所有储藏 |

***

## 标签（tag）

| 命令 | 说明 |
|------|------|
| `git tag` | 列出所有标签 |
| `git tag v1.0` | 打轻量标签 |
| `git tag -a v1.0 -m "发布说明"` | 打附注标签（推荐） |
| `git tag -d v1.0` | 删除本地标签 |
| `git push origin v1.0` | 推送标签到远程 |
| `git push origin --tags` | 推送所有标签 |
| `git checkout v1.0` | 切换到标签（查看历史版本） |

***

## 冲突解决

合并/变基遇到冲突时的流程：

```
1. git merge branch          # 提示 CONFLICT
2. 打开冲突文件，处理标记：
   <<<<<<< HEAD
   当前分支的内容
   =======
   传入分支的内容
   >>>>>>> branch
3. 编辑保留需要的内容，删除标记
4. git add file              # 标记冲突已解决
5. git commit                # 完成合并（rebase 时用 git rebase --continue）
```

放弃本次合并：`git merge --abort`（或 `git rebase --abort`）

***

## 其他常用

| 命令 | 说明 |
|------|------|
| `git ls-files` | 列出所有被跟踪的文件 |
| `git rm file` | 删除文件并暂存 |
| `git mv old new` | 重命名并暂存 |
| `git cherry-pick commit-id` | 把别的分支的某次提交复制到当前分支 |
| `git reflog` | 查看所有操作记录（误删分支/回退后悔时的救命稻草） |
| `git bisect start` | 二分法定位引入 bug 的提交 |
| `git clean -fd` | 删除所有未跟踪的文件和目录 ⚠️ |
| `git shortlog -sn` | 统计各作者提交数 |

> 💡 **误操作救星**：`git reflog` 记录了 HEAD 的每次移动，配合 `git reset --hard commit-id` 可以回到几乎任何状态。

***

## 常见场景速查

### 场景 1：提交信息写错了

```bash
git commit --amend -m "正确的信息"    # 未推送时
```

### 场景 2：想撤销最近一次提交（保留修改）

```bash
git reset --soft HEAD~1
```

### 场景 3：拉取时冲突，想以本地为准

```bash
git stash
git pull
git stash pop        # 或按需手动合并
```

### 场景 4：把误提交的文件移出追踪（保留本地）

```bash
git rm --cached file
echo "file" >> .gitignore
git commit -m "stop tracking file"
```

### 场景 5：分支删错了想恢复

```bash
git reflog                  # 找到删除前的 commit-id
git checkout -b branch commit-id
```
