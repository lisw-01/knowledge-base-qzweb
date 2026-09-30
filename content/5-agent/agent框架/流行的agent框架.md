> 核心一句话：**所有框架本质都是在帮你工程化"ReAct 循环 + 工具调用 + 记忆 + 多角色协作"**，先手写懂原理，再按场景选框架。

## 一、总览对比表

| 框架 | 出品方 | 开源 | 语言 | 定位一句话 |
|---|---|---|---|---|
| LangChain / LangGraph | LangChain | ✅ MIT | Python/JS | 生态最全的"乐高积木"+ 状态机编排 |
| LlamaIndex | LlamaIndex | ✅ MIT | Python/JS | 数据接入 + RAG 检索见长 |
| AutoGen | 微软 | ✅ MIT | Python/.NET | 多 Agent 对话协作鼻祖 |
| Semantic Kernel | 微软 | ✅ MIT | C#/Python/Java | 企业级、.NET 生态集成 |
| CrewAI | CrewAI | ✅ MIT | Python | 角色化"团队"编排，上手最快 |
| OpenAI Agents SDK | OpenAI | ✅ MIT | Python | 轻量官方方案，Swarm 的正式版 |
| smolagents | HuggingFace | ✅ Apache | Python | 极简 Code Agent（写代码当行动） |
| Dify | LangGenius | ✅ 修改版Apache | Web平台 | 可视化工作流，低代码平台 |
| Coze | 字节跳动 | ⚠️ 国内版闭源 / Coze开源版可自部署 | Web平台 | Bot 搭建平台，零代码 |
| Claude Agent SDK | Anthropic | ✅ MIT | Python/TS | 官方长任务 Agent + MCP 工具生态 |
| Pi (pi-mono) | earendil-works (Mario Zechner) | ✅ MIT | TypeScript | 极简 Agent Harness + 自扩展编码 Agent |

## 二、逐个拆解

### 1. LangChain / LangGraph

- **核心功能**
    - LangChain：统一的模型/工具/记忆/提示词抽象层，集成上千个组件
    - LangGraph：基于图的状态机编排，节点=步骤，边=流转，支持循环、分支、人工介入（human-in-the-loop）、状态持久化
- **优点**：生态最大、文档社区最全；LangGraph 适合复杂可控流程；LangSmith 可做链路追踪调试
- **缺点**：抽象层过厚，"为简单事情包十层"；版本迭代快、Breaking change 多；早期 API 被诟病过度封装
- **开源**：✅ MIT，商业化靠 LangSmith（观测）/ LangServe（部署）

### 2. LlamaIndex

- **核心功能**：数据框架——PDF/数据库/API 等异构数据 → 索引 → 检索 → 交给 LLM；Query Engine / Agent / Workflow 三层 API
- **优点**：RAG 场景最专业，数据连接器（LlamaHub）丰富；比 LangChain 聚焦，RAG 场景下代码更简洁
- **缺点**：RAG 之外的能力（多 Agent 协作等）相对弱；国内社区资料少于 LangChain
- **开源**：✅ MIT

### 3. AutoGen（微软）

- **核心功能**：多 Agent 以"对话"方式协作——GroupChat、代码执行器、人工介入；v0.4 后重构为事件驱动 + AutoGen Studio 可视化
- **优点**：多角色讨论/互相纠错能力强；微软背书，适合研究多 Agent 范式
- **缺点**：概念多、学习曲线陡；对话轮数不可控时 Token 消耗大；v0.2→v0.4 API 变动剧烈
- **开源**：✅ MIT

### 4. Semantic Kernel（微软）

- **核心功能**：插件（Plugin/函数）+ 规划器（Planner）+ 内存；原生融入 .NET/Azure 生态
- **优点**：企业级稳定性，C#/Java 支持最好；和 Azure OpenAI 无缝集成；适合存量企业系统接入
- **缺点**：Python 生态不如 .NET 完善；国内教程少；偏"企业味"，快速原型不如 CrewAI 爽
- **开源**：✅ MIT

### 5. CrewAI

- **核心功能**：以"团队"为隐喻——定义角色（Role）、目标（Goal）、背景故事（Backstory），按流程（Process）协作
- **优点**：概念直观，10 行代码跑起多 Agent；内置工具多；社区增长快
- **缺点**：灵活性有限，复杂流程控制力不如 LangGraph；调试偏黑盒，Token 消耗不小
- **开源**：✅ MIT，企业版闭源收费

### 6. OpenAI Agents SDK

- **核心功能**：Agent（指令+工具）+ Handoff（Agent 间移交）+ Guardrails（输入输出护栏）+ Tracing；前身是实验品 Swarm
- **优点**：极简、官方维护、原-function calling 风格，无过度抽象；Handoff 做多 Agent 很轻
- **缺点**：模型绑定 OpenAI（虽支持其他模型但体验打折）；能力较薄，复杂记忆/编排要自己写
- **开源**：✅ MIT

### 7. smolagents（HuggingFace）

- **核心功能**：CodeAgent——Agent 直接**写 Python 代码**作为行动（比 JSON 工具调用更灵活），核心代码极薄
- **优点**：动作空间是代码，减少解析出错；轻量好读，适合学原理；HF 生态（模型/空间）联动
- **缺点**：代码执行要沙箱隔离（安全成本）；场景不如大框架全面
- **开源**：✅ Apache 2.0

### 8. Dify（平台型）

- **核心功能**：Web 界面可视化编排工作流；内置 RAG、工具调用、知识库、模型管理；一次编排多端发布
- **优点**：低代码，非程序员也能搭 Agent；自部署简单（Docker）；工作流+Agent 混合模式实用
- **缺点**：复杂逻辑受限于画布节点；深度定制要写代码但平台约束多；修改版 Apache 协议对多租户 SaaS 有限制
- **开源**：✅（可自部署），商业版云服务收费

### 9. Coze（字节跳动）

- **核心功能**：零代码 Bot 搭建——插件/工作流/知识库/数据库/定时任务，发布到飞书、微信、Discord 等渠道
- **优点**：上手门槛最低，产品体验好；渠道发布一键完成；提示词优化、卡片交互等周边全
- **缺点**：国内版闭源，数据走平台云端；深度可控性差；开源版（Coze Studio）自部署需一定运维能力
- **开源**：⚠️ 国内 SaaS 闭源；海外有开源版可自部署

### 10. Claude Agent SDK

- **核心功能**：Anthropic 官方 Agent 开发套件——文件系统操作、Shell 执行、网页搜索等内置工具；深度绑定 MCP（Model Context Protocol）工具协议
- **优点**：Claude 模型原生优化，长任务（数小时级）能力强；MCP 已成为工具接入的事实标准，生态扩张快
- **缺点**：强绑定 Claude 模型；较新，成熟度/社区资料不如 LangChain 系
- **开源**：✅ MIT

### 11. Pi（pi-mono / pi-agent）

- **核心功能**：分层的极简工具箱（"harness not framework"）——`pi-ai`（统一多厂商 LLM API）、`pi-agent-core`（Agent 循环 + 工具调用 + 状态管理）、`pi-coding-agent`（交互式编码 Agent CLI）、`pi-tui`（终端 UI）；支持 MCP，最特色的**自扩展**：Agent 可以自己写代码给自己加工具/扩展
- **优点**：无过度抽象，代码量小、可通读，适合学"Agent 到底是什么"；多模型统一 API 干净；GitHub 110k+ stars，"极简主义"流派代表作
- **缺点**：偏编码 Agent 场景，通用业务编排能力弱；**无内置权限系统**（文件/进程/网络不做限制，需自行 Docker/沙箱隔离）；TypeScript 生态，Python 用户上手成本高；中文资料少
- **开源**：✅ MIT
- **定位提醒**：它和 Claude Code、Codex CLI、OpenCode、aider 同属"编码 Agent"赛道，与上面 LangChain/AutoGen 等"通用编排框架"不是一个类别

## 三、怎么选（经验法则）

```
想深入理解原理        → 先手写 ReAct（见学习路径），别急着上框架
复杂可控流程/生产级    → LangGraph
RAG 为主             → LlamaIndex
多角色讨论/研究多Agent → AutoGen
快速搭多 Agent 原型    → CrewAI
只用 OpenAI、要轻量    → OpenAI Agents SDK
C#/.NET 企业项目      → Semantic Kernel
不想写代码/做产品 Demo  → Dify 或 Coze
用 Claude 模型        → Claude Agent SDK（+ MCP 工具）
极简主义/讨厌重框架     → Pi（或干脆手写循环）
```

> ⚠️ 共同的坑：框架都解决不了"Prompt 写不好"和"工具设计不合理"这两个根本问题；Token 消耗 = 轮数 × 上下文长度，多 Agent 系统尤其烧钱，先小跑通再放规模。
