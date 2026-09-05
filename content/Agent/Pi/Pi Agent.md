---
title: Pi Agent
date: 2026-08-31
tags:
  - Agent
  - AI编程
  - 工具
description: Pi Agent 介绍、使用方法，以及基于它定制企业级 Agent 的完整指南
---

# Pi Agent

> 极简开源终端编程智能体（Coding Agent）：模型无关、核心极简、扩展随心。GitHub 90K+ Star，MIT 协议。

- 官网：https://pi.dev
- 代码仓库：https://github.com/badlogic/pi-mono
- 协议：MIT（可商用）
- 作者：Mario Zechner（libGDX 游戏框架作者，GitHub @badlogic），现由 Earendil Works 维护

***

## 一、Pi Agent 是什么

**Pi 是一个运行在终端里的极简编程智能体**：你用自然语言提需求，它会自己读文件、写代码、改代码、执行命令，循环往复直到任务完成。

它的定位是 **minimal terminal coding harness（极简终端编码脚手架）**——不是聊天机器人，也不是 IDE 插件，而是一套把**模型、工具、上下文、会话和扩展系统**串起来的终端执行框架。

核心哲学一句话：

> An autonomous agent is just an LLM + tools + a loop.
> 自主智能体本质就三件事：大模型、工具集、循环调度。多余能力全部外置，不塞进内核。

名字 pi 体现了它的定位：像圆周率一样**简单、纯粹、无限延展**。

### 1.1 解决了什么痛点

| 传统 AI 编程工具的痛点 | Pi 的答案                                                                                          |
| ------------- | ----------------------------------------------------------------------------------------------- |
| 厂商锁定          | 内置 30+ 家模型接入：Claude、GPT、Gemini、DeepSeek、Kimi、MiniMax、xAI、OpenRouter……支持本地 llama.cpp，/model 一键切换 |
| 订阅/价格贵        | 复用已有订阅：Claude Pro/Max、ChatGPT Plus/Pro、GitHub Copilot 订阅都能直接登录使用；也可用 API Key 按量付费               |
| 黑盒难定制         | 完全开源（MIT），TypeScript 写几行代码就能加自定义工具、命令、组件；社区包 pi install 一条命令安装                                  |
| 功能堆砌          | 刻意不内置子智能体、计划模式、任务清单、权限弹窗——核心只保留最必要的部分                                                           |
| 隐私顾虑          | 完全本地运行，模型调用走自己的 Key/订阅；支持离线模式（--offline）                                                        |

### 1.2 工作原理（一分钟看懂）

Pi 本质是一个「Agent 循环 + 终端界面」：

1. 你输入自然语言，如"帮我修复登录页面的这个 Bug"
2. Pi 把请求发给 AI 模型，模型默认只有 4 个工具：

| 工具 | 功能 |
|------|------|
| read | 读文件 |
| write | 写文件 |
| edit | 补丁式精确编辑文件 |
| bash | 执行 shell 命令（跑测试、装依赖、git 提交） |

3. 模型自主决定"读哪个文件 -> 怎么改 -> 跑什么命令验证"，循环直到任务完成
4. 全程终端可见每一步操作，随时可打断、补充指令

大道至简，四个工具足以完成绝大多数编程任务。在 Databricks 内部基准测试中，使用 Claude Opus 时 Pi 通过率最高，且成本显著低于 Claude Code 和 Codex，原因是它每轮发送的上下文只有其他工具的约 1/3。

### 1.3 「不做什么」的设计哲学

Pi 官网有一个罕见板块——「What we didn't build」（我们没做什么）。作者的核心假设是：前沿模型经过大量 RL 训练，本身就理解什么是编码代理，框架不需要过度指导模型。

Pi 刻意省略的功能：

- 没有内置 MCP 协议（需要时通过扩展接入）
- 没有子代理（用 tmux 多开终端，或安装 pi-sub-agent 扩展）
- 没有权限确认弹窗（跑在容器里就好）
- 没有计划模式（新建一个 TODO.md 文件）
- 没有内置任务列表（任务列表占用模型上下文）

对比数据：

| 维度 | Claude Code 等主流工具 | Pi |
|------|---------------------|-----|
| 核心 agent 循环代码量 | 数千行 TypeScript | 约 418 行 |
| 系统提示 + 工具定义 | 数千 tokens | < 1,000 tokens |
| 默认工具数量 | 十几个 | 4 个 |

### 1.4 四层架构（monorepo 分包）

| 包名 | 职责 |
|------|------|
| @earendil-works/pi-ai | 模型适配层：统一 30+ 厂商、300+ 模型的 LLM API，抹平消息格式、toolCall、流式事件差异 |
| @earendil-works/pi-agent-core | Agent 核心运行时（灵魂）：Agent Loop、消息会话管理、事件流，不含 UI 和编码业务逻辑 |
| @earendil-works/pi-coding-agent | 编码业务层：会话、工具、持久化、压缩、扩展、Skills、模式 |
| @earendil-works/pi-tui | 终端交互层：渲染界面 |

依赖单向、职责边界干净，非常适合学习 Agent 工程化源码。

***

## 二、使用

### 2.1 安装

```bash
# 全局安装（需要 Node.js 18+）
npm install -g --ignore-scripts @earendil-works/pi-coding-agent

# 或 macOS / Linux 一键脚本
curl -fsSL https://pi.dev/install.sh | sh
```

--ignore-scripts 跳过依赖的生命周期脚本，Pi 正常运行不需要它们（供应链安全加固）。

### 2.2 配置模型

```bash
# 方式 1：环境变量（API Key 按量付费）
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export DEEPSEEK_API_KEY=...

# 方式 2：复用已有订阅（Claude Pro/Max、ChatGPT Plus、GitHub Copilot）
# 首次启动 pi 时按提示 OAuth 登录
```

### 2.3 配置非内置模型（自定义 Provider）

Pi 内置了 30+ 家模型厂商，但仍有部分厂商（如智谱 BigModel）没有内置。任何提供 **OpenAI 兼容 API** 的服务都可以通过 `models.json` 手动接入。

#### 配置文件位置

| 系统 | 路径 |
|------|------|
| Windows | `C:\Users\<用户名>\.pi\agent\models.json` |
| macOS / Linux | `~/.pi/agent/models.json` |

> 该文件默认**不存在**，首次配置需要手动创建（`.pi\agent` 目录在 Pi 首次运行后自动生成）。文件在每次打开 `/model` 时重新加载，编辑后无需重启 Pi。

#### 完整示例：接入智谱 GLM-4.5-air

```json
{
  "providers": {
    "zhipu": {
      "name": "智谱 BigModel",
      "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
      "api": "openai-completions",
      "apiKey": "$ZHIPU_API_KEY",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        {
          "id": "glm-4.5-air",
          "name": "GLM 4.5 Air",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 32000,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
```

#### 字段说明

| 字段 | 说明 |
|------|------|
| `baseUrl` | API 端点，填厂商的 OpenAI 兼容地址 |
| `api` | API 类型：`openai-completions`（最通用）/ `openai-responses` / `anthropic-messages` / `google-generative-ai` |
| `apiKey` | `$环境变量名`（推荐）或 key 明文 |
| `compat` | 兼容性开关（见下方） |
| `models[].id` | 模型 ID（发送给 API 的名字） |
| `models[].reasoning` | 是否推理模型 |
| `models[].contextWindow` / `maxTokens` | 上下文窗口 / 最大输出 token |
| `models[].cost` | 单价（元或美元/token），填 0 表示不追踪费用 |

#### compat 兼容性开关

部分 OpenAI 兼容服务（智谱、Ollama、vLLM 等）不支持 `developer` 角色或 `reasoning_effort` 参数，不关闭会报错：

| 字段 | 说明 |
|------|------|
| `supportsDeveloperRole: false` | Pi 改用 `system` 消息发送系统提示 |
| `supportsReasoningEffort: false` | 不发送 `reasoning_effort` 参数 |

#### 设置 API Key（环境变量方式）

```powershell
# Windows PowerShell（永久设置，设置后需重开终端）
[Environment]::SetEnvironmentVariable("ZHIPU_API_KEY", "你的key", "User")
```

```bash
# macOS / Linux
echo 'export ZHIPU_API_KEY=你的key' >> ~/.bashrc && source ~/.bashrc
```

#### 使用

启动 `pi` 后按 `Ctrl+L`（或输入 `/model`），列表中会出现自定义 provider 的模型，选中即可。

命令行直接指定：

```bash
pi --model zhipu/glm-4.5-air
# 或临时传 key
pi --model zhipu/glm-4.5-air --api-key 你的key
```

#### 鉴权方式优先级

Pi 支持四种鉴权方式，优先级从高到低：

1. `--api-key` 命行参数（仅内存，不落盘）
2. `~/.pi/agent/auth.json` 配置文件
3. 环境变量
4. `models.json` 中 provider 的 `apiKey`

#### 常见厂商的 OpenAI 兼容 baseUrl 参考

| 厂商 | baseUrl |
|------|---------|
| 智谱 BigModel | `https://open.bigmodel.cn/api/paas/v4` |
| Z.ai（智谱海外） | `https://api.z.ai/api/paas/v4` |
| DeepSeek | `https://api.deepseek.com/v1` |
| Moonshot (Kimi) | `https://api.moonshot.ai/v1` |
| MiniMax | `https://api.minimax.io/v1` |
| OpenRouter | `https://openrouter.ai/api/v1` |
| Ollama（本地） | `http://localhost:11434/v1` |
| vLLM（本地） | `http://localhost:8000/v1` |

> 进阶：Extension 中用 `pi.registerProvider()` 也可以注册 provider（支持自定义鉴权、动态拉取模型列表、非标准流式 API），见官方文档 Custom Providers 章节。

### 2.4 基本使用

```bash
cd 你的项目目录
pi
```

进入交互式终端界面后直接打字对话：

```
> 帮我修复登录页面的这个 Bug
> 给 utils/date.ts 补几个单元测试
> 重构这个函数，太长了
```

常用快捷键：

| 快捷键 | 功能 |
|--------|------|
| Ctrl+L | 弹出模型选择器 |
| Shift+Tab | 循环切换思考级别 |
| Esc | 中断当前生成 |

常用命令（会话内输入）：

| 命令 | 功能 |
|------|------|
| /model | 切换模型 |
| /compact | 压缩会话上下文（长会话省钱利器） |
| /review | 代码审查（可指定 focus） |
| /tree | 查看会话树，分支/回放历史 |
| /steer | 任务运行中补充方向（纠偏） |

### 2.5 四种使用模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| Interactive | 终端交互式编码 | 日常读代码、试方案、连续追问 |
| Print / JSON | 把 Pi 当脚本命令，输出被其他程序消费 | CI 流水线、自动化脚本 |
| RPC | 其他进程通过协议调用 Pi | 接入已有工具链、编辑器集成 |
| SDK | 在 TypeScript/Node 项目里直接组合 Pi 能力 | 构建产品、内部工具集成 |

非交互式示例：

```bash
# 一条命令完成审查并输出 JSON（供 CI 消费）
pi -p "审查 src/ 下的改动，输出发现的问题" --json
```

### 2.6 项目上下文文件

在项目根目录放置以下文件，Pi 每次开工前自动读取：

| 文件 | 作用 |
|------|------|
| AGENTS.md | 项目规则：改完代码要跑什么命令、禁止执行什么操作、团队约定 |
| SYSTEM.md | Agent 稳定行为边界，减少每次临场补充 |

AGENTS.md 示例：

```markdown
# 项目规则
- 改完代码必须跑 npm run check 验证
- 禁止本地执行生产数据库迁移
- 提交信息遵循 conventional commits
- 使用 pnpm，不要用 npm
```

### 2.7 安装扩展包

```bash
# 安装社区扩展（如 MCP 支持、子代理等）
pi install <package-name>
```

***

## 三、基于 Pi 定制企业级 Agent

Pi 的三层定制能力，按投入成本从低到高排列：Skills（提示词层）-> Extensions（运行时层）-> SDK（进程内嵌层）。

### 3.1 路线选择

| 路线 | 定制方式 | 成本 | 适用场景 |
|------|---------|------|---------|
| 路线 1 | Skills + Prompt 模板 + AGENTS.md | 小时级 | 统一团队工作流、沉淀最佳实践 |
| 路线 2 | Extensions（TS 代码扩展）+ 自定义工具 | 天级 | 接入内部系统、增加领域工具、安全拦截 |
| 路线 3 | SDK 内嵌（createAgentSession） | 周级 | 做成产品、Web 界面、自动化流水线 |

### 3.2 路线 1：Skills——把团队经验固化

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

### 3.3 路线 2：Extensions——自定义工具与拦截

用 TypeScript 写扩展，可以给 Agent 加自定义工具、修改运行时行为。

#### 自定义工具示例

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

#### 安全拦截（企业必备）

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

#### 会话压缩（长会话成本控制）

```typescript
// 主动压缩会话，保留关键信息丢弃冗余
const result = await session.compact('保留所有架构决策，丢弃中间调试过程');
```

### 3.4 路线 3：SDK——进程内嵌完整 Agent

createAgentSession 在调用方进程内构建完整 Agent 会话，可注入自定义存储、配置、认证、模型注册表、资源加载器和工具——无桥接、无子进程、无 socket。

#### 最小可用示例

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

#### AgentSession 核心能力

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

#### 自定义全部注入项

```typescript
const { session } = await createAgentSession({
  model: myModel,                    // 锁定企业指定模型
  tools: ['read', 'bash'],           // 只开放部分工具（禁 write/edit）
  sessionManager: SessionManager.create(customDir),  // 会话持久化到企业指定位置
});
```

### 3.5 企业级架构参考

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

### 3.6 成本与可观测性

- Pi 内置 Token 与成本追踪，界面底部实时显示当前模型、思考级别、token 消耗和费用估算
- SDK 模式下可通过事件流自建监控面板，按用户/项目/任务维度统计
- compact() 主动压缩长会话，避免上下文膨胀导致成本失控

***

## 四、Pi vs 主流工具对比

| 维度 | Claude Code | Codex CLI | Pi |
|------|-------------|-----------|-----|
| 开源 | 否 | 否 | 是（MIT） |
| 模型绑定 | Anthropic | OpenAI | 无绑定，30+ 厂商 |
| 核心大小 | 重 | 重 | 约 418 行核心循环 |
| 内置功能 | 大而全 | 大而全 | 极简，按需扩展 |
| 上下文效率 | - | - | 约 1/3（基准测试） |
| 定制能力 | 有限 | 有限 | Tools/Extensions/SDK 全开 |
| 沙箱/权限 | 内置审批 | 内置审批 | 无（自行容器化） |

## 五、适合谁

- 想要多模型自由切换、不被单一厂商锁定的开发者/团队
- 已有 Claude/ChatGPT/Copilot 订阅想复用、不想额外付费的用户
- 需要深度定制 Agent 行为、把 Agent 嵌入自有产品的工程团队
- 对代码隐私有要求、需要本地/私有化部署的企业
- 不适合：想要开箱即用、全功能大礼包的用户（更适合 Claude Code 这类成品）
- 不适合：没有能力/意愿做容器隔离就直接跑生产（Pi 无内置沙箱）

***

## 参考链接

- 官网：https://pi.dev
- GitHub：https://github.com/badlogic/pi-mono
- 官方文档（SDK / Extensions / Skills）：https://pi.dev/docs
- 中文指南（社区）：https://pi-agent.org

### npm 包地址

| 包名 | 用途 | npm 地址 |
|------|------|---------|
| `@earendil-works/pi-coding-agent` | 主包：CLI + SDK（含 createAgentSession） | https://www.npmjs.com/package/@earendil-works/pi-coding-agent |
| `@earendil-works/pi-agent-core` | Agent 核心运行时（Agent Loop / 事件流） | https://www.npmjs.com/package/@earendil-works/pi-agent-core |
| `@earendil-works/pi-ai` | 模型适配层（统一 30+ 厂商 LLM API） | https://www.npmjs.com/package/@earendil-works/pi-ai |
| `@earendil-works/pi-tui` | 终端交互渲染层 | https://www.npmjs.com/package/@earendil-works/pi-tui |

> 日常使用只需安装主包 `@earendil-works/pi-coding-agent`（其余三个是它的依赖，会自动安装）；做深度定制时才需要单独引用。