> 核心一句话：**messages 是 LLM API 的唯一输入——一个按时间排好的"对话剧本"数组，每条 `{role, content}`；LLM 本身无状态，所谓"多轮对话的记忆"，全靠你把历史一条条拼回去再发。**

## 一、messages 是什么

调 `/chat/completions` 时，真正的"问题"不是一串文本，而是 messages 数组：

```json
{
  "model": "glm-4-flash",
  "temperature": 0,
  "messages": [
    {"role": "system", "content": "你是一个计算器助手，回答简洁"},
    {"role": "user",   "content": "3*7等于几"},
    {"role": "assistant", "content": "3*7等于21"},
    {"role": "user",   "content": "再加10呢"}
  ]
}
```

模型看到的不是"最后一句话"，而是**整个剧本**。它根据全部内容续写"下一条 assistant 台词"。所以：**你组织 messages 的方式 = 你给模型的世界观**。

## 二、四种 role

| role        | 谁在说话   | 用途                          | 位置                            |
| ----------- | ------ | --------------------------- | ----------------------------- |
| `system`    | 你（开发者） | 人设、规则、格式约束，指令权重最高           | 数组最前，只出现一次                    |
| `user`      | 最终用户   | 用户的输入 / 要模型处理的任务            | 按时间穿插                         |
| `assistant` | 模型     | 模型的历史回复（**你手动拼回去的**）        | 按时间穿插                         |
| `tool`      | 你的程序   | 工具执行结果，配合 `tool_call_id` 回传 | 紧跟在带 tool_calls 的 assistant 后 |

> 记忆口诀：system 定规则，user 提要求，assistant 是历史，tool 报结果。

## 三、多轮对话的真相：LLM 无状态

**API 不记得你上次说过什么**。每次请求都是独立的一次调用，"它记得上文"的唯一原因是你把历史全量重发了：

```python
# 第一轮
messages = [{"role": "user", "content": "我叫小明"}]
# 模型答：你好小明

# 第二轮想让它记得你叫小明？必须自己拼：
messages = [
    {"role": "user",      "content": "我叫小明"},
    {"role": "assistant", "content": "你好小明"},   # ← 上一轮的回复，手动塞回来
    {"role": "user",      "content": "我叫什么？"},
]
```

由此推出两个必然结论：

1. **token 成本逐轮递增**：第 N 轮要把前 N-1 轮全部重发，这就是"上下文膨胀"（见 [[（1）agent开发学习路径]] 避坑清单第 6 条）
2. **超出上下文窗口就要裁剪**：滑动窗口截断旧消息，或让模型把旧历史摘要成一条 system/user 消息

> ChatGPT 网页版"记得住你"，本质是服务端替你维护了这个 messages 数组并做了裁剪/摘要，和模型本身无关。

## 四、Function Calling 时的 message 结构

开启 tools 后，剧本里多两种"新台词"（对照 [[_Demo.阶段1&2]] 阶段 2 的实际请求）：

```json
[
  {"role": "user", "content": "帮我算一下 128 乘以 456"},

  {"role": "assistant",                 ← 模型不直接回答，而是"点菜"
   "content": "",                        ← 注意：经常没有 content，要补空串
   "tool_calls": [{
       "id": "call_abc123",
       "type": "function",
       "function": {"name": "calculate", "arguments": "{\"expression\": \"128*456\"}"}
   }]},

  {"role": "tool",                      ← 你的程序执行完，把结果"上菜"
   "tool_call_id": "call_abc123",        ← 必须对应上面的 id，成对出现
   "content": "58368"}
]
```

把这份剧本再发给模型，它就能基于工具结果生成最终回答。

**三个必踩的坑（实测）：**

1. **assistant 的 tool_calls 消息可能没有 content 字段**——原样拼回历史，下一轮请求 GLM 会报错，要补 `"content": ""`
2. **tool 消息必须与 tool_calls 成对**：assistant 说要调 3 个工具，就必须跟 3 条 tool 消息（各自带对应 `tool_call_id`），缺一条 API 直接拒绝
3. **`arguments` 是 JSON 字符串不是对象**：`tc["function"]["arguments"]` 要再过一次 `json.loads` 才能拿到参数字典

> 有趣的对比（见 [[（1）LLM学习路径]] 方案 A/B）：手写 ReAct 版没有 tool 角色，我们**借 user 的身份**传 `Observation: 58368`；FC 版用标准的 tool 角色 + tool_call_id。功能等价，后者是模型特训过的官方频道，更稳。

## 五、实操要点

1. **顺序即时间线**：system 永远第一，其余按发生顺序，最后一条一般是 user（或 tool 结果）
2. **能写进 system 就别写进 user**：规则类约束（格式、禁令、人设）放 system 更稳，不会被对话冲淡
3. **history 由你裁剪**：messages 里放什么、放几条，是你的代码决定的——这也是 Agent 的"短期记忆"管理层（长期记忆见 [[link_embedding]]）
4. **content 永远是字符串**：工具返回 dict/list 要先 `json.dumps`；模型输出的结构化内容也是字符串，要自己 `json.loads`
5. **temperature=0 时，messages 完全决定输出**：调 Prompt 本质上就是在调 messages——Agent 的"规划能力"，一大半体现为程序怎么动态拼这份剧本（塞工具结果、塞检索到的知识、塞摘要后的历史）


