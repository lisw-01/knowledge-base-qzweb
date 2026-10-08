---
title: 2-Pi Agent架构
date: 2026-09-30
tags:
  - Agent
  - 架构
description: Pi Agent 的分层架构：核心三层包、调用链路、Remote CBOR 远程会话栈与运行模式
---

# Pi Agent 架构

> 核心一句话：**Pi = 严格单向分层的 monorepo——「模型适配层 pi-ai → Agent 内核 pi-agent-core → 产品组装层 pi-coding-agent → 终端 UI pi-tui」，外加一套可选的 CBOR 远程会话栈（pi-protocol / pi-client / pi-server）**。下层不知道上层，每层可独立发布使用。
> 前置阅读：[[1-Pi Agent简介]] ｜ 源码细节：[[3-Pi Agent分析]]

## 一、全景：包依赖图

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
- **agent**（即 pi-agent-core）— 依赖 ai + telemetry
- **protocol** — 独立，仅依赖 typebox
- **client** — 依赖 protocol
- **server** — 依赖 agent（harness）+ protocol
- **tui** — 独立（依赖 marked 等），不直接 import pi-agent-core
- **coding-agent** — 顶层应用，依赖 agent、ai、client、protocol、tui
- **session-backends/sqlite-node** — agent 的 session 存储后端
- **evals** — 独立评测框架

## 二、核心三层包（真正内核分层）

这是 Pi 官方定义、源码结构里的 3 个核心包，职责边界清晰，单向依赖：

| # | Package | 定位 | 核心职责 | 依赖 |
|---|---------|------|---------|------|
| L1 | `pi-ai` | Unified LLM 统一模型接入层 | 多 Provider 适配、modelRuntime、模型注册表、归一化流式 chunk、工具 schema、discoverModels、凭证管理、OpenAI/Anthropic/Bedrock/zai 等适配器 | 无其他 Pi 包依赖 |
| L2 | `pi-agent-core` | Agent 纯内核层 | Agent Loop、状态管理、工具抽象与调度、事件总线、StreamFn 传输抽象、会话原语、终止/最大轮次控制 | 仅依赖 pi-ai 的流接口，不绑定文件/CLI/扩展 |
| L3 | `pi-coding-agent` | 产品运行时组装层（SDK 入口） | **最关键**：组装 core + 内置编码工具 (read/write/bash/edit)、会话持久化 (JSONL)、扩展扫描加载 (`~/.pi/extensions`)、Skill、Prompt 模板、models.json 解析、权限确认、多模式（TUI/Print/RPC/stdio）、`createAgentSession` | 依赖 pi-agent-core + pi-ai |

**依赖方向严格单向：`pi-coding-agent` → `pi-agent-core` → `pi-ai`，下层不知道上层。**

### 2.1 附加 UI / 周边包（不属于核心三层）

- `pi-tui`：终端差分渲染 UI，依赖 pi-coding-agent，不直接 import pi-agent-core
- `pi-client` / `pi-protocol` / `pi-server`：实验性 Remote Pi CBOR 远程会话套件，独立叠加层（见第四节）
- `sqlite-node`：session 存储的 Node/SQLite 后端
- `telemetry`：厂商中立的遥测契约
- `evals`：隔离 workspace + 成本收集的评测框架

## 三、本地 TUI/CLI 调用链路（官方原生模式）

```
pi (CLI binary) / pi-tui
    ↓ 调用
pi-coding-agent
    ├─ DefaultResourceLoader 扫描加载磁盘扩展目录
    ├─ 读取 models.json、注册 providers（包含 zai 这类扩展 provider）
    ├─ 注入内置文件/bash工具、StateStore
    └─ createAgentSession() 内部实例化 pi-agent-core 的 AgentLoop
        ↓
pi-agent-core
        ↓ 通过 StreamFn 抽象
pi-ai (modelRuntime.getModel / provider adapters)
        ↓
LLM Provider API
```

## 四、Remote-Pi 远程会话栈（实验性，CBOR）

核心三层之上，官方叠加了一套传输无关的远程会话协议栈：

- `pi-protocol`：CBOR schema、framing（4 字节 big-endian 长度前缀帧）、codec、消息定义
- `pi-client`：transport-neutral CBOR 客户端，`ByteTransport` 是任意传输（WebSocket/TCP/UnixSocket）的插入点
- `pi-server`：字节连接接收、帧解码、sessionId 多路分发、协议命令调度

### 完整远程模式 = 远程协议两层 + 原生核心三层 → 合计五层

```
L5 pi-client (官方)       transport-neutral CBOR 客户端
        ↓ WebSocket/TCP/UnixSocket 字节流
L4 pi-server (官方)       字节连接接入、帧解码、sessionId多路分发、命令调度 Service Boundary
        ↓ 调用 AgentSession / createAgentSession
L3 pi-coding-agent       产品运行时、扩展加载、工具集、会话管理
        ↓
L2 pi-agent-core         Agent Loop / 状态 / 工具编排
        ↓
L1 pi-ai                 统一LLM provider / modelRuntime
        ↓
LLM 厂商 API
```

> 关键点：
>
> - Remote pi-server **不重新实现 AgentLoop**，内部复用 pi-coding-agent 的 AgentSession
> - CBOR 协议栈**完全不依赖** core/coding-agent 业务逻辑，只做字节 ↔ 消息编解码、分发
> - SSE：官方 CBOR 协议本身**原生不支持**，只能做 HTTP 网关适配层（双通道 POST 控制 + SSE base64 推帧 / JSON 桥接），不属于 pi-client/pi-server 原生 transport
> - 会话租约：客户端对会话持有 exclusive / shared lease，支持多端附着与并发控制

## 五、三种运行模式对比

| 模式 | 使用包 | 经过远程协议层？ | 适用场景 |
|------|--------|---------------|---------|
| 本地原生 TUI/CLI | pi-tui → pi-coding-agent → core → pi-ai | ❌ 不经过 pi-server/pi-client | 终端本地开发，最主流 |
| Remote 远程会话 | pi-client → pi-server → pi-coding-agent → core → pi-ai | ✅ 完整五层 | Web UI、远程 Agent 服务、跨进程/跨机器会话 |
| stdin/stdout RPC mode | pi-coding-agent 内置 | ❌ 独立 JSON 行协议 | IDE / 编辑器集成 |

## 六、接 pi-agent-core 还是 pi-coding-agent

| | 用 pi-agent-core（裸 Agent） | 用 pi-coding-agent（createAgentSession） |
|------|---------------------------|----------------------------------------|
| 依赖体积 | 小（仅 pi-ai + telemetry） | 大（拉入工具、扩展、session 管理等） |
| LLM 调用 | 完全一样（最终都走 `streamSimple`） | 完全一样 |
| 编码能力 | 需自己写工具 | 内置 read/grep/find/ls/edit/write/bash |
| 可靠性 | 无自动重试、无 compaction | 自动重试、上下文压缩、错误恢复 |
| 会话持久化 | 无（除非手写） | SessionManager（inMemory / 文件 / SQLite） |

> 经验法则：**做编码类/贴近产品形态的东西用 pi-coding-agent；只要"LLM+工具+循环"的裸内核（如自定义领域 Agent、嵌入式场景）用 pi-agent-core。**

## 七、一次完整调用的数据流

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

> 各层内部实现细节（类型定义、事件生命周期、Agent Loop 双层循环、协议 schema、扩展系统）逐包拆解见 [[3-Pi Agent分析]]。
