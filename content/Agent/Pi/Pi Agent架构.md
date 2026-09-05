- ✅ **官方原生核心三层包架构**：monorepo 原生设计，本地 TUI/CLI 走这个
- ✅ **官方实验性 Remote-Pi 远程会话扩展栈**：CBOR framed 二进制协议（pi-client /pi-protocol/pi-server），叠加在核心三层之上。


## 一、官方原生：核心三层包（真正内核分层）

这是 Earendil Works Pi 官方定义、源码结构里的 3 个核心包，职责边界清晰，单向依赖：

| #   | Package           | 定位                  | 核心职责                                                                                                                                                                        | 依赖                              |
| --- | ----------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| L1  | `pi-ai`           | Unified LLM 统一模型接入层 | 多 Provider 适配、modelRuntime、模型注册表、归一化流式 chunk、工具 schema、discoverModels、凭证管理、OpenAI/Anthropic/Bedrock/zai 等适配器                                                                | 无其他 Pi 包依赖                      |
| L2  | `pi-agent-core`   | Agent 纯内核层          | Agent Loop、状态管理、工具抽象与调度、事件总线、StreamFn 传输抽象、会话原语、终止 / 最大轮次控制                                                                                                                 | 仅依赖 pi-ai 的流接口，不绑定文件 / CLI / 扩展 |
| L3  | `pi-coding-agent` | 产品运行时组装层（SDK 入口）    | **最关键**：组装 core + 内置编码工具 (read/write/bash/edit)、会话持久化 (JSONL)、扩展扫描加载 (`~/.pi/extensions`)、Skill、Prompt 模板、models.json 解析、权限确认、多模式（TUI/Print/RPC/stdio）、`createAgentSession` | 依赖 pi-agent-core + pi-ai        |




**依赖方向严格单向：`pi-coding-agent` → `pi-agent-core` → `pi-ai`，下层不知道上层。**






### 1.1 附加 UI / 周边包（不属于核心三层）

- `pi-tui`：终端差分渲染 UI，**依赖 pi-coding-agent，不直接 import pi-agent-core**
- `pi-client` / `pi-protocol` / `pi-server`：**实验性 Remote Pi CBOR 远程会话套件**（我们之前讨论的 framed-CBOR transport-neutral 协议，是独立叠加层）
### 1.2 TUI / CLI 正确本地调用链路（官方原生模式）

plaintext

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



## 二、官方 Remote-Pi 远程会话扩展栈（实验性，CBOR）

这就是我们前面讨论的 framed-CBOR /transport-neutral 远程会话、

- `pi-protocol`：CBOR schema、framing、codec、消息定义 = 我们说的 Pi-Remote-Session
- `pi-client`：transport-neutral CBOR 客户端 = 我们说的 Layer5 Pi-SessionClient
- `pi-server`：字节连接接收、会话多路分发、协议命令调度 = 我们说的 Layer4 Pi-ConnectionService

### 完整远程模式 = 远程协议两层 + 原生核心三层 → 合计五层

也就是我们之前推演的五层，**它是 Remote 分布式部署的完整栈，不是 Pi 原生内核分层**：

plaintext

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
> - Remote pi-server 不重新实现 AgentLoop，内部复用 pi-coding-agent 的 AgentSession
> - CBOR 协议栈**完全不依赖** core/coding-agent 业务逻辑，只做字节 ↔ 消息编解码、分发
> - SSE：官方 CBOR 协议本身**原生不支持**，只能做 HTTP 网关适配层（双通道 POST 控制 + SSE base64 推帧 / JSON 桥接），不属于 pi-client/pi-server 原生 transport




# 三 、 两种官方运行模式对比

| 模式                    | 使用包                                                    | 经过远程协议层？                  | 适用场景                           |
| --------------------- | ------------------------------------------------------ | ------------------------- | ------------------------------ |
| 本地原生 TUI/CLI          | pi-tui → pi-coding-agent → core → pi-ai                | ❌ 不经过 pi-server/pi-client | 终端本地开发，最主流                     |
| Remote 远程会话           | pi-client → pi-server → pi-coding-agent → core → pi-ai | ✅ 完整五层                    | Web UI、远程 Agent 服务、跨进程 / 跨机器会话 |
| stdin/stdout RPC mode | pi-coding-agent 内置                                     | ❌ 独立 JSON 行协议             | IDE / 编辑器集成                    |


# 四、连pi-agent-core 还是 pi-coding-agent

|        | 用 pi-agent-core（裸 Agent）  | 用 pi-coding-agent（createAgentSession）  |
| ------ | ------------------------- | -------------------------------------- |
| 依赖体积   | 小（仅 pi-ai + telemetry）    | 大（拉入工具、扩展、session 管理等）                 |
| LLM 调用 | 完全一样（最终都走 `streamSimple`） | 完全一样                                   |
| 编码能力   | 需自己写工具                    | 内置 read/grep/find/ls/edit/write/bash   |
| 可靠性    | 无自动重试、无 compaction        | 自动重试、上下文压缩、错误恢复                        |
| 会话持久化  | 无（除非手写）                   | SessionManager（inMemory / 文件 / SQLite） |
