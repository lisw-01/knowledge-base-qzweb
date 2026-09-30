---
title: Pi Agent 分析
date: 2026-09-30
tags:
  - Agent
  - 源码分析
  - 架构
description: Pi Agent 逐包源码级分析（类型、事件、Agent Loop、协议、扩展系统）与企业级定制落地实战
---

# Pi Agent 分析

> 核心一句话：**逐包拆开 Pi 的源码看它如何工程化「LLM + 工具 + 循环」，再落到企业级定制的三条路线（Skills / Extensions / SDK）**。
> 前置阅读：[[（1）Pi Agent简介]] ｜ 分层与调用链：[[（2）Pi Agent架构]] ｜ SDK 逐项示例：[pi-sdk-demo](pi-sdk-demo/README)

## 产品定位

pi 是一个 **agent harness** monorepo：既提供可直接使用的交互式编码代理 CLI（`pi` 命令），也提供可复用的 agent 运行时、统一 LLM API、终端 UI 框架。全部拆分为可独立发布的 npm 包（`@earendil-works/*`），采用 lockstep 版本策略统一发版。

> 包依赖图、三层分层、调用链路、数据流见 [[（2）Pi Agent架构]]，本篇按包逐个深入。

---

# 第一部分：逐包源码分析

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

# 第二部分：企业级定制落地

Pi 的三层定制能力，按投入成本从低到高：Skills（提示词层）→ Extensions（运行时层）→ SDK（进程内嵌层）。

## 1. 路线 1：Skills——把团队经验固化

Skill 是遵循开放 Agent Skills 标准的 Markdown 文件夹，描述"遇到某类任务该怎么做"。模型按需自动加载，不占常驻上下文。

```
.pi/skills/
  release-checklist/
    SKILL.md
  db-migration/
    SKILL.md
```

SKILL.md 示例：

```markdown
---
name: release-checklist
description: 发布前检查流程
---

# 发布检查清单
1. 跑全量测试：npm test
2. 检查 CHANGELOG 是否更新
3. 确认版本号已递增
4. 用 git diff --stat 复查改动范围
5. 打 tag 并推送
```

企业落地建议：把团队的发布流程、代码规范、排障手册、新人入职指南全部写成 Skills，沉淀在仓库的 .pi/ 目录随代码走，新成员克隆仓库即获得全部团队经验。

## 2. 路线 2：Extensions——自定义工具与拦截

用 TypeScript 写扩展，可以给 Agent 加自定义工具、修改运行时行为。

### 自定义工具示例

```typescript
import { createAgentSession } from '@earendil-works/pi-coding-agent';
import { Type } from '@sinclair/typebox';

const myTool = {
  name: 'query_ticket',
  description: '查询内部工单系统的工单详情',
  parameters: Type.Object({
    ticketId: Type.String({ description: '工单号' }),
  }),
  execute: async (_toolCallId, params) => {
    // 对接企业内部 API
    const res = await fetch(`https://tickets.internal/api/${params.ticketId}`, {
      headers: { Authorization: `Bearer ${process.env.TICKET_TOKEN}` },
    });
    const data = await res.json();
    return {
      content: [{ type: 'text', text: JSON.stringify(data) }],
      details: {},
    };
  },
};

const { session } = await createAgentSession({
  customTools: [myTool],
});
```

### 安全拦截（企业必备）

Pi 的 Agent 循环暴露了完整事件流钩子，可以在工具调用前做权限拦截：

```typescript
agent.subscribe((event) => {
  // 在每次工具调用前检查
  if (event.type === 'tool_call') {
    // 禁止危险命令
    if (event.toolName === 'bash' && /rm -rf|DROP TABLE/.test(event.input)) {
      throw new Error('危险操作已被企业策略拦截');
    }
    // 审计日志
    auditLog.write({
      user: currentUser,
      tool: event.toolName,
      input: event.input,
      timestamp: Date.now(),
    });
  }
});
```

⚠️ Pi 没有内置权限系统和沙箱，它以启动用户的完整权限运行。企业生产环境必须：要么容器化隔离（官方推荐），要么用上面的钩子自建拦截层。

### 会话压缩（长会话成本控制）

```typescript
// 主动压缩会话，保留关键信息丢弃冗余
const result = await session.compact('保留所有架构决策，丢弃中间调试过程');
```

## 3. 路线 3：SDK——进程内嵌完整 Agent

createAgentSession 在调用方进程内构建完整 Agent 会话，可注入自定义存储、配置、认证、模型注册表、资源加载器和工具——无桥接、无子进程、无 socket。

### 最小可用示例

```typescript
import {
  createAgentSession,
  ModelRuntime,
  SessionManager,
} from '@earendil-works/pi-coding-agent';

const modelRuntime = await ModelRuntime.create();

const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  modelRuntime,
});

// 订阅事件流，拿到逐字流式输出
session.subscribe((event) => {
  if (
    event.type === 'message_update' &&
    event.assistantMessageEvent.type === 'text_delta'
  ) {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await session.prompt('当前目录下有哪些文件？');
```

### AgentSession 核心能力

```typescript
interface AgentSession {
  // 发送 Prompt 并等待完成
  prompt(text: string, options?: PromptOptions): Promise<void>;

  // 流式传输期间插入指令（纠偏）
  steer(text: string): Promise<void>;

  // 后续问题排队
  followUp(text: string): Promise<void>;

  // 订阅事件流
  subscribe(listener: (event: AgentSessionEvent) => void): () => void;

  // 模型控制
  setModel(model: Model): Promise<void>;
  setThinkingLevel(level: ThinkingLevel): void;

  // 会话树导航（任意历史消息上分叉）
  navigateTree(targetId: string, options?: { ... }): Promise<...>;

  // 压缩长会话
  compact(customInstructions?: string): Promise<CompactionResult>;

  // 中断当前操作
  abort(): Promise<void>;
}
```

### 自定义全部注入项

```typescript
const { session } = await createAgentSession({
  model: myModel,                    // 锁定企业指定模型
  tools: ['read', 'bash'],           // 只开放部分工具（禁 write/edit）
  sessionManager: SessionManager.create(customDir),  // 会话持久化到企业指定位置
});
```

> SDK 全部 13 个能力维度（模型/提示词/技能/工具白名单/扩展/上下文文件/密钥/设置/会话/完全接管/运行时替换）各有一个可运行示例，见 [pi-sdk-demo](pi-sdk-demo/README)。

## 4. 企业级架构参考

一个基于 Pi 的企业级 Agent 整体架构：

```
+---------------------------------------------+
|  企业入口层                                   |
|  Web UI / 内部平台 / CI 流水线 / IM 机器人      |
+---------------------------------------------+
|  网关层（可选，参考 pi-gateway 模式）            |
|  认证鉴权 / 多渠道接入 / 路由                    |
+---------------------------------------------+
|  Pi Agent 层（SDK 内嵌 createAgentSession）     |
|  |- customTools：内部工单/Jenkins/监控查询       |
|  |- 事件钩子：审计日志 + 危险操作拦截            |
|  |- Skills：团队流程（发布/迁移/排障手册）        |
|  |- SessionManager：会话持久化（企业存储）        |
+---------------------------------------------+
|  模型层（pi-ai 统一接口）                       |
|  |- 云端：Claude / GPT / DeepSeek（按任务路由）  |
|  |- 本地：Ollama / llama.cpp（敏感数据不出域）    |
+---------------------------------------------+
|  执行环境层                                    |
|  容器隔离（Docker）/ 权限最小化 / 网络策略         |
+---------------------------------------------+
```

关键决策点：

1. 模型路由：敏感代码用本地模型，日常任务用云模型按成本/能力路由（pi-ai 层切换零成本）
2. 安全边界：Pi 无内置沙箱，必须在容器中运行，通过事件钩子做二次拦截
3. 会话资产：Pi 的会话是 JSONL 文件 + 树结构（类似 Git 分支），排查过程、重构脉络可回放共享，方便团队复盘
4. 上下文工程：AGENTS.md 写项目规则 + SYSTEM.md 定行为边界 + compact 控成本 + 按需加载 Skills

## 5. 成本与可观测性

- Pi 内置 Token 与成本追踪，界面底部实时显示当前模型、思考级别、token 消耗和费用估算
- SDK 模式下可通过事件流自建监控面板，按用户/项目/任务维度统计
- compact() 主动压缩长会话，避免上下文膨胀导致成本失控

---

# 第三部分：设计要点总结

1. **严格分层**：产品（coding-agent）→ 运行时（agent）→ AI 抽象（ai）→ 存储（sqlite-node），每层可独立发布
2. **LLM 边界统一**：`convertToLlm` + `StreamFn`，never-throw 流式契约把错误编码进事件流
3. **一切可插拔**：工具后端（Operations）、传输（ByteTransport）、session 存储、遥测、扩展系统
4. **扩展系统经 virtual modules** 获得与宿主一致的依赖视图
5. **单一 CBOR 协议**同时支撑交互 TUI 与 headless RPC 两种产品形态
