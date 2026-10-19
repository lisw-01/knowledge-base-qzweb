import re

p = 'STORY.md'
s = open(p, encoding='utf-8').read()

# ---- 1. 长度与分章 ----
s = s.replace('**PPT 长度**：37 页（封面 + 目录 + 4 章 + 结束页）。Hero 页 7 页，占比 21%。',
              '**PPT 长度**：46 页（封面 + 目录 + 4 章 + 结束页）。Hero 页 9 页，占比 20%。')
s = s.replace('**页面总数与分章（37 页 / 4 章）**', '**页面总数与分章（46 页 / 4 章）**')
s = s.replace('| 第 3 章 Pi Agent：一个极简范式 | 20–29 | 10 |',
              '| 第 3 章 Pi Agent：一个极简范式 | 20–38 | 19 |')
s = s.replace('| 第 4 章 落地实践：智数问答 agent-DQ | 30–36 | 7 |',
              '| 第 4 章 落地实践：智数问答 agent-DQ | 39–45 | 7 |')
s = s.replace('| 结束页 | 37 | 1 |', '| 结束页 | 46 | 1 |')

# ---- 2. 契约表 ----
s = s.replace('`03 · Pi Agent：一个极简范式` | 20–29 |', '`03 · Pi Agent：一个极简范式` | 20–38 |')
s = s.replace('| 第 30 页 |', '| 第 39 页 |')
s = s.replace('`04 · 落地实践：智数问答 agent-DQ` | 30–36 |', '`04 · 落地实践：智数问答 agent-DQ` | 39–45 |')

# ---- 3. Hero ----
s = s.replace(
    '**Hero 页定位（7 页 / 19%）：** 01（封面）· 12（Agent 公式）· 16（七层地图）· 22（418 行核心）· 24（完整数据流）· 32（三级路由）· 37（结束页）。\n间隔校验：01→12→16→22→24→32→37，任意两个 Hero 之间至少隔 1 页 Supporting。✅',
    '**Hero 页定位（9 页 / 20%）：** 01（封面）· 12（Agent 公式）· 16（七层地图）· 22（418 行核心）· 24（完整数据流）· 26（模型适配）· 32（双层循环）· 41（三级路由）· 46（结束页）。\n间隔校验：01→12→16→22→24→26→32→41→46，任意两个 Hero 之间至少隔 1 页 Supporting。✅')

# ---- 4. rhythm ----
old_rhythm = re.search(r'^01 peak.*$', s, re.M).group(0)
new_rhythm = ('01 peak｜02 valley｜03 transition｜04 peak｜05 valley｜06 valley｜07 peak｜08 valley｜09 valley｜10 peak｜'
              '11 transition｜12 peak｜13 valley｜14 peak｜15 valley｜16 peak｜17 valley｜18 peak｜19 valley｜'
              '20 transition｜21 valley｜22 peak｜23 valley｜24 peak｜25 valley｜'
              '26 peak｜27 valley｜28 peak｜29 valley｜30 valley｜31 peak｜32 peak｜33 valley｜34 valley｜35 peak｜36 valley｜37 peak｜'
              '38 valley｜39 transition｜40 valley｜41 peak｜42 valley｜43 valley｜44 peak｜45 valley｜46 peak')
s = s.replace(old_rhythm, new_rhythm)

# ---- 5. 版式预算 ----
s = s.replace('**非对称版式预算：** 内容页 32 页中 30 页使用非对称版式（94% ≥ 40%）。✅',
              '**非对称版式预算：** 内容页 41 页中 38 页使用非对称版式（93% ≥ 40%）。✅')
s = s.replace('**`N卡片横排` 出现次数：** 2（第 04 页 role 四卡、第 28 页上二下一，≤2）。✅',
              '**`N卡片横排` 出现次数：** 1（第 04 页 role 四卡，≤2）。✅')
s = s.replace('**`左大图+右侧文字` + `非对称双栏` 合计：** 7 页（`非对称双栏` 于 06/14/18/21/29/31/34），占 19%（≤40%）。✅',
              '**`左大图+右侧文字` + `非对称双栏` 合计：** 12 页（06/14/18/21/26/28/30/31/34/36/37/38），占 29%（≤40%）。✅')

# ---- 6. 表格行：26-28 换成 12 行，原 29-37 顺延 +9 ----
new_rows = [
 '| 26 | 模型适配：40 家厂商，一个 stream() | content | hero | peak | 非对称双栏 | Table(事件映射) + 类型清单 | anchor | 字数约380 / 图1 / 留白16% | 禁止只说"做了归一化"不给映射表；禁止把适配层讲成 SDK 包装 | 统一类型 + 归一化事件流。核心是 type 的翻译：anthropic 的 content_block_start / delta / stop 怎么映射成 text / thinking / toolcall 三组事件；没有边界语义的厂商由适配器合成边界；终止原因折叠成枚举；每个 delta 都带 partial 快照。判断：适配层只产出两样东西，上层就稳了。 |',
 '| 27 | 兼容开关与 never-throw | content | supporting | valley | 左表右卡 | Table(8 开关) + 卡片组 | evidence | 字数约340 / 图0 / 留白18% | 禁止把 compat 讲成"配置项罗列"；禁止不提残缺从哪来 | 8 个 compat 开关逐项对照（developer 角色、reasoning_effort、流中 usage、finish_reason、maxTokens 字段名、工具结果补字段…）；never-throw 把异常塞进事件流；lazyApi 按需加载 SDK；四级鉴权优先级。判断：OpenAI 兼容服务各有各的残缺，开关表就是排查表。 |',
 '| 28 | 上下文工程：每一行常驻都要付租金 | content | supporting | peak | 左堆栈右双卡 | Diagram(五层系统提示) | anchor | 字数约360 / 图1 / 留白16% | 禁止把分层组装写成"拼接字符串"；禁止只讲 Skills 不讲成本 | 系统提示五层：内核基础提示 <1000 token → AGENTS.md（从 cwd 向上遍历发现）→ SYSTEM.md → APPEND_SYSTEM.md → Skills 目录；Skills 只有 name+description 常驻，正文按需；Prompt 模板即文件版斜杠命令。判断：1/3 上下文是四件事叠加出来的。 |',
 '| 29 | compaction：压缩有损，日志无损 | content | supporting | valley | 左右双栏 | Diagram(双触发) + 摘要模板 | evidence | 字数约380 / 图1 / 留白14% | 禁止把压缩讲成"截掉旧消息"；禁止不提切点规则 | 双触发（threshold 提前压 / overflow 事后压）；切点三规则（凑够 keepRecentTokens、绝不在 toolResult 切、split turn 补前缀摘要）；结构化摘要六段模板 + 增量合并 + 文件清单兜底；JSONL 只追加 compaction entry。 |',
 '| 30 | 工具系统：三种视角，四段流水 | content | supporting | valley | 左类型右流水线 | Diagram(四阶段流水线) | anchor | 字数约360 / 图0 / 留白16% | 禁止把工具讲成"函数列表"；禁止只说四阶段不说是谁在跑 | AgentTool 三种视角（给模型 / 给人 / 给 UI）；四阶段：Prepare 校验+钩子 → Execute → Finalize 改写 → 截断保护；默认只挂 4 个工具。判断：四阶段是核心循环在 execute 外面套的包装，不是工具的方法。 |',
 '| 31 | 会话系统：追加日志，树形分叉 | content | supporting | peak | 左代码右双卡 | CodeBlock(JSONL 树) | evidence | 字数约340 / 图1 / 留白16% | 禁止把会话讲成"存个 JSON"；禁止不提分叉价值 | 一条 entry 一行、只追加；parent 指针长成树，navigateTree 可在任意历史消息分叉；SessionManager 五种姿势；Runtime 四条替换路径（都先触发 before_switch / before_fork）；远程租约。 |',
 '| 32 | Agent 循环：418 行，两层 while | content | hero | peak | 左代码右说明 | CodeBlock(循环骨架) | anchor | 字数约330 / 图1 / 留白16% | 禁止把循环讲成"while true 调模型"；禁止不解释外层存在的原因 | 外层跑续跑、内层跑工具循环；五步：turn_start → 队列注入 → stream → 执行工具 → turn_end + 停止判定；Thought 是三段（transformContext / convertToLlm / stream）。判断：418 行里没有一行智能，全是调度。 |',
 '| 33 | 插话不打断，停止靠原语 | content | supporting | valley | 左表右清单 | Table(steer vs followUp) | evidence | 字数约360 / 图0 / 留白16% | 禁止把插话讲成"中断重来"；禁止把停止条件写成单一判断 | steer / followUp 的区别只在进队时机；谁消费取决于进队时循环死没死（内层活着内层消费，内层退了外层消费）；四类停止原语：stopReason / shouldStopAfterTurn / abort / 截断保护。 |',
 '| 34 | 扩展系统：一个函数，一张虚拟模块表 | content | supporting | valley | 左代码右方案 | CodeBlock(VIRTUAL_MODULES) | anchor | 字数约340 / 图1 / 留白16% | 禁止只讲 registerTool 不讲加载机制；禁止不提双实例问题 | 扩展 = export default (pi) => {}；三种形态 + 四个发现位置；virtual modules：jiti 解析 import 时先查表，命中返回宿主正在运行的模块对象；双实例灾难（两个事件总线、拦截静默失效）。 |',
 '| 35 | 事件系统：两套事件，四档粒度 | content | supporting | peak | 左四档右对比 | Table(四档事件) | evidence | 字数约380 / 图0 / 留白14% | 禁止把两套事件讲成平行词表；禁止混淆 toolcall_delta 与 tool_execution_* | AgentEvent 10 种按 run / turn / message / execution 四档；产品层再叠 queue_update、compaction、auto_retry；message_* 是 AssistantMessageEvent 的信封；钩子不是事件。判断：内核不认识任何一个消费者。 |',
 '| 36 | 安全外置：三道防线，一本账 | content | supporting | valley | 左哲学右可观测 | Diagram(三道防线) | evidence | 字数约360 / 图1 / 留白16% | 禁止把"无沙箱"讲成"没有安全"；禁止只讲防线不讲记账 | 无沙箱哲学 + 代价；三道防线：容器隔离（最硬）→ 钩子拦截（最灵活）→ 工具白名单（最简单）；可观测：usage 挂在消息上、telemetry 抽象、evals 回归。 |',
 '| 37 | 远程会话栈：同一套 Agent，换个壳 | content | supporting | peak | 左协议右架构 | CodeBlock(帧格式) + Diagram(五层) | anchor | 字数约340 / 图1 / 留白16% | 禁止把远程栈讲成"加个 WebSocket"；禁止不提 server 复用 AgentSession | CBOR 帧（4 字节长度头 + payload）+ ByteTransport 传输无关 + TranscriptItem 归一化 + 快照 / 增量 + 会话租约；server 不重写循环。判断：本地 IPC 用 stdio RPC 就够。 |',
]

lines = s.split('\n')
out = []
inserted = False
for ln in lines:
    m = re.match(r'^\| (\d{2}) \|', ln)
    if m:
        n = int(m.group(1))
        if n in (26, 27, 28):
            if n == 26 and not inserted:
                out.extend(new_rows)
                inserted = True
            continue
        if 29 <= n <= 37:
            ln = re.sub(r'^\| \d{2} \|', '| %02d |' % (n + 9), ln)
    out.append(ln)
s = '\n'.join(out)

# ---- 7. Checklist ----
s = s.replace('- Hero 页 7 / 33 = 21%（20–30% 区间内）；封面与结束页为 hero；无相邻 hero。✅',
              '- Hero 页 9 / 46 = 20%（15–30% 区间内）；封面与结束页为 hero；无相邻 hero。✅')
s = s.replace('- `N卡片横排` 0 次。✅', '- `N卡片横排` 1 次（第 04 页）。✅')
s = s.replace('- 非对称版式占比 96%（≥40%）；`左大图+右侧文字` + `非对称双栏` 合计 21%（≤40%）。✅',
              '- 非对称版式占比 93%（≥40%）；`左大图+右侧文字` + `非对称双栏` 合计 29%（≤40%）。✅')

open(p, 'w', encoding='utf-8').write(s)
print('story updated')
