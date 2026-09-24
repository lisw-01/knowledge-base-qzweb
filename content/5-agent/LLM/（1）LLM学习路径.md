LLM = **Large Language Model，大语言模型**

LLM 是能理解、生成人类语言，可完成推理、归纳、文本转换，还能配合外部工具做规划决策的大语言模型。
## 一、LLM 核心基础概念

1. **Token**
    
    LLM 的最小处理单元，可以是单词、字、偏旁符号。
    
    - 中文大概：1 个汉字≈2 token
    - API 计费、上下文窗口上限，都是按 token 算。
        
        > 例：GLM-4-Flash 上下文窗口支持 128k token，代表一次性最多可以输入 + 输出合计 128k token 的文本。
        
    
2. **上下文窗口（Context Window）**
    
    LLM 能一次性 “看到” 的全部内容（历史对话、提示词、文档、工具返回结果）。
    
    - 超过上限，会丢失最前面的信息；
    - Agent 里很容易遇到：多次工具调用后上下文膨胀，token 超限。
    - 解决方案：摘要压缩、向量 RAG 长期记忆。
    
3. **Prompt / 提示词**
    
    你发给大模型的指令文本，用来告诉模型角色、任务、输出格式、约束规则。
    
    Agent 里的系统提示词（System Prompt）就是用来定义 Agent 身份、可用工具、输出规范。
    
4. **Temperature（温度）**
    
    控制模型输出随机性：
    
    - `0`：最确定、稳定，适合**Agent 工具调用、生成 SQL、结构化输出**（优先选 0）
    - `0.7`：有创造力，适合写文案、聊天
    - `>1`：非常发散，容易胡编幻觉，Agent 项目不推荐
    
5. **幻觉 (Hallucination)**
    
    LLM 会编造不存在事实、参数、表名。
    
    ✅ Agent 开发最头疼问题：模型虚构工具、虚构 SQL 表、编造不存在数据。
    
    缓解方法：
    
    - 严格 prompt 约束
    - 工具返回真实数据再让模型总结
    - 增加反思校验模块
    - 给模型限定知识库（RAG）
    
1. **[[embedding]]（嵌入向量）**
    
    把文本转为一串数字向量，用于体现相似度。1：相似   -1： 相反   0：无关
    



## 二、LLM 两种使用方式（Agent 开发都会用到）

### 1. 普通对话调用（Chat Completions）

输入对话消息数组 `[ {"role":"system"}, {"role":"user"} ]`，模型直接输出文字。

python

```
# 极简示例（智谱GLM）
import requests
import os
from dotenv import load_dotenv
load_dotenv()

resp = requests.post(
    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    headers={"Authorization": f"Bearer {os.getenv('ZHIPU_API_KEY')}"},
    json={
        "model": "glm-4-flash",
        "temperature": 0,
        "messages": [
            {"role":"system", "content":"你是一个计算器助手，回答简洁"},
            {"role":"user", "content":"3*7等于几"}
        ]
    }
)
print(resp.json()["choices"][0]["message"]["content"])
```

### 2. 工具调用（Function Calling）

LLM**输出结构化参数**，告诉程序调用哪个工具、传什么参数，就是 Agent 的核心能力。

> 两种实现：
> 
> - 方案 A：手写 Prompt 强制输出`Action:xxx[xxx]`（前面原生 ReAct Demo）
> - 方案 B：模型原生 Function Calling（GLM、GPT 都支持，更稳定，工业常用）

两种实现完成**同一个任务**：用户问"帮我算一下 128 乘以 456"，LLM 决定调用计算工具，程序执行后把结果喂回去，LLM 给出最终回答。对比着看，区别一目了然。

### 方案 A Demo：手写 Prompt（ReAct 文本格式）

原理：在 Prompt 里**自己约定输出格式**（`Action:工具名[参数]`），模型输出的是普通文本，我们自己解析、自己执行、把结果拼回对话循环。

```python
# fc_demo_a.py
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ZHIPU_API_KEY")
BASE_URL = os.getenv("ZHIPU_BASE_URL")

# ① 我拥有的工具（普通 Python 函数）
def calculate(expression: str) -> str:
    # 演示直接 eval；真实项目不要 eval 任意输入，应白名单校验或用安全计算库
    return str(eval(expression))

# ② 提示词里写死格式约定：LLM 只能按这个格式"说话"
SYSTEM_PROMPT = """你可以使用工具回答问题。可用工具：
calculate: 计算数学表达式

请严格按以下格式回复，不要输出其他内容：
Thought: 我需要思考怎么做
Action: 工具名[参数]
（系统会执行工具并把结果以 Observation 返回给你）
当你已经知道答案，输出：
Answer: 最终答案
"""

def llm(messages):
    resp = requests.post(f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "glm-4-flash", "temperature": 0, "messages": messages})
    return resp.json()["choices"][0]["message"]["content"]

# ③ ReAct 循环：解析文本 → 执行 → 拼回去 → 直到出现 Answer
def run(question):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    for _ in range(5):   # 最多循环5次，防止死循环
        output = llm(messages)
        print("模型输出：", output)
        # 用正则从文本里"抠"出工具名和参数 —— 方案A的核心麻烦点
        m = re.search(r"Action:\s*(\w+)\[(.+?)\]", output)
        if not m:
            return re.search(r"Answer:\s*(.+)", output).group(1)  # 没有Action=答完了
        tool_name, arg = m.group(1), m.group(2)
        result = globals()[tool_name](arg)   # 执行工具
        print("工具返回：", result)
        # 把执行结果以 Observation 拼回对话
        messages.append({"role": "assistant", "content": output})
        messages.append({"role": "user", "content": f"Observation: {result}"})

print(run("帮我算一下 128 乘以 456"))
```

运行效果：

```
模型输出： Thought: 这是一道乘法计算，我需要调用计算工具
Action: calculate[128*456]
工具返回： 58368
模型输出： Thought: 拿到计算结果，可以回答了
Answer: 128 乘以 456 等于 58368。
最终输出： 128 乘以 456 等于 58368。
```

> 特点：格式是**我们自己发明**的，模型偶尔不守规矩（多说话、格式写错），正则解析就可能失败，需要各种兜底。适合理解原理。

### 方案 B Demo：原生 Function Calling（推荐）

原理：工具用 **JSON Schema 正式声明**传给模型（`tools` 参数），模型开启特训过的"工具模式"，**返回值直接是结构化 JSON**（`tool_calls` 字段），不用自己发明格式、不用正则解析。

```python
# fc_demo_b.py
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ZHIPU_API_KEY")
BASE_URL = os.getenv("ZHIPU_BASE_URL")

def calculate(expression: str) -> str:
    return str(eval(expression))   # 同样的工具，真实项目别直接 eval

# ① 用 JSON Schema 正式"注册"工具：名字、用途、参数说明
tools = [{
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
}]

def llm(messages):
    resp = requests.post(f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "glm-4-flash", "temperature": 0,
              "messages": messages, "tools": tools})   # ② tools 随请求传入
    return resp.json()["choices"][0]["message"]

def run(question):
    messages = [{"role": "user", "content": question}]
    for _ in range(5):
        msg = llm(messages)
        if not msg.get("tool_calls"):          # 没有工具调用 = 直接回答了
            return msg["content"]
        messages.append(msg)                   # 把模型的工具请求记入历史
        for tc in msg["tool_calls"]:           # 可能一次请求多个工具
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])   # ③ 参数直接是JSON，不用正则！
            print(f"模型要求调用：{name}({args})")
            result = calculate(**args)       # 执行真实函数
            # ④ 把结果以 role=tool 塞回对话，模型继续
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result
            })

print(run("帮我算一下 128 乘以 456"))
```

运行效果：

```
模型要求调用：calculate({'expression': '128*456'})
最终输出： 128 乘以 456 等于 58368。
```

> 注意模型自动把"乘以"翻译成了表达式 `128*456`——参数填什么，靠的就是 JSON Schema 里那段 description。

### 两方案对比总结

| | 方案 A：手写 Prompt | 方案 B：原生 Function Calling |
| --- | --- | --- |
| 格式约定 | 自己发明（Action:xxx[]） | 官方标准（JSON Schema） |
| 模型输出 | 普通文本，要正则抠参数 | 结构化 `tool_calls` JSON，直接解析 |
| 稳定性 | 模型可能不守格式，需兜底 | 模型专门训练过，非常稳 |
| 兼容性 | 任何模型都能用（哪怕不支持FC） | 需要模型支持（GLM-4、GPT 都支持） |
| 使用建议 | 理解原理用 | **实际项目一律用这个** |

> 两种方案里，模型都**只负责"说要调什么"**，真正执行函数的永远是我们的 Python 代码——这就是 Agent 安全的关键：模型没有权限，只有建议权。



