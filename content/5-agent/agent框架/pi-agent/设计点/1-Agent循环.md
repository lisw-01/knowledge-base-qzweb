---
title: 设计点1-Agent循环
date: 2026-10-08
tags:
  - Agent
  - pi-agent
  - 设计点
description: Pi 的 Agent 循环：双层 while、steering/followUp 消息队列、停止控制原语
---

# 设计点 1：Agent 循环（内核中的内核）

> 核心一句话：**Pi 的核心就一个约 418 行的双层 while 循环——内层跑"工具调用循环"，外层跑"续跑循环"；用户的插话和追问全部变成队列消息注入，而不是硬中断**。
> 系列：[[0-Pi Agent总览]] ｜ 下一篇 [[2-工具系统]] ｜ 源码细节：[[3-Pi Agent分析]] §2

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

## 三、steer 与 followUp：插话的两种姿势

| | steer（转向） | followUp（追问） |
|---|---|---|
| 时机 | agent **正在跑**时插入 | agent 空闲时排队 |
| 生效 | 下一轮立即注入 | 当前 run 结束后作为新输入 |
| 语义 | 纠偏："别用方案A，改用B" | 续跑："好，那再帮我加上测试" |
| UI | `/steer` 命令 / 输入框直接打字 | 输入框直接打字 |

- 两者都进 `PendingMessageQueue`，支持两种 drain 策略：`all`（一次全注入）/ `one-at-a-time`（一次一条）
- `queue_update` 事件让 UI 实时显示排队情况

> 设计精髓：**"打断"不是杀死进程，而是把话塞进队列**。模型下一轮自然看到你的话——上下文不断裂，不需要任何恢复逻辑，abort 语义和纠偏语义彻底分开。

## 四、停止控制：四类原语

| 机制 | 作用 |
|------|------|
| `stopReason` | 模型自己说停：`stop`（说完）/ `length`（到长度）/ `toolUse`（要调工具继续）/ `error` / `aborted` / `deferred` |
| `shouldStopAfterTurn` 钩子 | 每个 turn 结束问一次宿主"还要继续吗"——预算、时间、外部信号都可以在这里叫停 |
| `abort()` | 硬中断当前运行（用户按 Esc）；`waitForIdle()` 等运行与监听器全部沉淀后再收尾 |
| 截断保护 | `stopReason = length` 时 `failToolCallsFromTruncatedMessage`：让所有 tool call 直接失败，**绝不执行可能被截断的残缺参数** |

## 五、一次完整调用的数据流

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

## 六、设计启示（迁移到你自己的 Agent）

1. **循环分两层**：内层"工具循环" + 外层"续跑循环"——单层 while 写不出"答完追问接着干"
2. **steering 队列值得抄**：用户纠偏是高频需求，"注入消息"比"中断重启"优雅得多，且天然保留完整上下文
3. **shouldStopAfterTurn 是干净的扩展点**：把终止条件从循环内部挪到宿主钩子，预算控制/外部取消都不用碰内核
4. **截断保护常被忽略**：输出被截断时直接执行半截参数是事故源，"失败优于残缺执行"
5. 对照 [（2）agent开发需要处理的功能点和设计原则](../../Agent/（2）agent开发需要处理的功能点和设计原则) 的控制层四件套（Answer / 最大轮数 / 超时 / token 预算）：Pi 把它们拆成了 stopReason + 钩子 + abort 三类原语，组合出同样的保障

## 关联阅读

- 工具在循环里怎么被执行 → [[2-工具系统]]
- 循环的每个节点怎么被外界观察 → [[3-事件系统]]
- `convertToLlm` 在 LLM 边界做什么 → [[5-上下文工程]]
- 源码级细节（Agent 类 API、AgentHarness）→ [[3-Pi Agent分析]] §2
