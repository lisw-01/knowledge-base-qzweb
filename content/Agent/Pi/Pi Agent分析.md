# Pi Monorepo 架构分析

## 产品定位

pi 是一个 **agent harness** monorepo：既提供可直接使用的交互式编码代理 CLI（`pi` 命令），也提供可复用的 agent 运行时、统一 LLM API、终端 UI 框架。全部拆分为可独立发布的 npm 包（`@earendil-works/*`），采用 lockstep 版本策略统一发版。

## 包依赖图

```
                telemetry (no deps)
               /       |
              v        v
   ai  <-----  agent  <-----  coding-agent
   |             |                |
   |             v                v
   +--->  protocol <-------  client
                                ^
                                |
                             server

   tui (standalone)  <-----  coding-agent
```

依赖流向：

- **telemetry** — 基础层，无依赖
- **ai** — 依赖 telemetry
- **agent** — 依赖 ai + telemetry（session 存储抽象内置于包内，sqlite-node 是其 Node 实现）
- **protocol** — 独立，仅依赖 typebox
- **client** — 依赖 protocol
- **server** — 依赖 agent（harness）+ protocol
- **tui** — 独立（依赖 marked 等）
- **coding-agent** — 顶层应用，依赖 agent、ai、client、protocol、tui
- **session-backends/sqlite-node** — agent 的 session 存储后端
- **evals** — 独立评测框架

---

## 1. AI 包（@earendil-works/pi-ai）

**定位**：统一 LLM API，自动模型发现与提供商配置。把 OpenAI、Anthropic、Google、Bedrock 等提供商的 SDK 差异屏蔽在一个共同的流式接口后面。

### 关键类型（`packages/ai/src/types.ts`）

```
Model<TApi>     -- id, name, api, provider, baseUrl, reasoning, cost, contextWindow, maxTokens,
                   thinkingLevelMap, input, samplingParams, headers, compat
Context         -- systemPrompt?, messages: Message[], tools?: Tool[]
Tool<TParams>   -- name, description, parameters (TSchema), constrainedSampling?
Message         -- UserMessage | AssistantMessage | ToolResultMessage

UserMessage       -- role: "user", content: string | (Text|Image)[], timestamp
AssistantMessage  -- role: "assistant", content: (Text|Thinking|ToolCall)[], api, provider, model,
                     usage, stopReason, errorMessage?, deferred?, timestamp
ToolResultMessage -- role: "toolResult", toolCallId, toolName, content, details?, usage?,
                     addedToolNames?, isError, timestamp

Usage           -- input, output, cacheRead, cacheWrite, reasoning?, totalTokens, cost{...}
StopReason      -- "pending" | "stop" | "length" | "toolUse" | "error" | "aborted" | "deferred"
ThinkingLevel   -- "minimal" | "low" | "medium" | "high" | "xhigh" | "max"
Transport       -- "sse" | "websocket" | "websocket-cached" | "auto"
```

### 提供商与 API 体系

- `KnownApi`（10 种 wire 格式）：`openai-completions`、`openai-responses`、`azure-openai-responses`、`openai-codex-responses`、`anthropic-messages`、`bedrock-converse-stream`、`google-generative-ai`、`google-vertex`、`mistral-conversations`、`pi-messages`
- `KnownProvider`（约 40 家）：anthropic、openai、google、amazon-bedrock、deepseek、xai、groq、cerebras、openrouter、zai、mistral、moonshotai、minimax、github-copilot、fireworks、together、huggingface、nvidia、cloudflare-workers-ai、vercel-ai-gateway、qwen-token-plan 系列、xiaomi-token-plan 系列等
- `OpenAICompletionsCompat`：为 OpenAI 兼容端点提供逐项能力开关（`supportsStore`、`supportsDeveloperRole`、`supportsReasoningEffort`、`supportsUsageInStreaming`、`supportsFinishReason`、`maxTokensField`、`requiresToolResultName`、`requiresAssistantAfterToolResult`），默认按 URL 自动探测

### 流式协议（AssistantMessageEvent）

```
{ type: "start", partial }                          -- 首事件，携带 partial AssistantMessage
{ type: "text_start/text_delta/text_end", contentIndex, ... }
{ type: "thinking_start/thinking_delta/thinking_end", contentIndex, ... }
{ type: "toolcall_start/toolcall_delta/toolcall_end", contentIndex, ... }
{ type: "done", reason: "stop"|"length"|"toolUse"|"deferred", message }
{ type: "error", reason: "aborted"|"error", error: AssistantMessage }
```

每个 delta 事件都携带最新的 `partial`（完整部分消息），消费方无需自己拼接状态。

### EventStream（`packages/ai/src/utils/event-stream.ts`）

通用 `EventStream<T, R>`：push 型异步可迭代 + `result()` Promise（resolve 为最终 R）。`AssistantMessageEventStream` 以 `done/error` 为完成条件，从终止事件提取最终 `AssistantMessage`。

### Provider 架构（`packages/ai/src/models.ts`）

- `Provider<TApi>`：id、name、baseUrl、auth 方法、模型列表、stream 行为
- `Models` 集合：对外暴露 `stream / complete / streamSimple / completeSimple / fetchDeferred / cancelDeferred`
- `ProviderStreams` 统一流契约：`stream()`、`streamSimple()`、可选 `fetchDeferred()/cancelDeferred()`
- **never-throw 契约**：`StreamFn` 一旦调用，请求/模型/运行时失败必须编码进返回流的 `error` 事件（stopReason 为 `"error"` 或 `"aborted"` + errorMessage），不允许同步抛出
- `api/lazy.ts`：`lazyApi(() => import(...))` 把每个 API 模块包成 `ProviderStreams`，首次调用才动态加载 SDK；`lazyStream` 同步返回流，setup 失败经 `error` 事件终止——懒加载与 never-throw 契约自洽
- `models.generated.ts`：脚本生成的模型目录（禁止手改，改 `scripts/generate-models.ts` 后再生成），含成本/上下文窗口/思考等级元数据
- 另有 images 子系统（`ImagesModel`、openrouter-images API）

---

## 2. Agent 包（@earendil-works/pi-agent-core）

**定位**：通用 agent 运行时——传输抽象、状态管理、工具执行。拥有核心 agent 循环、事件系统和工具编排。

### 关键类型（`packages/agent/src/types.ts`）

```
AgentState      -- systemPrompt, model, thinkingLevel, tools, messages, isStreaming,
                   streamingMessage, pendingToolCalls, errorMessage

AgentTool<TParams, TDetails> extends Tool<TParams>:
  label             -- UI 人类可读名
  prepareArguments? -- 原始参数兼容垫片
  execute(toolCallId, params, signal?, onUpdate?) -> AgentToolResult<TDetails>
  executionMode?    -- "sequential" | "parallel"

AgentToolResult<T>  -- content: (Text|Image)[], details: T, usage?, addedToolNames?, terminate?
AgentToolUpdateCallback<T> -- (partialResult) => void   -- 流式工具进度

AgentContext    -- systemPrompt, messages: AgentMessage[], tools?: AgentTool[]
AgentMessage    -- Message | CustomAgentMessages[keyof CustomAgentMessages]
                   （声明合并可扩展：扩展包可注入自定义消息类型）

StreamFn        -- (model, context, options?) => AssistantMessageEventStream
ToolExecutionMode -- "sequential" | "parallel"
QueueMode       -- "all" | "one-at-a-time"
ThinkingLevel   -- "off" | "minimal" | "low" | "medium" | "high" | "xhigh" | "max"
```

### AgentEvent 生命周期事件

```
{ type: "agent_start" }
{ type: "agent_end", messages }
{ type: "turn_start" }
{ type: "turn_end", message, toolResults }
{ type: "message_start", message }
{ type: "message_update", message, assistantMessageEvent }
{ type: "message_end", message }
{ type: "tool_execution_start", toolCallId, toolName, args }
{ type: "tool_execution_update", toolCallId, toolName, args, partialResult }
{ type: "tool_execution_end", toolCallId, toolName, result, isError }
```

### Agent 类（`packages/agent/src/agent.ts`）

有状态包装器，持有 transcript、模型、工具、系统提示词：

- `prompt(input)` — 新开一轮（string / messages / images）
- `continue()` — 从当前 transcript 继续
- `subscribe(listener)` — 订阅 AgentEvent（支持 AbortSignal）
- `steer(message)` / `followUp(message)` — 注入队列消息（`PendingMessageQueue` 支持 `all` / `one-at-a-time` 两种 drain 策略）
- `abort()` — 中断当前运行；`waitForIdle()` — 运行与监听器全部沉淀后 resolve
- 钩子：`beforeToolCall`、`afterToolCall`、`shouldStopAfterTurn`、`prepareNextTurn`
- `convertToLlm` — 在 LLM 调用边界把 `AgentMessage[]` 转为 `Message[]`（自定义消息在此折叠/展开）

### Agent Loop（`packages/agent/src/agent-loop.ts`）

双层 while 结构：

1. **外层循环**：agent 本应停止后处理 follow-up 消息（继续运行）
2. **内层循环**：处理 tool calls 与 steering 消息
   - 发 `turn_start`
   - 注入 pending 消息（steering / follow-up）
   - `streamAssistantResponse()`：`transformContext` → `convertToLlm` → 调 ai 层 stream → 逐事件发 `message_start/update/end`
   - 执行工具调用（sequential 或 parallel 模式）
   - 发 `turn_end` → 检查 `shouldStopAfterTurn` → 轮询 steering 队列

**工具执行四阶段**：

1. **Prepare**：校验参数，跑 `beforeToolCall` 钩子（可阻止/终止）
2. **Execute**：跑 `tool.execute()`，可选 `onUpdate` 流式进度
3. **Finalize**：跑 `afterToolCall` 钩子（可覆盖 content/details/isError/terminate）
4. 截断消息（stopReason `"length"`）→ `failToolCallsFromTruncatedMessage` 直接让所有 tool call 失败，而不是执行可能残缺的调用

### AgentHarness（`packages/agent/src/harness/agent-harness.ts`）

在基础 Agent 之上加：session 持久化、compaction（上下文压缩）、branch summarization（分支摘要）、多 lane（多写作 lane）、skill/template 管理。含类型化错误类（`LaneBusy`、`MissingIdentities`、`NoActiveRun` 等）与 outcome 类型（`RunOutcome`、`CompactionOutcome`、`NavigationOutcome`）。是 server 端运行时的底座。

---

## 3. Protocol 包（@earendil-works/pi-protocol）

**定位**：传输无关的 CBOR 协议，定义远程 pi 会话的 schema、帧与编解码。

### 线格式（`packages/protocol/src/framing.ts`）

长度前缀 CBOR 帧：**4 字节 big-endian uint32 长度头 + CBOR payload**。`encodeFrame()` 编码，`FrameDecoder` 增量解码（接受任意字节分块，吐出完整帧），带最大帧长校验。

### 核心 Schema（`packages/protocol/src/schemas.ts`）

```
PROTOCOL_VERSION = 1

-- Transcript Item（协议归一化的会话条目）--
UserTranscriptItem      -- id, role: "user", content: Text|Image[], timestamp
AssistantTranscriptItem -- id, role: "assistant", content: Text|Thinking|ToolCall[], model: ModelRef,
                          status: "streaming"|"complete"|"error"|"aborted", stopReason, usage?, timestamp
ToolTranscriptItem      -- id, role: "tool", toolCallId, toolName, input, content, details?, usage?,
                          status: "running"|"complete"|"error", isError, timestamp

-- 增量进度 --
TranscriptProgress:
  item_started     -- item: TranscriptItem
  assistant_delta  -- messageId, contentIndex, kind: "text"|"thinking"|"toolCall", delta
  item_updated     -- item (assistant 或 tool)
  item_finished    -- item (完成/出错/中止)

-- 会话状态 --
SessionSnapshot  -- id, name?, cwd, createdAt, updatedAt, phase, model, thinkingLevel,
                    attached, locked, revision, transcript, queuedSteer, queuedSteerCount
SessionPhase     -- "idle" | "turn" | "compaction" | "branch_summary" | "retry"

-- 服务端状态 --
ServerSnapshot   -- serverId, protocolVersion, revision, sessions, models

-- Client → Server 命令 --
Command: list | create | attach | detach | prompt | steer | abort | set_model | set_thinking

-- Server → Client --
ServerMessage: ServerHello | ServerHelloError | ResponseEnvelope | EventEnvelope
ServerEvent:   server_snapshot | session_snapshot | session_progress | session_removed
```

握手：client 先发 `{ type: "hello", version }`，server 回 `{ type: "hello", version, connectionId, snapshot }` 或 `{ type: "hello_error", error }`。

### Codec（`packages/protocol/src/codec.ts`）

- `encodeClientMessage` / `encodeServerMessage`：typebox `Check()` 校验 → CBOR 编码 → 帧封装
- `ClientMessageDecoder` / `ServerMessageDecoder`：增量解码（帧解码 + CBOR 解析 + schema 校验）
- `parseClientMessage` / `parseServerMessage`：单条消息校验解析，失败抛 `ProtocolValidationError`

---

## 4. Client 包（@earendil-works/pi-client）

**定位**：传输无关的远程会话客户端，跑在帧化 CBOR 字节流之上。

### ByteTransport（`packages/client/src/transport.ts`）

```
ByteTransport         -- send(chunk: Uint8Array), close()
ByteTransportHandlers -- onData, onClose, onError
ByteTransportFactory  -- (handlers) => ByteTransport | Promise<ByteTransport>
```

这是任意传输（Unix socket、WebSocket、stdio）的插入点。

### PiClient（`packages/client/src/client.ts`）

- `PiClient.connect(options)` — 工厂，建立连接 + 握手
- `createSession()` — 新建会话，返回带 **exclusive lease** 的 `PiSessionHandle`
- `attachSession(sessionId)` — 附着已有会话（shared lease）
- `acquireSession(sessionId, { mode })` — `"shared"` / `"exclusive"` 租约获取
- `listSessions()` — 列出可用会话
- 租约管理：exclusive/shared 租约、generation 失效、清理 reconciliation
- 请求跟踪：`PendingRequest` map + sequence id（`request-{id}` 信封），响应按 id 匹配 resolve
- `subscribe(listener)` 订阅 ServerSnapshot；`onEvent(listener)` 订阅 ServerEvent 流

### PiSessionHandle（`packages/client/src/session-handle.ts`）

```
id, active, attached, snapshot
subscribe(onSnapshot)      -- 快照更新
onEvent(listener)          -- 服务端事件
prompt(text)               -- 发 prompt，返回 SessionSnapshot
steer(text)                -- 运行中转向
abort()                    -- 中止当前 run
setModel(model) / setThinking(level)
detach() / dispose()       -- 释放会话
```

`connection.ts` 维护底层连接：打开、hello 握手、服务端消息解码、连接状态切换与断言、断开/失败关闭流程。

---

## 5. Server 包（@earendil-works/pi-server）

**定位**：接受字节级连接，经服务边界管理会话，分发协议命令。

### PiServer（`packages/server/src/server.ts`）

- 从 `PiServerListener`（如 Unix socket 监听器）接受 `ByteConnection`
- 握手：首条消息必须是 `hello`，校验协议版本，回 `ServerHello` 附带完整快照
- 握手后把 `RequestEnvelope` 命令分派给 `LiveSessionManager`
- 向 attached 连接广播会话快照与进度事件

### 服务边界（`packages/server/src/types.ts`）

```
PiServerService:
  listSessions() / listModels()
  createSession(options) -> PiSessionRuntime
  openSession(sessionId) -> PiSessionRuntime

PiSessionRuntime:
  snapshot() -> SessionSnapshot
  getPhase() -> SessionPhase
  prompt(input) / steer(input) / abort()
  setModel(model) / setThinking(level)
  subscribe(listener) -> unsubscribe
  dispose()
```

### LiveSessionManager（`packages/server/src/sessions.ts`）

- 会话获取：处理已存在 / opening / terminal / disposing 状态，从 service 创建 runtime 后注册 snapshot/progress 订阅
- 命令执行：`list/create/attach/detach/prompt/steer/abort/set_model/set_thinking` 全部分支
- 广播：runtime 事件触发 snapshot 广播给 attached 连接
- **自动 dispose**：零连接 + 零操作 + idle + 非 closing 的会话自动销毁

---

## 6. Coding-Agent 包（@earendil-works/pi-coding-agent）

**定位**：完整的编码代理应用——在基础 agent 上加编码工具、会话管理、compaction、扩展系统和 TUI。`bin.pi` → `dist/bundle/cli.js`。

### AgentSession（`packages/coding-agent/src/core/agent-session.ts`）

所有运行模式（interactive / print / json / rpc）共享的核心抽象：

- agent 状态访问与事件订阅，自动 session 持久化
- 模型与思考级别管理（含 cycling）
- **Compaction**：按 overflow/threshold 触发 → `session_before_compact` 扩展钩子 → 底层 `compact()` → 保存 compaction entry → `compaction_start/end`、`session_compact` 事件；`willRetry` 控制 overflow 后是否继续 turn
- 工具注册与激活（内置 + 扩展 + 自定义）
- 系统提示词构建（注入工具片段与 guidelines）
- bash 执行与环境注入；会话切换与分支

`AgentSessionEvent` 在核心 `AgentEvent` 基础上扩展：

```
agent_end { willRetry } | agent_settled | queue_update { steering, followUp } |
compaction_start/end | auto_retry_start/end | summarization_retry_* |
bash_execution_update | entry_appended | session_info_changed | thinking_level_changed
```

### AgentSessionRuntime（`packages/coding-agent/src/core/agent-session-runtime.ts`）

持有当前 AgentSession 与 cwd 绑定的服务。会话替换四路径：`newSession()`（新建）、`switchSession()`（resume）、`fork()`（按 entry 分支/克隆）、`importFromJsonl()`（导入 JSONL 再 resume）。均先触发 `session_before_switch` / `session_before_fork` 扩展钩子（可取消），再 teardown 当前会话。

### 工具系统（`packages/coding-agent/src/core/tools/`）

8 个内置工具，每个都有**双重工厂**：`createXxxTool()` 返回 AgentTool（给核心循环），`createXxxToolDefinition()` 返回 ToolDefinition（给扩展渲染/UI）：

| 工具 | Schema |
|---|---|
| read | `{ path, offset?, limit? }` |
| bash | `{ command, timeout? }` |
| powershell | `{ command, timeout? }` |
| edit | `{ path, edits: [{ oldText, newText }] }` |
| write | `{ path, content }` |
| grep | `{ pattern, path?, include? }` |
| find | `{ pattern, path? }` |
| ls | `{ path? }` |

每个工具有**可插拔 Operations 接口**（`ReadOperations`、`EditOperations`、`BashOperations`…，默认本地 `fs`/`spawn` 实现），支持远程委派（如 SSH）。工具分组：Coding 默认组（read/bash/edit/write）、只读组（read/grep/find/ls）。

### 扩展系统（`packages/coding-agent/src/core/extensions/`）

- `Extension` / `InlineExtension` / `ExtensionFactory` — 扩展定义形态
- `ExtensionRunner` — 发现、加载、运行扩展；loader 通过 **virtual modules** 注入 `pi-agent-core`、`pi-tui`、`pi-ai`、`pi-coding-agent` 等依赖，扩展无需自带 node_modules
- `ExtensionAPI` — 暴露给扩展的 API 面；`defineTool()` 定义扩展工具
- 可订阅事件：`session_start`、`session_shutdown`、`session_before_switch`、`session_before_fork`、`session_before_compact`、`session_compact`、`session_tree`、`agent_start`、`agent_end`、`tool_call`、`tool_result`、`turn_start`、`turn_end`、`message_start`、`message_end`、`before_agent_start`、`before_provider_request`、`input`、`context`
- 扩展可注册：工具、自定义命令/快捷键、CLI flags、UI 组件

### SDK 与运行模式

`createAgentSession()`（`packages/coding-agent/src/core/sdk.ts`）是程序化入口：装配模型运行时、工具、扩展、会话管理，并 `setDefaultStreamFn(streamSimple)` 接通 ai 层。`main.ts` 按 flag 分四种模式：

- **interactive** — 全 TUI + 会话管理
- **print**（`-p`）— 一次性 prompt，输出 stdout
- **json** — 结构化 JSON 输出
- **rpc** — stdio 上服务 protocol，供外部客户端

---

## 7. TUI 包（pi-tui）

**定位**：差分渲染的终端 UI 库，可独立使用。

### 核心（`packages/tui/src/tui.ts`）

```
Component  -- render(width) => string[], handleInput?(data), invalidate()
Focusable  -- 焦点组件契约，emit CURSOR_MARKER 支持硬件光标定位
TUI        -- 渲染循环、overlay、焦点、输入分发
Container  -- 子组件管理 + 焦点委托
TuiMainScreen / TuiAltScreen -- 主屏与 alt-screen（全屏）支持
```

**差分渲染**：比较当前帧与上一帧，只写变化的行。overlay 系统（`showOverlay()` → `OverlayHandle`，支持 hide/setHidden/focus/unfocus 与焦点恢复）。

### 组件清单（`packages/tui/src/components/`）

`Markdown`、`Text`、`TruncatedText`、`Box`、`Input`、`Editor`（分段、粘贴、光标、撤销、补全选择）、`SelectList`、`SettingsList`、`ScrollView`、`HStack`/`VStack`、`Image`、`Loader`/`CancellableLoader`、`Spacer`、`stack`。

### Markdown 渲染（`packages/tui/src/components/markdown.ts`）

- 基于 marked 解析器 + 自定义 LaTeX tokenizer 扩展
- 逐 token 处理 `heading/paragraph/text/latexBlock/code/list/table/blockquote/hr/html/space`
- 能力：标题、语法高亮代码块、列换行表格、带边框引用、嵌套列表、行内 Unicode LaTeX、块级 LaTeX、水平线、OSC 8 超链接、删除线；`MarkdownTheme` 提供 heading/link/code/codeBlock/quote 等样式函数
- **缓存**：按 text+width 缓存渲染结果，`setText()`/`invalidate()` 时失效

### 终端图片（terminal-image.ts）

探测终端能力（Kitty、iTerm2、Sixel），按支持的协议编码图片，计算 cell 尺寸做布局。

---

## 8. 支撑包

### session-backends/sqlite-node

agent-core sessions 的 Node SQLite 后端。表结构（`src/sqlite/migrations/001_initial.sql`）：`sessions`、`entries`、`session_sequences`、`session_stats`、`branch_entries`、`lanes`、`records`、`facts`、`branch_tips`、`writer_leases`。通过 writer lease + 事务队列控制并发写入，支持分支、多写者租约、FTS 全文搜索。`SqliteSessionStorage`（`src/sqlite/repo.ts`）实现 agent-core 的 session 存储接口。

### telemetry

`TelemetryContext`/`TelemetrySpan` 抽象（span 携带 attributes/events/status）+ 内存参考实现，供 ai/agent 层记录请求链路。

### evals

`src/pi-harness.ts` 创建隔离 workspace + agent session，执行 prompt 步骤，收集 transcript、token usage 与成本；支持 baseline/candidate 对比与 harness table 生成。

---

## 一次完整调用的数据流

```
用户输入 (TUI Editor / RPC client prompt)
  → AgentSession.prompt() ── 持久化 entry → SQLite 后端
  → Agent.prompt() → runAgentLoop
      outer loop (follow-up)
        inner loop:
          inject steering/follow-up 消息
          streamAssistantResponse: transformContext → convertToLlm → ai 层 streamSimple
            → Provider 解析（lazy 加载 SDK）→ 原生 API 调用
            ← AssistantMessageEvent 流（text/thinking/toolcall delta…）
          message_update → TUI 流式渲染 / RPC assistant_delta 转发
          tool calls → beforeToolCall → execute（可插拔 Operations）→ afterToolCall
          turn_end → shouldStopAfterTurn → steering 轮询
  → agent_end → waitForIdle → 会话快照广播（server 模式）
```

## 设计要点总结

1. **严格分层**：产品（coding-agent）→ 运行时（agent）→ AI 抽象（ai）→ 存储（sqlite-node），每层可独立发布
2. **LLM 边界统一**：`convertToLlm` + `StreamFn`，never-throw 流式契约把错误编码进事件流
3. **一切可插拔**：工具后端（Operations）、传输（ByteTransport）、session 存储、遥测、扩展系统
4. **扩展系统经 virtual modules** 获得与宿主一致的依赖视图
5. **单一 CBOR 协议**同时支撑交互 TUI 与 headless RPC 两种产品形态
