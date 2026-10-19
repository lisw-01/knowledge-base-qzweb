# STORY.md — 从 LLM 到 Agent 再到 Pi Agent

## ① 用户意图对齐

- **目标受众**：公司内部研发同学（懂代码、会写工程，但没有系统做过 AI Agent）。现场分享场景，约 40–60 分钟。
- **核心目标**：听完之后，听众能① 说清 LLM、Agent、Pi Agent 三者的递进关系；② 理解 Agent 的能力边界来自"七层工程"而非模型本身；③ 知道 Pi 的极简哲学与它凭什么省 token；④ 看懂 agent-DQ（智数问答）是如何把 Pi 落地成一个真实业务系统，并带走一批可直接复用的踩坑经验。
- **PPT 长度**：33 页（封面 + 目录 + 4 章 + 结束页）。Hero 页 7 页，占比 21%。
- **视觉调性**：科技深色 / 深蓝底 + 青蓝高亮 / 工程感 / 克制 / 数据密集。
- **内容边界**：
  - 必讲：LLM 的无状态与上下文窗口、Function Calling、ReAct、Agent 七层功能地图、十条设计原则、Pi 的极简哲学与分层架构、agent-DQ 的三级路由 / 发现式注册 / 隔离与安全 / SSE 链路、真实踩坑。
  - 不讲：Transformer 内部原理、模型训练与微调、向量数据库选型细节、多 Agent 编排。
  - 禁碰：任何未经文档佐证的数字与结论；不虚构 benchmark。

---

## ② 页面布局骨架

**页面总数与分章（33 页 / 4 章）**

| 章节 | 页码 | 页数 |
| :--- | :--- | :--- |
| 封面 + 目录（前置） | 01–02 | 2 |
| 第 1 章 LLM：一切的地基 | 03–09 | 7 |
| 第 2 章 Agent：从"能聊"到"能干" | 10–18 | 9 |
| 第 3 章 Pi Agent：一个极简范式 | 19–25 | 7 |
| 第 4 章 落地实践：智数问答 agent-DQ | 26–32 | 7 |
| 结束页 | 33 | 1 |

**目录↔章节扉页契约（强制，N=4）**

| 目录条目 | 章节扉页 | 扉页标题（逐字一致） | 页码区间 |
| :--- | :--- | :--- | :--- |
| 01 · LLM：一切的地基 | 第 03 页 | `01 · LLM：一切的地基` | 03–09 |
| 02 · Agent：从"能聊"到"能干" | 第 10 页 | `02 · Agent：从"能聊"到"能干"` | 10–18 |
| 03 · Pi Agent：一个极简范式 | 第 19 页 | `03 · Pi Agent：一个极简范式` | 19–25 |
| 04 · 落地实践：智数问答 agent-DQ | 第 26 页 | `04 · 落地实践：智数问答 agent-DQ` | 26–32 |

→ 4 个 `type: section` 扉页齐全、编号 01–04 连续，与目录逐字一致。✅

**Hero 页定位（7 页 / 21%）：** 01（封面）· 11（Agent 公式）· 15（七层地图）· 21（418 行核心）· 23（完整数据流）· 28（三级路由）· 33（结束页）。
间隔校验：01→11→15→21→23→28→33，任意两个 Hero 之间至少隔 1 页 Supporting。✅

**rhythm 曲线**

01 peak｜02 valley｜03 transition｜04 valley｜05 valley｜06 peak｜07 valley｜08 valley｜09 peak｜10 transition｜11 peak｜12 valley｜13 peak｜14 valley｜15 peak｜16 valley｜17 peak｜18 valley｜19 transition｜20 valley｜21 peak｜22 valley｜23 peak｜24 valley｜25 valley｜26 transition｜27 valley｜28 peak｜29 valley｜30 valley｜31 peak｜32 valley｜33 peak

→ 无连续 ≥3 页 valley；章节切换处均为 transition。✅

**非对称版式预算：** 内容页 28 页中 27 页使用非对称版式（96% ≥ 40%）。✅
**对称版式预算：** 仅第 09 页使用 `图表+洞察`（1 页 ≤ 2 页上限）；封面 / 章节扉页 / 结束页走自定义版式。✅
**`N卡片横排` 出现次数：** 0（≤2）。✅
**`左大图+右侧文字` + `非对称双栏` 合计：** 7 页（`非对称双栏` 于 05/13/17/20/25/27/30），占 21%（≤40%）。✅

---

## ③ 页面大纲

> 契约：本表是 STORY.md 与 slides/*.slide 之间的逐页约定，生成时严格对照。

| # | title | type | role | rhythm | layout | visual | visual_role | density | anti_pattern | description |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 01 | 从 LLM 到 Agent 再到 Pi Agent | cover | hero | peak | 全幅图+骑线文字 | L1: cover_hero.png（全幅底图） | anchor | 字数约40 / 图1 / 留白35% | 禁止居中平铺纯文字；禁止标题右侧塞装饰小图 | 主标题 + 副标题"一条从模型到业务系统的完整链路" + 分享人/日期。一句话点题：模型是原料，Agent 才是产品。 |
| 02 | 目录 | catalog | supporting | valley | 左标题+右内容 | L3: 青蓝角标 | evidence | 字数约150 / 图0 / 留白22% | 禁止四卡片横排；禁止条目只写标题不写看点 | 四章并列，每章一句"听完你能得到什么"。 |
| 03 | 01 · LLM：一切的地基 | section | transition | transition | 全屏视觉+大标题 | L1: sec_llm.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白45% | 禁止铺满正文段落；禁止四卡片预览 | 章节扉页 + 一句导语：不理解 LLM 的无状态，就理解不了 Agent 的上下文工程。 |
| 04 | LLM 是"无状态的文本预测器" | content | supporting | valley | 左标题+右内容 | Diagram(Token 切分示意 SVG) | evidence | 字数约240 / 图1 / 留白25% | 禁止把 Token/上下文窗口塞进等宽卡片；禁止只给定义不给后果 | 无状态 = 每次请求都要把 messages 完整重发；上下文窗口 = 输入+输出总量上限。判断：Agent 里上下文膨胀是必然，不是意外。 |
| 05 | 四个必须先记住的概念 | content | supporting | valley | 非对称双栏 | FAIcon列表（4 项） | evidence | 字数约300 / 图0 / 留白22% | 禁止等宽四卡横排；禁止只罗列术语 | Prompt 定角色与格式、Temperature=0 保确定性、幻觉要靠工具真实数据压制、Embedding 是长期记忆的检索底座。判断：这四点决定了 Agent 的稳定性上限。 |
| 06 | 两种调用方式：对话 vs 工具调用 | content | supporting | peak | 左标题+右内容 | Diagram(两条链路对比 SVG) | evidence | 字数约260 / 图1 / 留白24% | 禁止 50:50 等分双栏；禁止把工具调用写成"高级对话" | 普通对话只出文本；工具调用让模型输出结构化参数、由你的代码真正执行。判断：这一步是"聊天机器人"与"Agent"的分水岭。 |
| 07 | 方案 A：手写 Prompt 的 ReAct 循环 | content | supporting | valley | 上大图+下方卡片 | CodeBlock(Python) + L2 踩坑卡 | anchor | 字数约280 / 图1 / 留白20% | 禁止把代码缩成 200×70 装饰贴片；禁止只贴代码不讲坑 | 上半部完整 ReAct 循环代码，下半部三张"踩坑实录"卡：模型自演 Observation、正则解析失败、循环耗尽返回 None。判断：格式自己发明，就一定会有不守规矩的一天。 |
| 08 | 方案 B：原生 Function Calling | content | supporting | valley | 左标题+右内容 | CodeBlock(TypeScript/JSON) | evidence | 字数约250 / 图1 / 留白22% | 禁止只讲概念不给 schema；禁止把 Schema 说成"可选优化" | 用 JSON Schema 正式声明工具，模型返回 tool_calls，无需正则。判断：description 就是写给模型看的 API 文档。 |
| 09 | A/B 对比与一条安全红线 | content | supporting | peak | 图表+洞察 | Table(4 行对比) | evidence | 字数约180 / 图1 / 留白28% | 禁止把结论埋在正文里；禁止罗列对比却不给选型建议 | 四维对比 + 选型结论：实际项目一律用原生 Function Calling。安全红线：模型只有建议权，执行权永远在你的代码里。 |
| 10 | 02 · Agent：从"能聊"到"能干" | section | transition | transition | 全屏视觉+大标题 | L1: sec_agent.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白45% | 禁止铺满正文段落；禁止四卡片预览 | 章节扉页 + 导语：Agent 的核心代码就一个 while 循环，真正的开发量全在循环之外。 |
| 11 | Agent = LLM + 工具 + 记忆 + 规划 | content | hero | peak | 巨型数字+洞察 | 大数字公式（≥72px） | anchor | 字数约120 / 图0 / 留白38% | 禁止等宽卡片横排；禁止把公式缩成一句正文 | 巨型公式占据视觉重心，四要素各配一句白话解释。判断：缺任何一项，都只是"会聊天的模型"。 |
| 12 | ReAct：思考 → 行动 → 观察 | content | supporting | valley | 左标题+右内容 | Diagram(循环回路 SVG) | anchor | 字数约230 / 图1 / 留白26% | 禁止把循环画成单向流程图；禁止不给终止条件 | Thought / Action / Observation 三段交替，直到 Answer。判断：循环必须带最大轮数兜底，否则一次死循环烧掉一个月预算。 |
| 13 | 工具与记忆：手脚和上下文 | content | supporting | peak | 非对称双栏 | FAIcon列表 + Diagram(记忆分层) | evidence | 字数约320 / 图1 / 留白20% | 禁止把"工具"讲成函数列表；禁止忽略"工具返回 = 模型可见输入" | 工具：小而专、描述大于实现、参数先校验再执行、错误要回喂。记忆：近期带原文、远期压摘要、事实存卡片、知识进向量库。 |
| 14 | 学习路径：五个阶段 | content | supporting | valley | 上大图+下方卡片 | Diagram(五阶段时间轴 SVG) | anchor | 字数约250 / 图1 / 留白22% | 禁止四卡横排；禁止跳过"手写 ReAct"直接讲框架 | 阶段 1 手写 ReAct → 2 原生 FC → 3 加记忆与 RAG → 4 多工具真实场景 → 5 框架与工程化。判断：先手写再上框架，否则出问题完全不会排查。 |
| 15 | 七层功能地图 | content | hero | peak | 巨型数字+洞察 | 大数字"⑦" + Diagram(七层塔 SVG) | anchor | 字数约160 / 图1 / 留白32% | 禁止把七层压成一行文字；禁止用等宽卡片代替层塔 | ①模型 ②提示 ③工具 ④记忆 ⑤控制 ⑥护栏 ⑦运营。判断：①~⑤ 是搭起来，⑥~⑦ 是别出事、出事能查；换模型只动①，加工具只动③。 |
| 16 | 逐层拆解：每层到底要写什么 | content | supporting | valley | 左标题+右内容 | FAIcon列表（7 行） | evidence | 字数约380 / 图0 / 留白18% | 禁止只列层名不给动作项；禁止单栏线性流水账排版 | 七层各给 2–3 个必须落地的动作项（如①的密钥/重试/流式、③的参数校验/错误回喂、⑤的四个终止条件）。 |
| 17 | 十条设计原则 | content | supporting | peak | 非对称双栏 | Table(10 行，宽侧) | evidence | 字数约300 / 图1 / 留白18% | 禁止把原则写成口号；禁止不给"违背的下场" | 每条原则配一句解释 + 违背后果。判断：前 3 条是架构级（决定项目成败），后 7 条是工程习惯级（决定维护成本）。 |
| 18 | 避坑清单与上线自查 | content | supporting | valley | 左标题+右内容 | FAIcon(check-circle) 双列清单 | evidence | 字数约260 / 图0 / 留白22% | 禁止与上一页原则页版式雷同；禁止清单只写正面表述 | 左列：7 条开发避坑；右列：7 条上线自查。判断：全部打勾，才算从"能跑的 demo"变成"敢给别人用的 Agent"。 |
| 19 | 03 · Pi Agent：一个极简范式 | section | transition | transition | 全屏视觉+大标题 | L1: sec_pi.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白45% | 禁止铺满正文段落；禁止四卡片预览 | 章节扉页 + 导语：自主智能体本质就是 LLM + 工具 + 循环；Pi 把这条公式工程化到了极致。 |
| 20 | Pi 是什么：三个反常识设计 | content | supporting | valley | 非对称双栏 | FAIcon列表（3 项） | evidence | 字数约300 / 图0 / 留白20% | 禁止 50:50 等分；禁止把"刻意不内置"写成功能缺失 | Pi = 极简终端编码代理 + 可复用 Agent 运行时（MIT）。刻意不内置 MCP/子代理/权限弹窗/计划模式/任务清单；无沙箱；上下文极省。判断：不是功能少，是把指导权还给模型。 |
| 21 | 极简的代价与回报 | content | hero | peak | 巨型数字+洞察 | 大数字 418 / 4 / 1/3（≥96px） | anchor | 字数约130 / 图1 / 留白34% | 禁止把三个数字塞进图表角落；禁止只给数字不给解释 | 核心循环约 418 行、系统提示 <1000 token、默认 4 个工具、每轮上下文约为同类工具 1/3。判断：省下来的上下文，就是省下来的钱和准确率。 |
| 22 | 分层架构：严格单向的 monorepo | content | supporting | valley | 左标题+右内容 | Diagram(四层依赖 SVG) | anchor | 字数约240 / 图1 / 留白24% | 禁止把四层画成平铺方块；禁止用 200×70 小图替代架构图 | pi-ai（统一 LLM）→ pi-agent-core（内核）→ pi-coding-agent（产品层）→ pi-tui（终端 UI），外加远程会话栈。判断：做编码类产品用 coding-agent，只要"LLM+工具+循环"的裸内核用 core。 |
| 23 | 一次调用的完整数据流 | content | hero | peak | 上大图+下方卡片 | Diagram(端到端链路 SVG，占满上半) | anchor | 字数约200 / 图1 / 留白20% | 禁止把链路压成单行文字；禁止省略工具四阶段 | 输入 → AgentSession.prompt → 双层 while → transformContext/convertToLlm → streamSimple → 事件回流 → 工具准备/执行/收尾/截断保护 → agent_end。判断：看懂了这条流，就懂了 Pi 的一切扩展点。 |
| 24 | 九个设计点：对应七层地图 | content | supporting | valley | 左标题+右内容 | Table(9 行映射表) | evidence | 字数约280 / 图1 / 留白18% | 禁止只列设计点名不写"解决什么问题"；禁止与七层地图页版式重复 | 模型适配 / 上下文工程 / 工具系统 / 会话系统 / Agent 循环 / 扩展系统 / 事件系统 / 安全与可观测 / 远程会话栈，一一映射到七层。判断：编号即层号——这是刻意的教学设计。 |
| 25 | 三层定制能力 | content | supporting | valley | 非对称双栏 | FAIcon列表（3 路线） | evidence | 字数约300 / 图0 / 留白20% | 禁止等宽三卡横排；禁止不给成本量级 | Skills（小时级，沉淀团队经验）→ Extensions（天级，加工具与拦截）→ SDK（周级，嵌进自有产品）。判断：先问"我要改造哪一层"，再选路线。 |
| 26 | 04 · 落地实践：智数问答 agent-DQ | section | transition | transition | 全屏视觉+大标题 | L1: sec_practice.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白45% | 禁止铺满正文段落；禁止四卡片预览 | 章节扉页 + 导语：把前面所有知识，装进一个真实业务系统。 |
| 27 | 项目概览：一句话与一套栈 | content | supporting | valley | 非对称双栏 | Diagram(架构总览 SVG) | evidence | 字数约300 / 图1 / 留白20% | 禁止 50:50 等分；禁止把技术栈写成 logo 墙 | 自然语言 → PI 理解意图并调工具 → 前端流式渲染文本/表格/图表/KPI。栈：Vue3+TS+Pinia / Node+Koa / @earendil-works/pi-coding-agent / 内存种子数据。判断：PI 是编排核心，不是外挂组件。 |
| 28 | 三级路由：准确性的核心 | content | hero | peak | 巨型数字+洞察 | 大数字"三级" + Diagram(路由决策 SVG) | anchor | 字数约200 / 图1 / 留白26% | 禁止让模型"自由选工具"；禁止把三级写成并列三卡 | ①业务 API → ②指标模板 → ③受控 SQL，不得跳级；缺参不调工具、先向用户索要。判断：把"选哪条路"从模型手里收回来，是准不准的关键。 |
| 29 | 发现式注册：加工具 = 丢一个文件 | content | supporting | valley | 左标题+右内容 | CodeBlock(扩展注册) + 目录树 | evidence | 字数约260 / 图1 / 留白22% | 禁止把注册机制讲成"配置数组"；禁止只贴代码不讲发现路径 | `.pi/extensions/*.ts` 由 DefaultResourceLoader 自动发现；`.pi/AGENTS.md`、`APPEND_SYSTEM.md` 自动合并进系统提示；代码里零硬编码工具数组。判断：新增能力不改主干代码，是低耦合的落地方式。 |
| 30 | 隔离与安全：租户 · 范围 · SQL 守卫 | content | supporting | valley | 非对称双栏 | Diagram(三层防线 SVG) | evidence | 字数约320 / 图1 / 留白20% | 禁止把安全写成"加了个校验"；禁止省略"PI 层无感知" | 数据范围：JWT → 显式传参 → scoper 强制注入 tenant_id + 部门；会话归属校验防越权读历史；SQL 经 node-sql-parser AST 校验（仅 SELECT/表白名单/强制 limit/AST 级注入范围）。判断：PI 层无感知、无法绕过，安全才成立。 |
| 31 | 流式链路与前端渲染扩展 | content | supporting | peak | 上大图+下方卡片 | Diagram(SSE 链路 SVG) + CodeBlock(契约) | anchor | 字数约240 / 图1 / 留白20% | 禁止把 SSE 讲成"轮询的替代品"；禁止省略事件契约 | session.subscribe → event-bus 映射 → SSE 事件契约（text_delta/thinking_delta/render/error/turn_reset/done）→ 前端按 renderer 路由 Text/Table/Chart/KPI。判断：后端只管发结构化事件，前端注册表决定长什么样。 |
| 32 | 踩坑实录：四个真实 Bug | content | supporting | valley | 左标题+右内容 | FAIcon列表（4 条）+ 大数字编号 | evidence | 字数约330 / 图1 / 留白18% | 禁止把踩坑写成"注意事项"；禁止只讲现象不讲根因与修法 | ① jiti 加载导致 ALS 实例隔离 → 彻底显式传参；② 事件订阅重复导致每字双倍 → attach 先 detach；③ 模型层 429 被静默吞掉 → message_end 兜底推错；④ 空结果被降级重试 → 双层熔断。判断：Agent 的坑大多不在模型，在"边界"。 |
| 33 | 模型是原料，工程才是产品 | ending | hero | peak | 全屏视觉+大标题 | L1: ending_hero.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白42% | 禁止堆砌致谢名单；禁止把结论写成流程回顾 | 收束金句 + 三段式回顾（模型/工程/落地）+ 落款与 Q&A。 |

**Checklist 自检**
- Hero 页 7 / 33 = 21%（20–30% 区间内）；封面与结束页为 hero；无相邻 hero。✅
- 无连续 ≥3 页 supporting + valley；章节切换处均为 transition。✅
- `N卡片横排` 0 次。✅
- 非对称版式占比 96%（≥40%）；`左大图+右侧文字` + `非对称双栏` 合计 21%（≤40%）。✅
- 任意相邻两页版式不同。✅
- 每页均具备 `role` / `rhythm` / `visual_role` / `anti_pattern` 字段。✅
- 含关键数据页均给出判断（"所以呢"）。✅
- `type: section` 扉页数 = 4 = 目录章节数，编号 01–04 连续且与目录逐字一致。✅
