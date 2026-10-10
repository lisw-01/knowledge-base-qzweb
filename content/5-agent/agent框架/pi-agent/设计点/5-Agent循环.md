---
title: 设计点5-Agent循环
date: 2026-10-08
tags:
  - Agent
  - pi-agent
  - 设计点
description: Pi 的 Agent 循环：双层 while、steering/followUp 消息队列、停止控制原语
---

# 设计点 5：Agent 循环（内核中的内核）

> 核心一句话：**Pi 的核心就一个约 418 行的双层 while 循环——内层跑"工具调用循环"，外层跑"续跑循环"；用户的插话和追问全部变成队列消息注入，而不是硬中断**。
> 系列：[[0-Pi Agent总览]] ｜ 对应（2）之⑤控制层 ｜ 上一篇 [[4-会话系统]] ｜ 下一篇 [[6-扩展系统]] ｜ 源码细节：[[3-Pi Agent分析]] §2

## 一、这个设计点解决什么问题

手写过 ReAct Agent 的人都知道（见 [_Demo.阶段1&2](../../Agent/_Demo.阶段1&2)），循环本身不难：

```
while True: 调LLM → 解析Action → 执行工具 → 拼回Observation → 直到Answer
```

难的是三个真实问题：

| 问题 | 白话版 |
|------|--------|
| 任务做完了吗？ | 模型输出 Answer 就停？那用户紧接着的追问呢？ |
| 中途插话怎么办？ | 生成到一半用户说"不对，换个思路"——杀掉重来，还是先听完？ |
| 怎么停得干净？ | 死循环、超长输出、用户按 Esc，各自怎么收场？ |

Pi 的答案：**循环拆两层，插话变队列，停止变钩子**。

## 二、双层循环结构（agent-loop.ts）

```
runAgentLoop()
│
├─ 外层循环（续跑）：agent 本应停止后，队列里还有 follow-up 消息？→ 继续跑
│
└─ 内层循环（干活）：一个 turn 接一个 turn
     ① 发 turn_start 事件
     ② 注入 pending 消息（steering / follow-up）
     ③ streamAssistantResponse()
          transformContext → convertToLlm → 调 pi-ai stream
          逐事件发 message_start / message_update / message_end
     ④ 执行本轮的工具调用（sequential 或 parallel）
     ⑤ 发 turn_end → 检查 shouldStopAfterTurn 钩子 → 轮询 steering 队列
```

- **内层管"一个任务的工具循环"**：调模型 → 执行工具 → 把结果拼回去 → 再调模型
- **外层管"多轮续跑"**：一个 run 正常结束后，如果队列里还有排队的追问，作为新输入继续跑——单层循环写不出这种"答完接着聊"

### 代码骨架（约 418 行的结构还原，注释标注每段机制）

```typescript
async function runAgentLoop(agent: Agent): Promise<void> {
  // ═══ 外层循环：续跑循环（"答完接着聊"） ═══
  while (true) {
    // ── 内层循环：一个任务的工具循环（教科书 ReAct 的本体） ──
    while (true) {
      emit("turn_start");                                 // ①

      // ② 注入点：drain PendingMessageQueue
      //    steer（运行中纠偏）和 followUp（追问）都变成一条 UserMessage
      const pending = queue.drain();                      // "all" 或 "one-at-a-time"
      messages.push(...pending);                          // 模型只看到"上下文里多了你的话"

      // ③ 流式调模型 = Thought 的产生地
      //    transformContext → convertToLlm → pi-ai stream（40 家厂商抹平成一个调用）
      //    逐事件发 message_start / message_update / message_end
      const assistant = await streamAssistantResponse(model, context);
      // 返回 AssistantMessage，带 stopReason：
      //   stop | length | toolUse | error | aborted | deferred

      // ④ 执行本轮的工具调用 = Action → Observation
      if (assistant.stopReason === "toolUse") {
        for (const call of assistant.toolCalls) {
          // 四阶段流水线（不内联在 loop 里，是 execute 外面的包装）：
          // Prepare（校验+beforeToolCall）→ execute → Finalize（afterToolCall）→ 截断保护
          const result = await pipeline.execute(call);
          messages.push(result);                          // 成败都拼回上下文 = Observation
        }
      }

      emit("turn_end");

      // ⑤ 停止判定：三个出口
      if (assistant.stopReason !== "toolUse") break;      // 模型说停 → 内层退出
      if (await hooks.shouldStopAfterTurn()) break;      // 宿主钩子叫停（预算/时间/外部信号）
    }

    // ═══ 外层逻辑：run 正常结束后，队列里还有排队的 followUp？ ═══
    if (!queue.hasFollowUp()) break;                      // 没有 → 整个循环结束
    // 有 → 消费掉，回到外层 while 顶部，作为新输入续跑
  }

  emit("agent_end", { willRetry });
}
```

### 逐段拆解

- **③ `streamAssistantResponse()` 是 "Thought"**：不是一次 `chat()` 完事，而是三步——`transformContext`（宿主改上下文）→ `convertToLlm`（AgentMessage 折叠成 LLM 原生 Message）→ pi-ai 层 `stream()`。失败走 never-throw：编码成流上的 `error` 事件（stopReason=error），循环里不用 try/catch
- **④ 工具段是 "Action → Observation"**：`stopReason === "toolUse"` 才执行，结果无条件拼回 `messages`——成功失败都一样（`isError` 标记），即"错误即信息"；每个工具按 `executionMode` 决定 sequential / parallel
- **② 注入点是插话的全部机制**：队列 drain 发生在 turn 边界，抢的是"两轮之间"，不抢正在生成的轮次；内层活着内层消费，内层退了外层消费——同一套 drain 逻辑，谁活着谁注入
- **⑤ 停止是三类原语的组合**（见第四节），不是单一条件：`stopReason`（模型说停）、`shouldStopAfterTurn` 钩子（宿主叫停，终止条件外置）、`abort()`（用户 Esc 硬中断，signal 一路传到流和工具）
- **截断保护在工具段之前**：`stopReason === "length"` 时 `failToolCallsFromTruncatedMessage` 把所有 tool call 直接标记失败，残缺参数绝不执行

### ④ 工具段展开：`for (call of toolCalls)` 逐行读 + 流水线内部的钩子

```typescript
for (const call of assistant.toolCalls) {
  // 四阶段流水线（不内联在 loop 里，是 execute 外面的包装）
  const result = await pipeline.execute(call);
  messages.push(result);      // 成败都拼回上下文 = Observation
}
```

**1. `for` 在遍历什么**：一条 AssistantMessage 可以带 **N 个** toolCall（模型一次说要调 3 个工具），循环逐个执行。骨架写成顺序 `for` 是简化——真实调度看每个工具的 `executionMode`（`sequential` / `parallel`）。

**2. `pipeline.execute(call)` 是黑盒入口**：四阶段不写在 loop 里，loop 只看到"toolCall 进 → result 出"，所有横切逻辑藏在流水线内部：

```
agent loop（调度层）         pipeline（包装层）                      工具（业务层）
                     ┌───────────────────────────────────────┐
pipeline.execute ──→ │ ① Prepare：Schema 校验 + beforeToolCall   │
(call)               │    钩子返回 block？→ 不执行，reason 包装   │
                     │    成失败 result 直接返回                  │
                     │ ② Execute：tool.execute()  ─────────────┼──→ 工具作者写的
                     │ ③ Finalize：afterToolCall 钩子，可改写    │    业务逻辑
                     │    content / isError / terminate         │
                     │ ④ 截断保护：stopReason=length → 短路，    │
                     │    全部标记失败，绝不进②                   │
                     └───────────────┬───────────────────────┘
                                     ↓
                           AgentToolResult（永不抛异常）
```

**3. 流水线内部的钩子：为什么能干预循环**

| 钩子 | 阶段 | 循环的行为 | 返回值语义 |
|---|---|---|---|
| `beforeToolCall`（扩展事件 `tool_call`） | ① Prepare | **停下来 await 返回值** | `{ block: true, reason }` → ② 不执行，reason 作错误 Observation 回喂模型；`undefined` → 放行 |
| `afterToolCall`（扩展事件 `tool_result`） | ③ Finalize | **停下来 await 返回值** | 返回新 result → 覆盖原结果进上下文；`undefined` → 原样放行 |

钩子能改变控制流的机制：**不是事件系统有魔力，是循环在流水线固定位置"等"钩子的返回值**。对比同位置发射的广播型事件 `tool_execution_start/update/end`——fire-and-forget，发完继续走。事件给旁观者（TUI/日志），钩子给参与者（扩展），见 [[7-事件系统]] §二。

三种典型路径走一遍：

| 场景 | 流程 | loop 拿到的 result |
|---|---|---|
| 正常 | ①过 → ②执行 → ③改写 → 返回 | 成功结果 |
| 钩子拦截 | ①返回 block → **② 根本不执行** | 失败结果（reason 是钩子写的文案） |
| 输出被截断 | ④短路 → **② 根本不执行** | 失败结果（半截参数不执行） |

**4. `messages.push(result)` 是这段代码的灵魂**：没有 if、没有 try/catch——`pipeline` 的契约是**永不抛异常**：成功、拦截、执行失败、截断保护，四种情况全部收敛成一个带 `isError` 标记的 `AgentToolResult`，走同一条返回通道。失败不中断循环，错误文本就是给模型看的 Observation，下一轮模型自己决定修参数、换工具还是放弃——**分支决策外包给了模型**。

**5. 三层各写各的**：

| 层 | 写什么 | 不用知道 |
|---|---|---|
| agent loop | 调度：遍历、push、下一轮 | 校验？钩子？截断？全不知道 |
| pipeline | 横切：校验、钩子调度、兜底 | 业务逻辑是什么 |
| 工具作者 | 只写 `execute()` 本体 | 校验和钩子框架替他跑 |

类比 Express：loop 是路由分发，pipeline 是 middleware 链，`tool.execute()` 是 handler——handler 作者永远只见业务，横切关注全在链上。loop 能压在 418 行的原因：所有"每次工具调用都要做的事"被抽进包装层，loop 只剩纯调度。流水线四阶段的完整展开（各阶段应用场景/参数含义/示例）→ [[3-工具系统]] §三。

### 与教科书 ReAct 的差异

教科书版是 `while True: LLM → parse Action → execute → 拼 Observation → 直到 Answer`，Pi 的改进全在"循环之外"：

1. **单层变双层**——`Answer` 不是终点，队列里的追问由外层续跑消费
2. **插话不打断**——运行中用户输入进 steering 队列，下一 turn 边界注入，上下文不断裂
3. **停止原语化**——max_turns / 超时 / 预算这类终止条件全部挪进 `shouldStopAfterTurn` 钩子，内核只认 stopReason + 钩子 + abort
4. **每一步都是事件**——turn_start/end、message_update、tool_execution_* 全程广播，UI 流式渲染就是订阅这些事件（见 [[7-事件系统]]）

> 一句话：**418 行里没有一行"智能"，全是调度——智能在模型，循环只负责把模型、工具、队列、钩子在正确的时机接到一起**。

## 三、steer 与 followUp：插话的两种姿势

|      | steer（转向）             | followUp（追问）           |
| ---- | --------------------- | ---------------------- |
| 进队时机 | agent **正在跑**时        | agent 空闲 / run 尾声时     |
| 语义   | 纠偏当前任务："别用方案A，改用B"    | 追问 / 接续任务："好，那再帮我加上测试" |
| UI   | `/steer` 命令 / 输入框直接打字 | 输入框直接打字                |

- 两者都进 `PendingMessageQueue`，支持两种 drain 策略：`all`（一次全注入）/ `one-at-a-time`（一次一条）
- `queue_update` 事件让 UI 实时显示排队情况（steering / followUp 分组显示）

**两种姿势的区别只在"进队时机 + 语义标签"，生效机制完全相同**：都由队列统一 drain，在下一个注入点（turn 边界 ②）往 `messages` 加一条 UserMessage——模型只看到"上下文里多了你的话"，不区分 steer / followUp。真正决定何时生效的，是**消息进队时循环还活着没有**：

| 进队时循环的状态 | 谁消费 | 生效方式 |
|---|---|---|
| 内层在跑（steer） | 内层循环 | 当前这轮说完，下一 turn 边界注入，任务继续 |
| 内层在跑（run 尾声排进的 followUp） | 内层循环 | 同样下一 turn 边界注入，**run 并不结束** |
| 内层已退出（空闲期排进的 followUp） | 外层循环 | 作为新输入续跑（"答完接着聊"） |

即 **followUp ≠ 必然等 run 结束**——"当前 run 结束后作为新输入"只适用于第三行。内外层消费同一个队列、复用同一条注入逻辑，谁活着谁注入，任何时刻插话都不丢、不延迟。

> **Pi 默认的插话姿势就是队列注入（不打断）**：运行中打字默认进 steer 队列（`/steer` 只是显式语法糖）；空闲打字默认 prompt 开新 run 或 followUp 排队。注入点固定在 turn 边界，不抢当前正在生成的轮次。想立即停用 `abort()`（Esc）——那是停止原语，和插话语义彻底分开：插话走队列保上下文，叫停走 abort。

> 设计精髓：**"打断"不是杀死进程，而是把话塞进队列**。模型下一轮自然看到你的话——上下文不断裂，不需要任何恢复逻辑，abort 语义和纠偏语义彻底分开。

## 四、停止控制：四类原语

| 机制 | 作用 |
|------|------|
| `stopReason` | 模型自己说停：`stop`（说完）/ `length`（到长度）/ `toolUse`（要调工具继续）/ `error` / `aborted` / `deferred` |
| `shouldStopAfterTurn` 钩子 | 每个 turn 结束问一次宿主"还要继续吗"——预算、时间、外部信号都可以在这里叫停 |
| `abort()` | 硬中断当前运行（用户按 Esc）；`waitForIdle()` 等运行与监听器全部沉淀后再收尾 |
| 截断保护 | `stopReason = length` 时 `failToolCallsFromTruncatedMessage`：让所有 tool call 直接失败，**绝不执行可能被截断的残缺参数** |

## 五、工具调用失败了怎么办：API 工具的错误重试

先明确机制边界：**Pi 的 auto-retry 只在 LLM 调用层**（settings `retry.maxRetries` + 退避 + `auto_retry_start/end` 事件），**工具层默认不重试**——工具失败返回带 `isError` 的 `AgentToolResult` 回喂模型，下一步由模型决定（"错误即信息"，见 [[3-工具系统]]）。要给"调外部 API 的工具"加 500 重试，有两条路：

### 路径 1：`execute()` 内部退避重试（管一个工具，确定性高）

```typescript
pi.registerTool({
  name: "fetch_api",
  label: "Fetch API",
  description: "调用内部 API 服务",
  parameters: Type.Object({ url: Type.String() }),
  execute: async (_toolCallId, params, signal, onUpdate, _ctx) => {
    const MAX_RETRIES = 3, BASE_DELAY_MS = 1000;
    let lastError = "";
    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      if (signal?.aborted) break;                      // 用户 Esc → 中止语义优先于重试
      try {
        const res = await fetch(params.url, { signal });
        if (res.ok) return { content: [{ type: "text", text: await res.text() }], details: {} };
        if (res.status < 500) {                        // 4xx 是请求本身错了，快速失败
          return { content: [{ type: "text", text: `HTTP ${res.status}` }], details: {}, isError: true };
        }
        lastError = `HTTP ${res.status}`;              // 5xx → 瞬时故障，可重试
      } catch (e) { lastError = String(e); }           // 网络错误/超时 → 同样按瞬时处理
      const delay = BASE_DELAY_MS * 2 ** (attempt - 1);  // 指数退避 1s/2s/4s
      if (attempt < MAX_RETRIES) {
        await onUpdate?.({ message: `请求失败（${lastError}），${delay}ms 后重试第 ${attempt + 1} 次…` });
        await new Promise((r) => setTimeout(r, delay));
      }
    }
    // 最终失败：不 throw，返回 isError 结果 → 模型下一轮自行决策
    return { content: [{ type: "text", text: `API 请求失败（已重试 ${MAX_RETRIES} 次）：${lastError}` }], details: {}, isError: true };
  },
});
```

三个关键点：**`signal` 必须接进去**（中止优先于重试）；**只重试瞬时错误**（5xx/网络超时，4xx 快速失败）；**最终失败返回 `isError` 而不是抛异常**——工具侧的 never-throw。

### 路径 2：钩子层统一处理（一个扩展管所有工具）

限制：按文档化能力，`afterToolCall` / `tool_result` 钩子只能**改写结果**（content/details/isError/terminate），不能透明地替你重新执行工具。所以实际写法是**识别瞬时错误 → 改写错误信息 → 引导模型下一轮自己重试**，可搭配 `tool_call` 钩子做连续失败熔断：

```typescript
pi.on("tool_result", async (event) => {
  if (!event.result.isError) return undefined;
  const text = event.result.content.map((c) => (c.type === "text" ? c.text : "")).join("");
  if (/HTTP 5\d\d|ECONNRESET|ETIMEDOUT/.test(text)) {
    return { ...event.result, content: [{ type: "text",
      text: `${text}\n\n[系统提示] 上游服务瞬时故障，参数本身没问题，请用相同参数重试一次。` }] };
  }
  return undefined;   // 非瞬时错误原样放行
});
```

### 怎么选（可组合：路径 1 兜底硬重试，路径 2 做审计和熔断）

| | 路径 1（execute 内重试） | 路径 2（钩子层） |
|---|---|---|
| 覆盖范围 | 单个工具，逐个写 | 一个扩展管所有工具 |
| 重试时机 | 立即、循环内、带退避 | 下一 turn，由模型决定（多一次 LLM 调用） |
| 确定性 | 高 | 依赖模型"听话" |
| 适合场景 | 知道哪些错误可重试、工具是幂等的 | 给一批现成工具统一加策略，或不能改工具源码 |

> ⚠️ **非幂等工具（write/edit 类）慎用重试**：500 可能是"已执行但响应失败"，盲目重试会重复写入——先确认幂等性或带请求 ID 去重。通用 ReAct 的失败分类 / 熔断 / 护栏全景 → [[（3）ReAct工具调用失败处理]]

## 六、一次完整调用的数据流

```
用户输入 (TUI Editor / RPC client prompt)
  → AgentSession.prompt() ── 持久化 entry
  → Agent.prompt() → runAgentLoop
      outer loop (follow-up)
        inner loop:
          inject steering/follow-up 消息
          streamAssistantResponse: transformContext → convertToLlm → ai 层 streamSimple
            → Provider 解析（lazy 加载 SDK）→ 原生 API 调用
            ← AssistantMessageEvent 流（text/thinking/toolcall delta…）
          message_update → TUI 流式渲染 / RPC assistant_delta 转发
          tool calls → beforeToolCall → execute → afterToolCall
          turn_end → shouldStopAfterTurn → steering 轮询
  → agent_end → waitForIdle → 会话快照广播（server 模式）
```

## 七、设计启示（迁移到你自己的 Agent）

1. **循环分两层**：内层"工具循环" + 外层"续跑循环"——单层 while 写不出"答完追问接着干"
2. **steering 队列值得抄**：用户纠偏是高频需求，"注入消息"比"中断重启"优雅得多，且天然保留完整上下文
3. **shouldStopAfterTurn 是干净的扩展点**：把终止条件从循环内部挪到宿主钩子，预算控制/外部取消都不用碰内核
4. **截断保护常被忽略**：输出被截断时直接执行半截参数是事故源，"失败优于残缺执行"
5. 对照 [[（2）agent开发需要处理的功能点和设计原则]] 的控制层四件套（Answer / 最大轮数 / 超时 / token 预算）：Pi 把它们拆成了 stopReason + 钩子 + abort 三类原语，组合出同样的保障

## 关联阅读

- 工具在循环里怎么被执行 → [[3-工具系统]]
- 工具失败的分类处理与重试全景（通用 ReAct）→ [[（3）ReAct工具调用失败处理]]
- 循环的每个节点怎么被外界观察 → [[7-事件系统]]
- `convertToLlm` 在 LLM 边界做什么 → [[2-上下文工程]]
- 源码级细节（Agent 类 API、AgentHarness）→ [[3-Pi Agent分析]] §2
