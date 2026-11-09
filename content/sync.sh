#!/usr/bin/env bash
# 知识库一键同步脚本
# 用法（任意终端）：git sync ["自定义提交信息"]
# 也可直接：bash sync.sh ["自定义提交信息"]
# 流程：暂存 -> 提交 -> 变基拉取 -> 推送
set -euo pipefail

cd "$(dirname "$0")"

msg="$*"
if [ -z "$msg" ]; then
  msg="feat(): note sync $(date '+%Y-%m-%d %H:%M:%S')"
fi

echo "==> [1/4] Staging all changes"
git add -A

echo "==> [2/4] Committing: $msg"
if git diff --cached --quiet; then
  echo "    No changes, skip commit"
else
  git diff --cached --stat
  git commit -m "$msg"
fi

echo "==> [3/4] Pull --rebase from origin/master"
git pull --rebase origin master

echo "==> [4/4] Pushing to origin/master"
git push origin master

echo "==> Done. Everything is up to date."
