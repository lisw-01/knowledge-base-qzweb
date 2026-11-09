#!/usr/bin/env bash
# 用 Quartz 把知识库内容构建成静态网站
# 用法：由 my-quartz/deploy/deploy.sh 自动调用；也可手动 bash build-site.sh
# 产物：../my-quartz/public
#
# 同步采用「差量覆盖」而不是整目录清空：只删除本次不再存在的旧文件（通常 0 个），
# 避免一次性删除上百个文件触发安全保护，也不会误删 Quartz 需要的目录。
set -euo pipefail

VAULT="$(cd "$(dirname "$0")" && pwd)"
SITE="$(dirname "$VAULT")/my-quartz"

if [ ! -d "$SITE/quartz" ]; then
  echo "ERROR: Quartz project not found at $SITE"
  exit 1
fi

echo "==> [1/2] Syncing notes into Quartz content/"
mkdir -p "$SITE/content"
PKG="$(mktemp)"
LIST="$PKG.list"
OLD="$PKG.old"
STALE_LIST="$PKG.stale"
trap 'rm -f "$PKG" "$LIST" "$OLD" "$STALE_LIST"' EXIT

cd "$VAULT"
tar -cf "$PKG" \
  --exclude='.git' \
  --exclude='.gitignore' \
  --exclude='.obsidian' \
  --exclude='.workbuddy' \
  --exclude='.wbapp_*' \
  --exclude='private' \
  --exclude='.gitkeep' \
  --exclude='build-site.sh' \
  --exclude='deploy.bat' \
  --exclude='sync.sh' \
  --exclude='sync.bat' \
  .

tar -tf "$PKG" | grep -v '/$' | sed 's#^\./##' | sort > "$LIST"
(cd "$SITE/content" && find . -type f -printf '%P\n' | sort) > "$OLD"

comm -23 "$OLD" "$LIST" > "$STALE_LIST"
STALE=$(grep -c . "$STALE_LIST" || true)

# 只要存在旧路径文件（笔记改名、目录重编号等），就把整个旧 content 目录
# mv 归档，再从全新空目录解包。全程零删除，不会触发批量删除保护；
# 归档目录同时充当历史快照，可随时手动清理。
if [ "$STALE" -gt 0 ]; then
  mkdir -p "$SITE/.build-archive"
  ARCHIVE="$SITE/.build-archive/content-$(date +%Y%m%d-%H%M%S)-$$"
  mv "$SITE/content" "$ARCHIVE"
  mkdir -p "$SITE/content"
  echo "    $STALE 个旧路径文件 -> 旧 content 整体归档：$ARCHIVE（零删除）"
fi

(cd "$SITE/content" && tar -xf "$PKG")
echo "    synced $(wc -l < "$LIST") files, stale $STALE handled"

echo "==> [2/2] Building static site"
cd "$SITE"
# Quartz 构建第一步会清空 output 目录。若 public/ 已有上百个文件，
# 一次性删除会触发批量删除保护。这里改为「重命名归档」：旧产物整体挪到
# 同盘符的 .build-archive/（纯 mv，零删除），Quartz 写入全新的 public/。
# 归档目录同时充当地历史版本快照，不需要时可手动删除。
if [ -d "$SITE/public" ]; then
  mkdir -p "$SITE/.build-archive"
  ARCHIVE="$SITE/.build-archive/public-$(date +%Y%m%d-%H%M%S)"
  mv "$SITE/public" "$ARCHIVE"
  echo "    旧产物已归档：$ARCHIVE"
fi
npx quartz build -o public

echo "==> Done. Output: $SITE/public"
