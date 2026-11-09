/* quartz-ai 客户端：检索 + AI 问答面板
 * 依赖: 页面全局 fetchData (Quartz renderPage 注入的 contentIndex.json Promise)
 * 数据: static/ai-index.json (scripts/ai-index.mjs 生成)
 */
;(function () {
  if (window.__quartzAI) {
    window.__quartzAI.mount()
    return
  }

  var LS_CFG = "quartz-ai.cfg"
  var MAX_RESULTS = 8
  var ASK_CONTEXTS = 6
  var CTX_CHARS = 1200

  function readCfg() {
    try {
      return JSON.parse(localStorage.getItem(LS_CFG)) || {}
    } catch (e) {
      return {}
    }
  }

  var state = {
    cfg: readCfg(),
    prefix: null,   // 当前页到站点根的相对前缀，如 "../../"
    index: null,    // ai-index.json
    content: null,  // contentIndex.json
    docs: null,     // 检索用文档数组
    df: null,
    loaded: false,
    loading: null,
    controller: null,
  }

  /* ---------- 工具 ---------- */

  function el(tag, cls, text) {
    var node = document.createElement(tag)
    if (cls) node.className = cls
    if (text !== undefined) node.textContent = text
    return node
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
  }

  /**
   * 解析相对路径基准：
   *  - root: 当前页到站点根的前缀（如 "../../"），用于笔记链接
   *  - aiUrl / ciUrl: 站内索引文件地址
   * 依据是 Quartz 在每页注入的 `const fetchData = fetch("<相对路径>/static/contentIndex.json")`
   */
  function resolveBases() {
    if (state.bases) return state.bases
    var prefix = null
    var scripts = document.querySelectorAll("script")
    for (var i = 0; i < scripts.length; i++) {
      var m = (scripts[i].textContent || "").match(
        /fetch\(["']([^"']*contentIndex\.json)["']\)/,
      )
      if (m) {
        prefix = m[1].replace(/static\/contentIndex\.json$/, "")
        break
      }
    }
    if (prefix === null) prefix = "./"
    state.bases = {
      root: prefix,
      aiUrl: new URL(prefix + "static/ai-index.json", document.baseURI).toString(),
      ciUrl: new URL(prefix + "static/contentIndex.json", document.baseURI).toString(),
    }
    return state.bases
  }

  /* ---------- 数据加载与检索 ---------- */

  function ensureLoaded() {
    if (state.loaded) return Promise.resolve()
    if (state.loading) return state.loading
    state.loading = (function () {
      var bases = resolveBases()
      return Promise.all([
        fetch(bases.aiUrl).then(function (r) {
          if (!r.ok) throw new Error("INDEX_MISSING")
          return r.json()
        }),
        typeof fetchData !== "undefined"
          ? fetchData
          : fetch(bases.ciUrl).then(function (r) {
              return r.json()
            }),
      ]).then(function (res) {
        state.index = res[0]
        state.content = res[1]
        prepareDocs()
        state.loaded = true
      })
    })()
    return state.loading
  }

  function chunkText(c) {
    var entry = state.content[c.g]
    if (!entry) return ""
    return String(entry.content || "").slice(c.s, c.e)
  }

  function tokenize(s) {
    var tokens = []
    var lower = s.toLowerCase()
    var latin = lower.match(/[a-z0-9][a-z0-9+#.\-]*/g) || []
    for (var i = 0; i < latin.length; i++) tokens.push(latin[i])
    var cjk = lower.match(/[\u4e00-\u9fff\u3400-\u4dbf]+/g) || []
    for (var j = 0; j < cjk.length; j++) {
      var seg = cjk[j]
      if (seg.length < 2) {
        tokens.push(seg)
      } else {
        for (var k = 0; k < seg.length - 1; k++) tokens.push(seg.slice(k, k + 2))
      }
    }
    return tokens
  }

  function prepareDocs() {
    state.docs = state.index.chunks.map(function (c) {
      var note = state.index.notes[c.g] || {}
      return {
        slug: c.g,
        title: note.t || c.g,
        tags: note.g || [],
        url: note.u,
        text: chunkText(c),
        hash: c.h,
        tf: null,
      }
    })
    // 词频与文档频率
    var df = {}
    for (var i = 0; i < state.docs.length; i++) {
      var d = state.docs[i]
      var tf = {}
      var toks = tokenize(d.title + " " + d.text).concat(
        (d.tags || []).map(function (t) {
          return String(t).toLowerCase()
        }),
      )
      for (var j = 0; j < toks.length; j++) {
        tf[toks[j]] = (tf[toks[j]] || 0) + 1
      }
      d.tf = tf
      for (var key in tf) df[key] = (df[key] || 0) + 1
    }
    state.df = df
  }

  function search(query) {
    if (!state.docs || state.docs.length === 0) return []
    var qTokens = tokenize(query)
    if (qTokens.length === 0) return []
    var n = state.docs.length
    var scored = []
    for (var i = 0; i < n; i++) {
      var d = state.docs[i]
      var score = 0
      var hit = false
      for (var j = 0; j < qTokens.length; j++) {
        var t = qTokens[j]
        var f = d.tf[t]
        if (!f) continue
        hit = true
        var idf = Math.log(1 + n / (1 + (state.df[t] || 0)))
        score += (1 + Math.log(f)) * idf
        // 标题命中加权
        if (d.title.toLowerCase().indexOf(t) !== -1) score += idf * 0.8
      }
      if (hit) scored.push({ d: d, score: score })
    }
    scored.sort(function (a, b) {
      return b.score - a.score
    })
    return scored.slice(0, MAX_RESULTS)
  }

  function makeSnippet(d, query) {
    var text = d.text.replace(/\s+/g, " ")
    var qTokens = tokenize(query)
    var pos = -1
    for (var i = 0; i < qTokens.length && pos === -1; i++) {
      pos = text.toLowerCase().indexOf(qTokens[i])
    }
    if (pos === -1) return text.slice(0, 140)
    var start = Math.max(0, pos - 40)
    return (start > 0 ? "…" : "") + text.slice(start, start + 160) + "…"
  }

  /* ---------- UI ---------- */

  var ui = {}

  function mount() {
    var root = document.getElementById("quartz-ai-root")
    if (!root || root.childElementCount > 0) return

    ui.fab = el("button", "qa-fab", "AI")
    ui.fab.type = "button"
    ui.fab.title = "AI 搜索 / 问答"

    ui.panel = el("aside", "qa-panel")
    ui.panel.hidden = true

    var head = el("div", "qa-head")
    head.appendChild(el("span", "qa-title", "AI 搜索"))
    var setBtn = el("button", "qa-iconbtn", "设置")
    setBtn.type = "button"
    var closeBtn = el("button", "qa-iconbtn", "×")
    closeBtn.type = "button"
    head.appendChild(setBtn)
    head.appendChild(closeBtn)

    ui.answer = el("div", "qa-answer")
    ui.answer.hidden = true

    ui.form = el("form", "qa-form")
    ui.input = el("input", "qa-input")
    ui.input.type = "text"
    ui.input.placeholder = "在笔记中搜索，或提问…"
    var searchBtn = el("button", "qa-searchbtn", "搜索")
    searchBtn.type = "submit"
    ui.askBtn = el("button", "qa-askbtn", "AI 问答")
    ui.askBtn.type = "button"
    ui.form.appendChild(ui.input)
    ui.form.appendChild(searchBtn)
    ui.form.appendChild(ui.askBtn)

    ui.results = el("div", "qa-results")
    ui.status = el("div", "qa-status")
    ui.status.hidden = true

    ui.panel.appendChild(head)
    ui.panel.appendChild(ui.answer)
    ui.panel.appendChild(ui.form)
    ui.panel.appendChild(ui.results)
    ui.panel.appendChild(ui.status)

    ui.dialog = buildSettings()

    root.appendChild(ui.fab)
    root.appendChild(ui.panel)
    root.appendChild(ui.dialog)

    ui.fab.addEventListener("click", togglePanel)
    closeBtn.addEventListener("click", function () {
      ui.panel.hidden = true
    })
    setBtn.addEventListener("click", function () {
      ui.dialog.showModal()
    })
    ui.form.addEventListener("submit", function (e) {
      e.preventDefault()
      runSearch()
    })
    ui.askBtn.addEventListener("click", runAsk)

    // SPA 导航会重建 DOM，mount 可能重复执行，全局监听只绑一次
    if (!state.keyBound) {
      state.keyBound = true
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && ui.panel && !ui.panel.hidden) ui.panel.hidden = true
      })
    }
  }

  function buildSettings() {
    var dlg = el("dialog", "qa-settings")
    var wrap = el("div", "qa-set-body")

    wrap.appendChild(el("h3", null, "AI 问答设置"))

    var l1 = el("label", "qa-label", "API 地址（OpenAI 兼容）")
    var base = el("input", "qa-set-input")
    base.type = "text"
    base.placeholder = "https://api.deepseek.com/v1"
    base.value = state.cfg.base || ""

    var l2 = el("label", "qa-label", "API Key")
    var key = el("input", "qa-set-input")
    key.type = "password"
    key.placeholder = "sk-..."
    key.value = state.cfg.key || ""

    var l3 = el("label", "qa-label", "模型")
    var model = el("input", "qa-set-input")
    model.type = "text"
    model.placeholder = "deepseek-chat"
    model.value = state.cfg.model || ""

    var hint = el(
      "p",
      "qa-hint",
      "Key 仅保存在本浏览器 localStorage，请求由浏览器直连你填写的服务商。" +
        "需服务商允许浏览器跨域调用（DeepSeek / Kimi / 硅基流动等均可）。不配置也可使用纯检索。",
    )

    var save = el("button", "qa-save", "保存")
    save.type = "button"
    save.addEventListener("click", function () {
      state.cfg = {
        base: base.value.trim(),
        key: key.value.trim(),
        model: model.value.trim() || "deepseek-chat",
      }
      localStorage.setItem(LS_CFG, JSON.stringify(state.cfg))
      dlg.close()
    })

    wrap.appendChild(l1)
    wrap.appendChild(base)
    wrap.appendChild(l2)
    wrap.appendChild(key)
    wrap.appendChild(l3)
    wrap.appendChild(model)
    wrap.appendChild(hint)
    wrap.appendChild(save)
    dlg.appendChild(wrap)
    return dlg
  }

  function togglePanel() {
    ui.panel.hidden = !ui.panel.hidden
    if (!ui.panel.hidden) {
      setStatus("正在加载索引…")
      ensureLoaded()
        .then(function () {
          hideStatus()
          ui.input.focus()
        })
        .catch(function (err) {
          setStatus(
            err.message === "INDEX_MISSING"
              ? "未找到 AI 索引（static/ai-index.json）。请先运行: npm run build:site"
              : "索引加载失败: " + err.message,
          )
        })
    }
  }

  function setStatus(msg) {
    ui.status.textContent = msg
    ui.status.hidden = false
  }

  function hideStatus() {
    ui.status.hidden = true
  }

  /* ---------- 搜索 ---------- */

  function runSearch() {
    var q = ui.input.value.trim()
    ui.answer.hidden = true
    ui.results.innerHTML = ""
    if (!q) return
    var hits = search(q)
    if (hits.length === 0) {
      setStatus("没有找到与「" + q + "」相关的笔记片段")
      return
    }
    hideStatus()
    for (var i = 0; i < hits.length; i++) {
      var d = hits[i].d
      var a = el("a", "qa-item")
      a.href = new URL(d.url, resolveBases().root).toString()
      var t = el("div", "qa-item-title", d.title)
      var s = el("div", "qa-item-snippet", makeSnippet(d, q))
      a.appendChild(t)
      a.appendChild(s)
      ui.results.appendChild(a)
    }
  }

  /* ---------- AI 问答 ---------- */

  function stopAsk() {
    if (state.controller) {
      state.controller.abort()
      state.controller = null
      ui.askBtn.textContent = "AI 问答"
    }
  }

  function runAsk() {
    var q = ui.input.value.trim()
    if (!q) {
      setStatus("请先输入问题")
      return
    }
    if (!state.cfg.base || !state.cfg.key) {
      setStatus("未配置 AI 接口，请先点击右上角「设置」填写 API 地址与 Key")
      return
    }
    var hits = search(q)
    if (hits.length === 0) {
      setStatus("没有检索到相关笔记，无法回答")
      return
    }
    hideStatus()
    ui.results.innerHTML = ""
    renderContexts(hits)

    ui.answer.hidden = false
    ui.answer.innerHTML = ""
    ui.askBtn.textContent = "停止"
    var ctrl = new AbortController()
    state.controller = ctrl

    var contexts = []
    for (var i = 0; i < Math.min(ASK_CONTEXTS, hits.length); i++) {
      contexts.push({
        n: i + 1,
        title: hits[i].d.title,
        url: hits[i].d.url,
        text: hits[i].d.text.slice(0, CTX_CHARS),
      })
    }

    var sys =
      "你是一个个人知识库助手。请仅依据用户提供的编号资料回答问题，用简体中文，" +
      "回答准确、简洁。引用资料时在句末标注编号，如 [1]、[2]。如果资料不足以回答问题，请明确说明，不要编造。"
    var material = contexts
      .map(function (c) {
        return "[" + c.n + "] 标题: " + c.title + "\n" + c.text
      })
      .join("\n\n")

    state.lastCtxs = contexts

    streamChat(
      {
        model: state.cfg.model,
        messages: [
          { role: "system", content: sys },
          { role: "user", content: "资料：\n\n" + material + "\n\n问题：" + q },
        ],
        stream: true,
        temperature: 0.3,
      },
      ctrl.signal,
    )
      .then(function (full) {
        renderAnswer(full, contexts)
        state.controller = null
        ui.askBtn.textContent = "AI 问答"
      })
      .catch(function (err) {
        if (err.name === "AbortError") return
        ui.answer.innerHTML = ""
        ui.answer.appendChild(
          el(
            "div",
            "qa-error",
            "请求失败: " +
              err.message +
              "（请检查设置中的 API 地址/Key/模型，以及该服务商是否允许浏览器直连）",
          ),
        )
        state.controller = null
        ui.askBtn.textContent = "AI 问答"
      })
  }

  function renderContexts(hits) {
    var box = el("div", "qa-ctx")
    box.appendChild(el("div", "qa-ctx-title", "参考资料"))
    var n = Math.min(ASK_CONTEXTS, hits.length)
    for (var i = 0; i < n; i++) {
      var a = el("a", "qa-ctx-item", "[" + (i + 1) + "] " + hits[i].d.title)
      a.href = new URL(hits[i].d.url, resolveBases().root).toString()
      box.appendChild(a)
    }
    ui.results.appendChild(box)
  }

  function renderAnswer(text, contexts) {
    var html = escapeHtml(text).replace(/\[(\d+)\]/g, function (m, num) {
      var c = contexts[parseInt(num, 10) - 1]
      if (!c) return m
      var href = new URL(c.url, resolveBases().root).toString()
      return '<a class="qa-cite" href="' + href + '">[' + num + "]</a>"
    })
    var body = el("div", "qa-answer-body")
    body.innerHTML = html.replace(/\n/g, "<br>")
    ui.answer.innerHTML = ""
    ui.answer.appendChild(body)
  }

  function streamChat(body, signal) {
    var base = state.cfg.base.replace(/\/+$/, "")
    return fetch(base + "/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + state.cfg.key,
      },
      body: JSON.stringify(body),
      signal: signal,
    }).then(function (res) {
      if (!res.ok) {
        return res.text().then(function (t) {
          throw new Error("HTTP " + res.status + " " + t.slice(0, 200))
        })
      }
      var reader = res.body.getReader()
      var decoder = new TextDecoder()
      var buffer = ""
      var full = ""
      function pump() {
        return reader.read().then(function (r) {
          if (r.done) return full
          buffer += decoder.decode(r.value, { stream: true })
          var lines = buffer.split("\n")
          buffer = lines.pop()
          for (var i = 0; i < lines.length; i++) {
            var line = lines[i].trim()
            if (line.indexOf("data:") !== 0) continue
            var payload = line.slice(5).trim()
            if (payload === "[DONE]") return full
            try {
              var j = JSON.parse(payload)
              var delta =
                j.choices && j.choices[0] && j.choices[0].delta
                  ? j.choices[0].delta.content || ""
                  : ""
              if (delta) {
                full += delta
                renderAnswer(full, state.lastCtxs || [])
              }
            } catch (e) {
              /* 忽略不完整行 */
            }
          }
          return pump()
        })
      }
      return pump()
    })
  }

  /* ---------- 启动 ---------- */

  window.__quartzAI = {
    mount: mount,
    // 调试/测试入口（不影响正常使用）
    _debug: {
      state: state,
      tokenize: tokenize,
      prepareDocs: prepareDocs,
      search: search,
    },
  }

  mount()
  document.addEventListener("nav", function () {
    // SPA 导航后当前页深度变了，相对路径基准必须重算
    state.bases = null
    setTimeout(mount, 30)
  })
})()
