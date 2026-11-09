#!/usr/bin/env node
/**
 * ai-index.mjs — AI 检索索引生成器（post-build，独立于 Quartz 核心）
 *
 * 输入:  public/static/contentIndex.json   (Quartz 构建产物，已过滤 private/草稿/加密)
 * 输出:  public/static/ai-index.json       (分块引用索引，chunks 指向 contentIndex 的 [s,e) 区间)
 *
 * 设计原则:
 *  - 只读 contentIndex.json，不解析 markdown、不触碰 quartz 内部模块
 *  - 每个 chunk 带 sha1 hash，为将来接入 embedding 向量检索预留增量缓存键
 *  - 索引是构建产物的派生品：笔记变更 -> 重新 build -> 索引自动同步
 */
import { readFileSync, writeFileSync, existsSync, statSync } from "node:fs"
import { createHash } from "node:crypto"
import path from "node:path"
import { parse as parseYaml } from "yaml"
import { slugifyFilePath } from "@quartz-community/utils"

const ROOT = process.cwd()
const SRC = path.join(ROOT, "public", "static", "contentIndex.json")
const OUT = path.join(ROOT, "public", "static", "ai-index.json")

const CHUNK_SIZE = 600   // 单块目标长度（字符）
const OVERLAP = 120      // 相邻块重叠
const MIN_LEN = 24       // 低于此长度的块丢弃
const SENT_SPLIT = /(?<=[。！？!?；;])/ // 长段落按句子切分

function chunkRanges(text) {
  const paras = []
  const re = /[^\n]+/g
  let m
  while ((m = re.exec(text)) !== null) {
    if (m[0].trim().length > 0) paras.push({ s: m.index, e: m.index + m[0].length, t: m[0].trim() })
  }

  // 展开为"单元"（短段落原样，长段落按句子拆）
  const units = []
  for (const p of paras) {
    if (p.t.length <= CHUNK_SIZE) {
      units.push(p)
      continue
    }
    let off = p.s
    for (const sent of p.t.split(SENT_SPLIT)) {
      if (sent.length === 0) continue
      units.push({ s: off, e: off + sent.length, t: sent })
      off += sent.length
    }
  }

  // 打包成块，块间带尾部重叠
  const ranges = []
  let cur = null
  for (const u of units) {
    const uLen = u.e - u.s
    if (!cur) {
      cur = { s: u.s, e: u.e, len: uLen }
      continue
    }
    if (cur.len + 1 + uLen > CHUNK_SIZE) {
      ranges.push({ s: cur.s, e: cur.e })
      const os = Math.max(cur.s, cur.e - OVERLAP)
      cur = { s: os, e: u.e, len: u.e - os }
    } else {
      cur.e = u.e
      cur.len = cur.e - cur.s
    }
  }
  if (cur) ranges.push({ s: cur.s, e: cur.e })
  return ranges.filter((r) => r.e - r.s >= MIN_LEN)
}

function resolvePathRoot() {
  const cfgPath = path.join(ROOT, "quartz.config.yaml")
  if (!existsSync(cfgPath)) return ""
  try {
    const cfg = parseYaml(readFileSync(cfgPath, "utf8"))
    const baseUrl = cfg?.configuration?.baseUrl
    if (!baseUrl) return ""
    const pathPart = String(baseUrl).split("/").slice(1).join("/") // 去掉域名部分
    return pathPart ? `/${pathPart.replace(/\/+$/, "")}` : ""
  } catch {
    return ""
  }
}

function main() {
  if (!existsSync(SRC)) {
    console.error(`[ai-index] 未找到 ${SRC}，请先运行 npx quartz build`)
    process.exit(1)
  }
  const index = JSON.parse(readFileSync(SRC, "utf8"))
  const notes = {}
  const chunks = []

  for (const [slug, entry] of Object.entries(index)) {
    const content = String(entry.content || "")
    const title = String(entry.title || slug)
    const tags = Array.isArray(entry.tags) ? entry.tags : []

    // 复用 Quartz 官方的 slugify 规则，保证与产出文件名完全一致
    const urlPath = slug === "index" ? "" : `${slugifyFilePath(slug + ".md")}.html`
    notes[slug] = { t: title, g: tags, u: urlPath }

    for (const r of chunkRanges(content)) {
      const text = content.slice(r.s, r.e)
      const h = createHash("sha1").update(text).digest("hex").slice(0, 16)
      chunks.push({ g: slug, s: r.s, e: r.e, h })
    }
  }

  const out = {
    version: 1,
    model: "kw-v1", // 检索模式标识；接入向量后形如 "bge-small-zh-v1.5@int8"
    generatedAt: new Date().toISOString(),
    chunkSize: CHUNK_SIZE,
    overlap: OVERLAP,
    notes,
    chunks,
  }

  writeFileSync(OUT, JSON.stringify(out))
  const kb = (Buffer.byteLength(JSON.stringify(out)) / 1024).toFixed(0)
  console.log(
    `[ai-index] ${Object.keys(notes).length} 篇笔记 -> ${chunks.length} 个分块 -> ${OUT} (${kb} KB)`,
  )
}

main()

// --watch: 本地开发用，轮询 contentIndex.json 变化后重建（避免文件被重建时 fs.watch 失效）
if (process.argv.includes("--watch")) {
  const stamp = () => {
    try {
      const s = statSync(SRC)
      return `${s.mtimeMs}:${s.size}`
    } catch {
      return ""
    }
  }
  let last = stamp()
  console.log("[ai-index] watch 模式启动，监听 contentIndex.json …")
  setInterval(() => {
    const cur = stamp()
    if (cur && cur !== last) {
      last = cur
      try {
        main()
      } catch (e) {
        console.error(`[ai-index] 重建失败: ${e.message}`)
      }
    }
  }, 1000)
}
