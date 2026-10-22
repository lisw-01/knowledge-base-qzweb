import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { h } from "preact"

const here = path.dirname(fileURLToPath(import.meta.url))
const clientJs = readFileSync(path.join(here, "..", "client.js"), "utf8")
const cssText = readFileSync(path.join(here, "..", "styles.css"), "utf8")

/**
 * AI 搜索/问答面板组件。
 * - 渲染一个挂载点 div，真正 UI 由 client.js 在浏览器端创建（便于 SPA 导航时重建）
 * - afterDOMLoaded / css 由 Quartz 构建管线打包进页面资源
 */
export function AIAsk(_opts) {
  return {
    name: "AIAsk",
    Component: () => h("div", { id: "quartz-ai-root" }),
    afterDOMLoaded: clientJs,
    css: cssText,
  }
}
