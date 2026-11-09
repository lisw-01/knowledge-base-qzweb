# （3）ReAct 工具调用失败处理

> 核心一句话：**工具失败不能抛异常打断循环——把错误信息包装成 Observation 放回上下文，让模型下一轮自救；框架层只做三件事：失败分类、临时错误有限重试、熔断兜底**。
> 系列：[[（1）agent开发学习路径]] ｜ [[（2）agent开发需要处理的功能点和设计原则]]（本篇 = 其 ③工具层"错误回喂" + ⑤控制层"终止条件" + ⑥护栏层的展开）｜ Pi 的机制化参考实现：[[5-Agent循环]]、[[3-工具系统]]

## 一、核心原则：错误是给模型看的观测，不是程序异常

ReAct 核心循环：Thought → Action（调工具）→ Observation → Thought。其中"执行工具 → 拼回 Observation"这一步**不区分成功失败**——try/catch 兜住一切异常，错误文本塞进 Observation 的位置，循环继续。

```js
while (step < maxSteps) {
  const llmOut = await llm.call(messages);          // Thought + Action
  messages.push({ role: "assistant", content: llmOut });
  if (llmOut.isFinalAnswer) break;

  let observation;
  try {
    observation = await executeTool(llmOut.toolName, llmOut.toolArgs);
  } catch (e) {
    observation = `工具 ${llmOut.toolName} 执行失败：${e}`;   // ← 错误也是观测
  }
  messages.push({ role: "tool", content: observation });      // ← 成败统一拼回上下文
}
```

模型看到错误 Observation 后的典型自救：修参数重试、换工具、换思路、输出 Answer 承认失败——**纠错是模型的活，循环只负责把错误送到模型眼前**。

三个最常见的坑：

1. **异常穿透**：catch 没兜住，整个 Agent 进程崩掉（最低级也最常见）
2. **错误信息太糊**：Observation 只写"调用失败"，模型无从恢复，只会用相同参数反复撞墙
3. **重试无上限**：无论框架层还是模型层重试，没有硬上限就是死循环发生器

## 二、先分类，再处理（四类失败，策略完全不同）

| 失败类型 | 例子 | 策略 |
|---|---|---|
| ① 临时可重试（transient） | 网络抖动、超时、429 限流、HTTP 5xx | **框架层有限重试**（指数退避 + 抖动，2~3 次）；重试成功 → 正常结果作 Observation；耗尽 → 错误交给 LLM |
| ② 确定性错误（permanent） | 参数缺失/格式错、工具不存在、权限不足、文件不存在、业务校验失败 | **不重试**，结构化错误直接回喂，让模型下一轮修参数 / 换工具 / 换方案 |
| ③ 业务空结果（不是报错） | 查询返回空、找不到数据 | 返回空结果本身，让模型思考换查询条件 |
| ④ 灾难性故障 | 依赖服务完全宕机、鉴权永久失效 | **熔断**：终止循环，返回给用户或人工介入 |

分类判据参考：HTTP 5xx / `ETIMEDOUT` / `ECONNRESET` / 429 → ①；HTTP 4xx / 参数校验失败 / `EACCES` / `ENOENT` → ②；**unknown 默认按②处理**（不重试，交给模型），宁可少重试不可多重试。

> ⚠️ **写操作重试必须带幂等 key**（唯一请求 id / 去重键）。超时的语义是"结果未知"而不是"失败"——服务可能已执行成功，盲目重试会重复扣款 / 重复发消息 / 重复写入。正确姿势：**优先回查状态确认结果，再决定是否重试**。

## 三、标准处理流程

```
1. LLM 输出 Action（工具名 + 参数）
2. 【框架层】参数预校验（JSON 合法性、必填字段）——非法直接生成错误 Observation，不调用工具
3. try/catch 包裹执行
    ├─ 捕获异常 → 按第二节分类
    ├─ 临时错误 → 有限重试（指数退避）
    └─ 重试耗尽 / 确定性错误 → 包装成结构化错误 Observation
4. Observation（成功结果 / 错误信息）追加进对话上下文
5. 回到 ReAct 循环：LLM 看到 Observation，进行新一轮 Thought
6. 全局硬保护：max_steps + 连续失败熔断
```

## 四、错误 Observation 怎么写（决定模型能不能自救）

❌ 差：`调用工具失败`（模型看不懂，容易无限重复调用相同参数）

✅ 好（结构化：失败原因 + 环境上下文 + 行动提示）：

```
Observation：工具 mkdirSync 执行失败。错误原因：目录无写入权限，路径=/app/sessions。
提示：请检查目录挂载与权限，或更换可写入的路径。
```

四要素：**错误类型**（让模型判断该重试还是该换路）、**原始错误信息**（errno、HTTP 状态码）、**相关上下文**（路径、变量实际值）、**下一步提示**（可选）。

## 五、代码示例（Node.js 简易 ReAct，含分类 + 有界重试）

```js
// 工具执行统一出口：永不抛异常，成败都走结构化返回值
async function executeTool(toolName, args) {
  try {
    if (!TOOLS[toolName]) {
      return { ok: false, errorType: "permanent",
        content: `Observation：不存在工具 ${toolName}，可用工具：${Object.keys(TOOLS).join(", ")}` };
    }
    const result = await TOOLS[toolName](args);
    return { ok: true, content: result };
  } catch (e) {
    if (["ETIMEDOUT", "ECONNRESET"].includes(e.code)) {
      return { ok: false, errorType: "transient", content: `Observation：网络错误（${e.code}）` };
    }
    return { ok: false, errorType: "permanent",
      content: `Observation：${e.message}${args.path ? `，路径=${args.path}` : ""}` };
  }
}

async function reactLoop(query, maxSteps = 8) {
  const messages = [
    { role: "system", content: REACT_PROMPT },
    { role: "user", content: query },
  ];
  let consecutiveFailures = 0;

  for (let step = 0; step < maxSteps; step++) {
    const llmOut = await llm.call(messages);              // 1. Thought + Action
    messages.push({ role: "assistant", content: llmOut });
    if (llmOut.isFinalAnswer) return llmOut.answer;

    let result = await executeTool(llmOut.toolName, llmOut.toolArgs);

    // 2. 临时错误：框架层退避重试，最多 2 次
    for (let retry = 1; retry <= 2 && result.errorType === "transient"; retry++) {
      await sleep(2 ** retry * 1000);
      result = await executeTool(llmOut.toolName, llmOut.toolArgs);
    }

    // 3. 连续失败熔断
    consecutiveFailures = result.ok ? 0 : consecutiveFailures + 1;
    if (consecutiveFailures >= 3) {
      return `任务终止：连续 ${consecutiveFailures} 次工具失败，最后错误：${result.content}`;
    }

    // 4. 成败统一回喂，进入下一轮 Thought
    messages.push({ role: "tool", content: result.content });
  }
  return `任务终止：达到最大轮数 ${maxSteps}`;
}
```

要点：`executeTool` 永不抛异常；重试只针对 `transient`；两层独立保险（max_steps + 连续失败计数）互为冗余。

## 六、生产护栏清单（防死循环、防 token 爆炸）

1. **最大迭代轮数 max_steps**：循环硬上限（5~10），超过直接终止，返回已收集的信息
2. **连续失败熔断**：连续 N 次工具失败即停，防止模型疯狂重试
3. **工具侧超时**：每次调用单独设超时，不能无限等待下游
4. **日志与 trace**：每步 Thought / Action / Observation / error_code / 重试次数落盘，一个 trace_id 串起全程
5. **幂等性**：有副作用的工具（写文件、DB、发消息）请求携带唯一 id，重试不产生重复副作用

## 七、Pi 怎么做（机制化参考实现）

| 本篇的做法 | Pi 的对应物 |
|---|---|
| 错误包装成 Observation 回喂 | `AgentToolResult.isError`：工具失败是带标记的结果而非异常，照常进上下文（[[3-工具系统]]） |
| 参数预校验 | 四阶段流水线 Prepare 阶段（Schema 校验 + `beforeToolCall` 钩子） |
| 残缺参数不执行 | `failToolCallsFromTruncatedMessage`：输出截断时所有 tool call 直接标记失败，绝不执行半截参数（[[5-Agent循环]] §四） |
| 临时错误有限重试 | 只在 **LLM 调用层**做（settings `retry.maxRetries` + 退避 + `auto_retry` 事件）；**工具层默认不重试**，交给模型或工具作者自己实现 |
| max_steps / 熔断 | `shouldStopAfterTurn` 钩子 + `stopReason`：预算、时间、外部信号都在钩子里叫停（[[5-Agent循环]] §四） |

> Pi 把本篇的"策略"拆成了"机制"：错误即信息做成数据流（`isError` + never-throw），终止兜底做成钩子（`shouldStopAfterTurn`），重试收敛在 LLM 层——工具层失败一律回喂，下一步怎么走由模型决定。

## 关联阅读

- 错误回喂在七层地图中的位置 → [[（2）agent开发需要处理的功能点和设计原则]] ③⑤⑥
- Pi 的工具执行流水线 → [[3-工具系统]]
- Pi 的循环与停止控制 → [[5-Agent循环]]
