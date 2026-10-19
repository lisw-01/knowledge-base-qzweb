# STORY.md — 从 LLM 到 Agent 再到 Pi Agent

## ① 用户意图对齐

- **目标受众**：公司内部研发同学（懂代码、会写工程，但没有系统做过 AI Agent）。现场分享场景，约 40–60 分钟。
- **核心目标**：听完之后，听众能① 说清 LLM、Agent、Pi Agent 三者的递进关系；② 理解 Agent 的能力边界来自"七层工程"而非模型本身；③ 知道 Pi 的极简哲学与它凭什么省 token；④ 看懂 agent-DQ（智数问答）是如何把 Pi 落地成一个真实业务系统，并带走一批可直接复用的踩坑经验。
- **PPT 长度**：46 页（封面 + 目录 + 4 章 + 结束页）。Hero 页 9 页，占比 20%。
- **视觉调性**：科技深色 / 深蓝底 + 青蓝高亮 / 工程感 / 克制 / 数据密集。
- **内容边界**：
  - 必讲：LLM 的无状态与上下文窗口、Function Calling、ReAct、Agent 七层功能地图、十条设计原则、Pi 的极简哲学与分层架构、agent-DQ 的三级路由 / 发现式注册 / 隔离与安全 / SSE 链路、真实踩坑。
  - 不讲：Transformer 内部原理、模型训练与微调、向量数据库选型细节、多 Agent 编排。
  - 禁碰：任何未经文档佐证的数字与结论；不虚构 benchmark。

---

## ② 页面布局骨架

**页面总数与分章（46 页 / 4 章）**

| 章节 | 页码 | 页数 |
| :--- | :--- | :--- |
| 封面 + 目录（前置） | 01–02 | 2 |
| 第 1 章 LLM：一切的地基 | 03–10 | 8 |
| 第 2 章 Agent：从"能聊"到"能干" | 11–19 | 9 |
| 第 3 章 Pi Agent：一个极简范式 | 20–38 | 19 |
| 第 4 章 落地实践：智数问答 agent-DQ | 39–45 | 7 |
| 结束页 | 46 | 1 |

**目录↔章节扉页契约（强制，N=4）**

| 目录条目 | 章节扉页 | 扉页标题（逐字一致） | 页码区间 |
| :--- | :--- | :--- | :--- |
| 01 · LLM：一切的地基 | 第 03 页 | `01 · LLM：一切的地基` | 03–10 |
| 02 · Agent：从"能聊"到"能干" | 第 11 页 | `02 · Agent：从"能聊"到"能干"` | 11–19 |
| 03 · Pi Agent：一个极简范式 | 第 20 页 | `03 · Pi Agent：一个极简范式` | 20–38 |
| 04 · 落地实践：智数问答 agent-DQ | 第 39 页 | `04 · 落地实践：智数问答 agent-DQ` | 39–45 |

→ 4 个 `type: section` 扉页齐全、编号 01–04 连续，与目录逐字一致。✅

**Hero 页定位（9 页 / 20%）：** 01（封面）· 12（Agent 公式）· 16（七层地图）· 22（418 行核心）· 24（完整数据流）· 26（模型适配）· 32（双层循环）· 41（三级路由）· 46（结束页）。
间隔校验：01→12→16→22→24→26→32→41→46，任意两个 Hero 之间至少隔 1 页 Supporting。✅

**rhythm 曲线**

01 peak｜02 valley｜03 transition｜04 peak｜05 valley｜06 valley｜07 peak｜08 valley｜09 valley｜10 peak｜11 transition｜12 peak｜13 valley｜14 peak｜15 valley｜16 peak｜17 valley｜18 peak｜19 valley｜20 transition｜21 valley｜22 peak｜23 valley｜24 peak｜25 valley｜26 peak｜27 valley｜28 peak｜29 valley｜30 valley｜31 peak｜32 peak｜33 valley｜34 valley｜35 peak｜36 valley｜37 peak｜38 valley｜39 transition｜40 valley｜41 peak｜42 valley｜43 valley｜44 peak｜45 valley｜46 peak

→ 无连续 ≥3 页 valley；章节切换处均为 transition。✅

**非对称版式预算：** 内容页 41 页中 38 页使用非对称版式（93% ≥ 40%）。✅
**对称版式预算：** 仅第 10 页使用 `图表+洞察`（1 页 ≤ 2 页上限）；封面 / 章节扉页 / 结束页走自定义版式。✅
**`N卡片横排` 出现次数：** 1（第 04 页 role 四卡，≤2）。✅
**`左大图+右侧文字` + `非对称双栏` 合计：** 12 页（06/14/18/21/26/28/30/31/34/36/37/38），占 29%（≤40%）。✅

---

## ③ 页面大纲

> 契约：本表是 STORY.md 与 slides/*.slide 之间的逐页约定，生成时严格对照。

| # | title | type | role | rhythm | layout | visual | visual_role | density | anti_pattern | description |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 01 | 从 LLM 到 Agent 再到 Pi Agent | cover | hero | peak | 全幅图+骑线文字 | L1: cover_hero.png（全幅底图） | anchor | 字数约40 / 图1 / 留白35% | 禁止居中平铺纯文字；禁止标题右侧塞装饰小图 | 主标题 + 副标题"一条从模型到业务系统的完整链路" + 分享人/日期。一句话点题：模型是原料，Agent 才是产品。 |
| 02 | 目录 | catalog | supporting | valley | 左标题+右内容 | L3: 青蓝角标 | evidence | 字数约150 / 图0 / 留白22% | 禁止四卡片横排；禁止条目只写标题不写看点 | 四章并列，每章一句"听完你能得到什么"。 |
| 03 | 01 · LLM：一切的地基 | section | transition | transition | 全屏视觉+大标题 | L1: sec_llm.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白45% | 禁止铺满正文段落；禁止四卡片预览 | 章节扉页 + 一句导语：不理解 LLM 的无状态，就理解不了 Agent 的上下文工程。 |
| 04 | messages 里的 role：谁在说话 | content | supporting | peak | 四卡横排+代码 | CodeBlock(messages 数组) + 4 张 role 卡 | evidence | 字数约240 / 图1 / 留白20% | 禁止把 role 当日志字段讲；禁止只列四个名字不说回填规则 | system 定规则 / user 提需求 / assistant 留痕 / tool 回事实。判断：role 决定这段话被当成指令、提问、自己的话，还是外部事实。 |
| 05 | LLM 是"无状态的文本预测器" | content | supporting | valley | 左标题+右内容 | Diagram(Token 切分示意 SVG) | evidence | 字数约240 / 图1 / 留白25% | 禁止把 Token/上下文窗口塞进等宽卡片；禁止只给定义不给后果 | 无状态 = 每次请求都要把 messages 完整重发；上下文窗口 = 输入+输出总量上限。判断：Agent 里上下文膨胀是必然，不是意外。 |
| 06 | 四个必须先记住的概念 | content | supporting | valley | 非对称双栏 | FAIcon列表（4 项） | evidence | 字数约300 / 图0 / 留白22% | 禁止等宽四卡横排；禁止只罗列术语 | Prompt 定角色与格式、Temperature=0 保确定性、幻觉要靠工具真实数据压制、Embedding 是长期记忆的检索底座。判断：这四点决定了 Agent 的稳定性上限。 |
| 07 | 两种调用方式：对话 vs 工具调用 | content | supporting | peak | 左标题+右内容 | Diagram(两条链路对比 SVG) | evidence | 字数约260 / 图1 / 留白24% | 禁止 50:50 等分双栏；禁止把工具调用写成"高级对话" | 普通对话只出文本；工具调用让模型输出结构化参数、由你的代码真正执行。判断：这一步是"聊天机器人"与"Agent"的分水岭。 |
| 08 | 方案 A：手写 Prompt 的 ReAct 循环 | content | supporting | valley | 上大图+下方卡片 | CodeBlock(Python) + L2 踩坑卡 | anchor | 字数约280 / 图1 / 留白20% | 禁止把代码缩成 200×70 装饰贴片；禁止只贴代码不讲坑 | 上半部完整 ReAct 循环代码，下半部三张"踩坑实录"卡：模型自演 Observation、正则解析失败、循环耗尽返回 None。判断：格式自己发明，就一定会有不守规矩的一天。 |
| 09 | 方案 B：原生 Function Calling | content | supporting | valley | 左标题+右内容 | CodeBlock(TypeScript/JSON) | evidence | 字数约250 / 图1 / 留白22% | 禁止只讲概念不给 schema；禁止把 Schema 说成"可选优化" | 用 JSON Schema 正式声明工具，模型返回 tool_calls，无需正则。判断：description 就是写给模型看的 API 文档。 |
| 10 | A/B 对比与一条安全红线 | content | supporting | peak | 图表+洞察 | Table(4 行对比) | evidence | 字数约180 / 图1 / 留白28% | 禁止把结论埋在正文里；禁止罗列对比却不给选型建议 | 四维对比 + 选型结论：实际项目一律用原生 Function Calling。安全红线：模型只有建议权，执行权永远在你的代码里。 |
| 11 | 02 · Agent：从"能聊"到"能干" | section | transition | transition | 全屏视觉+大标题 | L1: sec_agent.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白45% | 禁止铺满正文段落；禁止四卡片预览 | 章节扉页 + 导语：Agent 的核心代码就一个 while 循环，真正的开发量全在循环之外。 |
| 12 | Agent = LLM + 工具 + 记忆 + 规划 | content | hero | peak | 巨型数字+洞察 | 大数字公式（≥72px） | anchor | 字数约120 / 图0 / 留白38% | 禁止等宽卡片横排；禁止把公式缩成一句正文 | 巨型公式占据视觉重心，四要素各配一句白话解释。判断：缺任何一项，都只是"会聊天的模型"。 |
| 13 | ReAct：思考 → 行动 → 观察 | content | supporting | valley | 左标题+右内容 | Diagram(循环回路 SVG) | anchor | 字数约230 / 图1 / 留白26% | 禁止把循环画成单向流程图；禁止不给终止条件 | Thought / Action / Observation 三段交替，直到 Answer。判断：循环必须带最大轮数兜底，否则一次死循环烧掉一个月预算。 |
| 14 | 工具与记忆：手脚和上下文 | content | supporting | peak | 非对称双栏 | FAIcon列表 + Diagram(记忆分层) | evidence | 字数约320 / 图1 / 留白20% | 禁止把"工具"讲成函数列表；禁止忽略"工具返回 = 模型可见输入" | 工具：小而专、描述大于实现、参数先校验再执行、错误要回喂。记忆：近期带原文、远期压摘要、事实存卡片、知识进向量库。 |
| 15 | 学习路径：五个阶段 | content | supporting | valley | 上大图+下方卡片 | Diagram(五阶段时间轴 SVG) | anchor | 字数约250 / 图1 / 留白22% | 禁止四卡横排；禁止跳过"手写 ReAct"直接讲框架 | 阶段 1 手写 ReAct → 2 原生 FC → 3 加记忆与 RAG → 4 多工具真实场景 → 5 框架与工程化。判断：先手写再上框架，否则出问题完全不会排查。 |
| 16 | 七层功能地图 | content | hero | peak | 巨型数字+洞察 | 大数字"⑦" + Diagram(七层塔 SVG) | anchor | 字数约160 / 图1 / 留白32% | 禁止把七层压成一行文字；禁止用等宽卡片代替层塔 | ①模型 ②提示 ③工具 ④记忆 ⑤控制 ⑥护栏 ⑦运营。判断：①~⑤ 是搭起来，⑥~⑦ 是别出事、出事能查；换模型只动①，加工具只动③。 |
| 17 | 逐层拆解：每层到底要写什么 | content | supporting | valley | 左标题+右内容 | FAIcon列表（7 行） | evidence | 字数约380 / 图0 / 留白18% | 禁止只列层名不给动作项；禁止单栏线性流水账排版 | 七层各给 2–3 个必须落地的动作项（如①的密钥/重试/流式、③的参数校验/错误回喂、⑤的四个终止条件）。 |
| 18 | 十条设计原则 | content | supporting | peak | 非对称双栏 | Table(10 行，宽侧) | evidence | 字数约300 / 图1 / 留白18% | 禁止把原则写成口号；禁止不给"违背的下场" | 每条原则配一句解释 + 违背后果。判断：前 3 条是架构级（决定项目成败），后 7 条是工程习惯级（决定维护成本）。 |
| 19 | 避坑清单与上线自查 | content | supporting | valley | 左标题+右内容 | FAIcon(check-circle) 双列清单 | evidence | 字数约260 / 图0 / 留白22% | 禁止与上一页原则页版式雷同；禁止清单只写正面表述 | 左列：7 条开发避坑；右列：7 条上线自查。判断：全部打勾，才算从"能跑的 demo"变成"敢给别人用的 Agent"。 |
| 20 | 03 · Pi Agent：一个极简范式 | section | transition | transition | 全屏视觉+大标题 | L1: sec_pi.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白45% | 禁止铺满正文段落；禁止四卡片预览 | 章节扉页 + 导语：自主智能体本质就是 LLM + 工具 + 循环；Pi 把这条公式工程化到了极致。 |
| 21 | Pi 是什么：三个反常识设计 | content | supporting | valley | 非对称双栏 | FAIcon列表（3 项） | evidence | 字数约300 / 图0 / 留白20% | 禁止 50:50 等分；禁止把"刻意不内置"写成功能缺失 | Pi = 极简终端编码代理 + 可复用 Agent 运行时（MIT）。刻意不内置 MCP/子代理/权限弹窗/计划模式/任务清单；无沙箱；上下文极省。判断：不是功能少，是把指导权还给模型。 |
| 22 | 极简的代价与回报 | content | hero | peak | 巨型数字+洞察 | 大数字 418 / 4 / 1/3（≥96px） | anchor | 字数约130 / 图1 / 留白34% | 禁止把三个数字塞进图表角落；禁止只给数字不给解释 | 核心循环约 418 行、系统提示 <1000 token、默认 4 个工具、每轮上下文约为同类工具 1/3。判断：省下来的上下文，就是省下来的钱和准确率。 |
| 23 | 分层架构：严格单向的 monorepo | content | supporting | valley | 左标题+右内容 | Diagram(四层依赖 SVG) | anchor | 字数约240 / 图1 / 留白24% | 禁止把四层画成平铺方块；禁止用 200×70 小图替代架构图 | pi-ai（统一 LLM）→ pi-agent-core（内核）→ pi-coding-agent（产品层）→ pi-tui（终端 UI），外加远程会话栈。判断：做编码类产品用 coding-agent，只要"LLM+工具+循环"的裸内核用 core。 |
| 24 | 一次调用的完整数据流 | content | hero | peak | 上大图+下方卡片 | Diagram(端到端链路 SVG，占满上半) | anchor | 字数约200 / 图1 / 留白20% | 禁止把链路压成单行文字；禁止省略工具四阶段 | 输入 → AgentSession.prompt → 双层 while → transformContext/convertToLlm → streamSimple → 事件回流 → 工具准备/执行/收尾/截断保护 → agent_end。判断：看懂了这条流，就懂了 Pi 的一切扩展点。 |
| 25 | 九个设计点：对应七层地图 | content | supporting | valley | 左标题+右内容 | Table(9 行映射表) | evidence | 字数约280 / 图1 / 留白18% | 禁止只列设计点名不写"解决什么问题"；禁止与七层地图页版式重复 | 模型适配 / 上下文工程 / 工具系统 / 会话系统 / Agent 循环 / 扩展系统 / 事件系统 / 安全与可观测 / 远程会话栈，一一映射到七层。判断：编号即层号——这是刻意的教学设计。 |
| 26 | 模型适配：40 家厂商，一个 stream() | content | hero | peak | 非对称双栏 | Table(事件映射) + 类型清单 | anchor | 字数约380 / 图1 / 留白16% | 禁止只说"做了归一化"不给映射表；禁止把适配层讲成 SDK 包装 | 统一类型 + 归一化事件流。核心是 type 的翻译：anthropic 的 content_block_start / delta / stop 怎么映射成 text / thinking / toolcall 三组事件；没有边界语义的厂商由适配器合成边界；终止原因折叠成枚举；每个 delta 都带 partial 快照。判断：适配层只产出两样东西，上层就稳了。 |
| 27 | 兼容开关与 never-throw | content | supporting | valley | 左表右卡 | Table(8 开关) + 卡片组 | evidence | 字数约340 / 图0 / 留白18% | 禁止把 compat 讲成"配置项罗列"；禁止不提残缺从哪来 | 8 个 compat 开关逐项对照（developer 角色、reasoning_effort、流中 usage、finish_reason、maxTokens 字段名、工具结果补字段…）；never-throw 把异常塞进事件流；lazyApi 按需加载 SDK；四级鉴权优先级。判断：OpenAI 兼容服务各有各的残缺，开关表就是排查表。 |
| 28 | 上下文工程：每一行常驻都要付租金 | content | supporting | peak | 左堆栈右双卡 | Diagram(五层系统提示) | anchor | 字数约360 / 图1 / 留白16% | 禁止把分层组装写成"拼接字符串"；禁止只讲 Skills 不讲成本 | 系统提示五层：内核基础提示 <1000 token → AGENTS.md（从 cwd 向上遍历发现）→ SYSTEM.md → APPEND_SYSTEM.md → Skills 目录；Skills 只有 name+description 常驻，正文按需；Prompt 模板即文件版斜杠命令。判断：1/3 上下文是四件事叠加出来的。 |
| 29 | compaction：压缩有损，日志无损 | content | supporting | valley | 左右双栏 | Diagram(双触发) + 摘要模板 | evidence | 字数约380 / 图1 / 留白14% | 禁止把压缩讲成"截掉旧消息"；禁止不提切点规则 | 双触发（threshold 提前压 / overflow 事后压）；切点三规则（凑够 keepRecentTokens、绝不在 toolResult 切、split turn 补前缀摘要）；结构化摘要六段模板 + 增量合并 + 文件清单兜底；JSONL 只追加 compaction entry。 |
| 30 | 工具系统：三种视角，四段流水 | content | supporting | valley | 左类型右流水线 | Diagram(四阶段流水线) | anchor | 字数约360 / 图0 / 留白16% | 禁止把工具讲成"函数列表"；禁止只说四阶段不说是谁在跑 | AgentTool 三种视角（给模型 / 给人 / 给 UI）；四阶段：Prepare 校验+钩子 → Execute → Finalize 改写 → 截断保护；默认只挂 4 个工具。判断：四阶段是核心循环在 execute 外面套的包装，不是工具的方法。 |
| 31 | 会话系统：追加日志，树形分叉 | content | supporting | peak | 左代码右双卡 | CodeBlock(JSONL 树) | evidence | 字数约340 / 图1 / 留白16% | 禁止把会话讲成"存个 JSON"；禁止不提分叉价值 | 一条 entry 一行、只追加；parent 指针长成树，navigateTree 可在任意历史消息分叉；SessionManager 五种姿势；Runtime 四条替换路径（都先触发 before_switch / before_fork）；远程租约。 |
| 32 | Agent 循环：418 行，两层 while | content | hero | peak | 左代码右说明 | CodeBlock(循环骨架) | anchor | 字数约330 / 图1 / 留白16% | 禁止把循环讲成"while true 调模型"；禁止不解释外层存在的原因 | 外层跑续跑、内层跑工具循环；五步：turn_start → 队列注入 → stream → 执行工具 → turn_end + 停止判定；Thought 是三段（transformContext / convertToLlm / stream）。判断：418 行里没有一行智能，全是调度。 |
| 33 | 插话不打断，停止靠原语 | content | supporting | valley | 左表右清单 | Table(steer vs followUp) | evidence | 字数约360 / 图0 / 留白16% | 禁止把插话讲成"中断重来"；禁止把停止条件写成单一判断 | steer / followUp 的区别只在进队时机；谁消费取决于进队时循环死没死（内层活着内层消费，内层退了外层消费）；四类停止原语：stopReason / shouldStopAfterTurn / abort / 截断保护。 |
| 34 | 扩展系统：一个函数，一张虚拟模块表 | content | supporting | valley | 左代码右方案 | CodeBlock(VIRTUAL_MODULES) | anchor | 字数约340 / 图1 / 留白16% | 禁止只讲 registerTool 不讲加载机制；禁止不提双实例问题 | 扩展 = export default (pi) => {}；三种形态 + 四个发现位置；virtual modules：jiti 解析 import 时先查表，命中返回宿主正在运行的模块对象；双实例灾难（两个事件总线、拦截静默失效）。 |
| 35 | 事件系统：两套事件，四档粒度 | content | supporting | peak | 左四档右对比 | Table(四档事件) | evidence | 字数约380 / 图0 / 留白14% | 禁止把两套事件讲成平行词表；禁止混淆 toolcall_delta 与 tool_execution_* | AgentEvent 10 种按 run / turn / message / execution 四档；产品层再叠 queue_update、compaction、auto_retry；message_* 是 AssistantMessageEvent 的信封；钩子不是事件。判断：内核不认识任何一个消费者。 |
| 36 | 安全外置：三道防线，一本账 | content | supporting | valley | 左哲学右可观测 | Diagram(三道防线) | evidence | 字数约360 / 图1 / 留白16% | 禁止把"无沙箱"讲成"没有安全"；禁止只讲防线不讲记账 | 无沙箱哲学 + 代价；三道防线：容器隔离（最硬）→ 钩子拦截（最灵活）→ 工具白名单（最简单）；可观测：usage 挂在消息上、telemetry 抽象、evals 回归。 |
| 37 | 远程会话栈：同一套 Agent，换个壳 | content | supporting | peak | 左协议右架构 | CodeBlock(帧格式) + Diagram(五层) | anchor | 字数约340 / 图1 / 留白16% | 禁止把远程栈讲成"加个 WebSocket"；禁止不提 server 复用 AgentSession | CBOR 帧（4 字节长度头 + payload）+ ByteTransport 传输无关 + TranscriptItem 归一化 + 快照 / 增量 + 会话租约；server 不重写循环。判断：本地 IPC 用 stdio RPC 就够。 |
| 38 | 三层定制能力 | content | supporting | valley | 非对称双栏 | FAIcon列表（3 路线） | evidence | 字数约300 / 图0 / 留白20% | 禁止等宽三卡横排；禁止不给成本量级 | Skills（小时级，沉淀团队经验）→ Extensions（天级，加工具与拦截）→ SDK（周级，嵌进自有产品）。判断：先问"我要改造哪一层"，再选路线。 |
| 39 | 04 · 落地实践：智数问答 agent-DQ | section | transition | transition | 全屏视觉+大标题 | L1: sec_practice.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白45% | 禁止铺满正文段落；禁止四卡片预览 | 章节扉页 + 导语：把前面所有知识，装进一个真实业务系统。 |
| 40 | 项目概览：一句话与一套栈 | content | supporting | valley | 非对称双栏 | Diagram(架构总览 SVG) | evidence | 字数约300 / 图1 / 留白20% | 禁止 50:50 等分；禁止把技术栈写成 logo 墙 | 自然语言 → PI 理解意图并调工具 → 前端流式渲染文本/表格/图表/KPI。栈：Vue3+TS+Pinia / Node+Koa / @earendil-works/pi-coding-agent / 内存种子数据。判断：PI 是编排核心，不是外挂组件。 |
| 41 | 三级路由：准确性的核心 | content | hero | peak | 巨型数字+洞察 | 大数字"三级" + Diagram(路由决策 SVG) | anchor | 字数约200 / 图1 / 留白26% | 禁止让模型"自由选工具"；禁止把三级写成并列三卡 | ①业务 API → ②指标模板 → ③受控 SQL，不得跳级；缺参不调工具、先向用户索要。判断：把"选哪条路"从模型手里收回来，是准不准的关键。 |
| 42 | 发现式注册：加工具 = 丢一个文件 | content | supporting | valley | 左标题+右内容 | CodeBlock(扩展注册) + 目录树 | evidence | 字数约260 / 图1 / 留白22% | 禁止把注册机制讲成"配置数组"；禁止只贴代码不讲发现路径 | `.pi/extensions/*.ts` 由 DefaultResourceLoader 自动发现；`.pi/AGENTS.md`、`APPEND_SYSTEM.md` 自动合并进系统提示；代码里零硬编码工具数组。判断：新增能力不改主干代码，是低耦合的落地方式。 |
| 43 | 隔离与安全：租户 · 范围 · SQL 守卫 | content | supporting | valley | 非对称双栏 | Diagram(三层防线 SVG) | evidence | 字数约320 / 图1 / 留白20% | 禁止把安全写成"加了个校验"；禁止省略"PI 层无感知" | 数据范围：JWT → 显式传参 → scoper 强制注入 tenant_id + 部门；会话归属校验防越权读历史；SQL 经 node-sql-parser AST 校验（仅 SELECT/表白名单/强制 limit/AST 级注入范围）。判断：PI 层无感知、无法绕过，安全才成立。 |
| 44 | 流式链路与前端渲染扩展 | content | supporting | peak | 上大图+下方卡片 | Diagram(SSE 链路 SVG) + CodeBlock(契约) | anchor | 字数约240 / 图1 / 留白20% | 禁止把 SSE 讲成"轮询的替代品"；禁止省略事件契约 | session.subscribe → event-bus 映射 → SSE 事件契约（text_delta/thinking_delta/render/error/turn_reset/done）→ 前端按 renderer 路由 Text/Table/Chart/KPI。判断：后端只管发结构化事件，前端注册表决定长什么样。 |
| 45 | 踩坑实录：四个真实 Bug | content | supporting | valley | 左标题+右内容 | FAIcon列表（4 条）+ 大数字编号 | evidence | 字数约330 / 图1 / 留白18% | 禁止把踩坑写成"注意事项"；禁止只讲现象不讲根因与修法 | ① jiti 加载导致 ALS 实例隔离 → 彻底显式传参；② 事件订阅重复导致每字双倍 → attach 先 detach；③ 模型层 429 被静默吞掉 → message_end 兜底推错；④ 空结果被降级重试 → 双层熔断。判断：Agent 的坑大多不在模型，在"边界"。 |
| 46 | 模型是原料，工程才是产品 | ending | hero | peak | 全屏视觉+大标题 | L1: ending_hero.png（全幅底图） | atmosphere | 字数约40 / 图1 / 留白42% | 禁止堆砌致谢名单；禁止把结论写成流程回顾 | 收束金句 + 三段式回顾（模型/工程/落地）+ 落款与 Q&A。 |

**Checklist 自检**
- Hero 页 9 / 46 = 20%（15–30% 区间内）；封面与结束页为 hero；无相邻 hero。✅
- 无连续 ≥3 页 supporting + valley；章节切换处均为 transition。✅
- `N卡片横排` 1 次（第 04 页）。✅
- 非对称版式占比 93%（≥40%）；`左大图+右侧文字` + `非对称双栏` 合计 29%（≤40%）。✅
- 任意相邻两页版式不同。✅
- 每页均具备 `role` / `rhythm` / `visual_role` / `anti_pattern` 字段。✅
- 含关键数据页均给出判断（"所以呢"）。✅
- `type: section` 扉页数 = 4 = 目录章节数，编号 01–04 连续且与目录逐字一致。✅
