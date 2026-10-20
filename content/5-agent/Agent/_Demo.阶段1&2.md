> 本文是 [[（1）agent开发学习路径]] 阶段 1、阶段 2 的配套示例 Demo，两个都已实测跑通。
> 依赖：[mypackage包下的__init__.py](obsidian://open?vault=knowledge-base&file=5-agent%2FAgent%2Flink_%E5%8C%85%E4%B8%8B%E7%9A%84__init__.py)，返回完整 message 字典。
> 源码文件：`F:\agent-study\agent_react.py`、`F:\agent-study\agent_fc.py`。

## 任务设计

两个阶段做**同一个任务**："北京今天多少度？如果气温超过25度，帮我算一下 25*3.5 是多少"。

故意选这个任务，因为它需要**先查天气、再根据结果决定要不要算**——模型必须自己规划工具调用顺序，才能看到"自主决策"的最小闭环。工具用两个：`calculate`（计算器）+ `get_weather`（假数据天气）。

## 阶段 1 Demo：手写 ReAct 原生 Agent（agent_react.py）

两个工具 + 注册表，比 LLM 篇的单工具版多了"模型幻觉出不存在工具"的兜底；`stop=["Observation:"]` 防模型编造 Observation（坑见 [[（1）LLM学习路径]] 踩坑实录）。

```python
# agent_react.py —— 阶段1：手写 ReAct 原生 Agent（不借助任何框架）
import re
from mypackage import llm

# ① 工具集：普通 Python 函数 + 注册表（模型只能调这里登记过的）
def calculate(expression: str) -> str:
    return str(eval(expression))   # 演示用，真实项目别直接 eval

def get_weather(city: str) -> str:
    # 没接真实天气 API，先返回假数据跑通流程
    fake = {"北京": "晴，28度", "上海": "小雨，22度", "广州": "多云，30度"}
    return fake.get(city, f"{city}：暂无数据")

TOOLS = {"calculate": calculate, "get_weather": get_weather}

# ② Prompt：约定 ReAct 格式 + 列出工具清单 + 防幻觉规则
SYSTEM_PROMPT = """你是一个可以调用工具的助手。可用工具：
calculate: 计算数学表达式，参数如 128*456
get_weather: 查询城市天气，参数为城市名

你必须一轮一轮地回复，每轮严格按下面两种格式之一输出，禁止输出其他任何内容：

需要调用工具时，只输出这两行，然后立即停止，等待系统返回 Observation：
Thought: 一句话说明要做什么
Action: 工具名[参数]

收到 Observation 且已经足以回答时，只输出这一行：
Answer: 最终答案

重要规则：
- Observation 只能由系统执行工具后提供，绝对禁止自己编造 Observation
- 在收到真实的 Observation 之前，禁止输出 Answer
"""

# ③ ReAct 主循环：调 LLM → 解析 Action → 执行 → 拼回 Observation → 直到 Answer
def run(question):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for i in range(5):                       # 最大循环次数兜底，防死循环烧 token
        output = llm(messages, stop=["Observation:"])["content"]
        print(f"--- 第{i+1}轮 ---\n模型输出：{output}")
        m = re.search(r"Action:\s*(\w+)\[(.+?)\]", output)   # 正则抠工具名和参数
        if not m:
            a = re.search(r"Answer:\s*(.+)", output)
            return a.group(1) if a else "解析失败：" + output  # 没有Action=答完了
        tool_name, arg = m.group(1), m.group(2)
        if tool_name not in TOOLS:           # 模型幻觉出不存在的工具时兜底
            result = f"工具 {tool_name} 不存在，可用：{list(TOOLS)}"
        else:
            result = TOOLS[tool_name](arg)
        print("工具返回：", result)
        messages.append({"role": "assistant",
                         "content": output.split("Observation:")[0].split("Answer:")[0]})
        messages.append({"role": "user", "content": f"Observation: {result}"})
    return "达到最大循环次数，未能得到答案"

print("最终答案：", run("北京今天多少度？如果气温超过25度，帮我算一下 25*3.5 是多少"))
```

实际运行（多轮决策：查天气 → 判断 → 计算 → 回答）：

```
--- 第1轮 --- 模型输出：Thought: 查询北京今天的气温
Action: get_weather[北京]
工具返回： 晴，28度
--- 第2轮 --- 模型输出：Thought: 判断北京气温是否超过25度
Action: calculate[28>25]
工具返回： True
--- 第3轮 --- 模型输出：Thought: 计算气温超过25度时 25 乘 3.5 的结果
Action: calculate[25*3.5]
工具返回： 87.5
--- 第4轮 --- 模型输出：Answer: 87.5
最终答案： 87.5
```

> 看点：任务需要**先查天气再决定算不算**，模型自己规划了调用顺序——这就是"自主决策"最小闭环。注册表代替了 `globals()`，把模型可调用的范围收敛成白名单。

## 阶段 2 Demo：原生 Function Calling 版 Agent（agent_fc.py）

与阶段 1 同一个任务、同一套工具函数，只换"声明工具"和"解析输出"两处。

```python
# agent_fc.py —— 阶段2：原生 Function Calling 版 Agent
import json
from mypackage import llm

def calculate(expression: str) -> str:
    return str(eval(expression))   # 演示用，真实项目别直接 eval

def get_weather(city: str) -> str:
    fake = {"北京": "晴，28度", "上海": "小雨，22度", "广州": "多云，30度"}
    return fake.get(city, f"{city}：暂无数据")

TOOLS = {"calculate": calculate, "get_weather": get_weather}   # 注册表同阶段1

# ① 工具改用 JSON Schema 正式声明（description 写清楚，模型才选得准）
tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式的值，如加减乘除",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如：128*456"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，如：北京"}
                },
                "required": ["city"]
            }
        }
    }
]

# ② 主循环：结构与阶段1相同，但解析从"正则抠文本"变成"读 tool_calls JSON"
def run(question):
    messages = [{"role": "user", "content": question}]
    for i in range(5):                       # 同样要有最大次数兜底
        msg = llm(messages, tools=tool_schemas)
        print(f"--- 第{i+1}轮 ---\n模型输出：{msg}")
        if not msg.get("tool_calls"):        # 没有 tool_calls = 直接回答了
            return msg["content"]
        messages.append({"role": "assistant",
                         "content": msg.get("content") or "",
                         "tool_calls": msg["tool_calls"]})
        for tc in msg["tool_calls"]:         # 可能一次请求多个工具
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])   # 参数直接是JSON，不用正则
            if name not in TOOLS:
                result = f"工具 {name} 不存在，可用：{list(TOOLS)}"
            else:
                result = TOOLS[name](**args)
            print(f"工具调用：{name}({args}) → {result}")
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
    return "达到最大循环次数，未能得到答案"

print("最终答案：", run("北京今天多少度？如果气温超过25度，帮我算一下 25*3.5 是多少"))
```

实际运行：

```
--- 第1轮 --- 模型输出：{'tool_calls': [get_weather {'city': '北京'}]}
工具调用：get_weather({'city': '北京'}) → 晴，28度
--- 第2轮 --- 模型输出：{'tool_calls': [calculate {'expression': '25*3.5'}]}
工具调用：calculate({'expression': '25*3.5'}) → 87.5
--- 第3轮 --- 模型输出：{'content': '北京今天气温为28度，超过25度，计算25*3.5=87.5。'}
最终答案： 北京今天气温为28度，超过25度，计算25*3.5=87.5。
```

## 两版对比体感

1. 阶段 2 少了 SYSTEM_PROMPT、正则、stop、截断那一堆兜底——格式由模型特训保证
2. 参数是 JSON 直出，`json.loads` 即用
3. "28>25"这种小判断，阶段 2 模型自己做了没调工具（阶段 1 它老实调了 calculate），两版的决策风格略有差异
4. 代价：要为每个工具多写一份 JSON Schema

> 相同点（Agent 的骨架两版完全一致）：**循环 + 注册表 + 最大次数兜底**。框架（阶段 5）替换的只是这层骨架的工程化，工具函数和注册表永远是你自己的代码。
