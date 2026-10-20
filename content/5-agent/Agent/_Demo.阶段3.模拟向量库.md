> 本文是 [[（1）agent开发学习路径]] 阶段 3（前半：内存列表手写余弦检索）的配套示例 Demo，已实测跑通。
> 依赖：`mypackage` 包的 `llm()` + `embed()`（embedding-3，走 `/embeddings` 接口，见 [[link_embedding]]）。
> 源码文件：`F:\agent-study\agent_kb.py`。

## 任务设计

做一个**公司制度知识库问答 Agent**：

- 知识库 = 4 条公司制度（真实场景就是文档切块后的 chunk 列表）
- 向量库 = **纯内存列表 + 手写余弦相似度**，暴力遍历检索 topK（不借助 FAISS/Chroma，看清向量库的本质就是"存向量 + 算距离 + 排序取前K"）
- 把检索包装成 `search_knowledge` 工具，接到阶段 2 的 FC Agent 骨架上——这就完成了"知识库问答 Agent"

## 完整代码（agent_kb.py）

```python
# agent_kb.py —— 阶段3：知识库问答 Agent（内存列表 + 手写余弦检索）
import json
import math
from mypackage import llm, embed

# ① 知识库：几条公司制度（真实场景 = 文档切块后的 chunk 列表）
KNOWLEDGE = [
    "年假制度：入职满1年但不满5年的员工，每年享有5天带薪年假；入职满5年的员工，每年享有10天带薪年假；需提前3个工作日在OA系统申请。",
    "报销制度：差旅报销需在行程结束后15天内提交发票，单笔超过2000元需部门总监审批。",
    "考勤制度：工作时间为9:00-18:00，每月允许3次弹性打卡，超出按事假处理。",
    "设备申请：新员工入职当天可领取笔记本电脑，如需外接显示器需组长审批。",
]

# ② 手写余弦相似度 + 最小内存向量库（真实项目换成 FAISS / Chroma，接口长得几乎一样）
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)

class MemoryVectorStore:
    """最小向量库：add 批量入库，search 暴力遍历返回最相似的 topK"""
    def __init__(self):
        self.texts = []      # 内存列表存原文
        self.vectors = []    # 内存列表存向量（与原文下标一一对应）

    def add(self, texts):
        vecs = embed(texts)              # 一次性批量向量化（入库是一次性成本）
        self.texts.extend(texts)
        self.vectors.extend(vecs)

    def search(self, query, top_k=2):
        q_vec = embed([query])[0]        # 查询时才向量化（每次提问一次）
        scores = [cosine_similarity(q_vec, v) for v in self.vectors]
        ranked = sorted(zip(self.texts, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

store = MemoryVectorStore()
store.add(KNOWLEDGE)

# --- 先单独验证检索效果 ---
print("=== 检索测试：查询『我想休年假，能休几天』 ===")
for text, score in store.search("我想休年假，能休几天"):
    print(f"[相关度 {score:.3f}] {text}")

# ③ 把检索包装成 Agent 工具（给阶段2的 FC Agent 用）
def search_knowledge(query: str) -> str:
    results = store.search(query, top_k=2)
    return "\n".join(f"[相关度{score:.2f}] {text}" for text, score in results)

TOOLS = {"search_knowledge": search_knowledge}

tool_schemas = [{
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": "在公司知识库中搜索相关制度信息（年假、报销、考勤、设备等），输入问题关键词",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "要搜索的问题关键词，如：年假有几天"}
            },
            "required": ["query"]
        }
    }
}]

# ④ Agent 主循环：与阶段2完全相同的骨架，只是工具换成了知识库检索
SYSTEM_PROMPT = "你是公司制度问答助手。回答任何制度问题前，必须先调用 search_knowledge 检索知识库，且只基于检索到的内容回答；检索不到就说不知道，禁止编造。"

def run(question):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for i in range(5):
        msg = llm(messages, tools=tool_schemas)
        print(f"--- 第{i+1}轮 ---\n模型输出：{msg}")
        if not msg.get("tool_calls"):
            return msg["content"]
        messages.append({"role": "assistant",
                         "content": msg.get("content") or "",
                         "tool_calls": msg["tool_calls"]})
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            result = TOOLS[name](**args)
            print(f"工具调用：{name}({args}) → {result}")
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
    return "达到最大循环次数，未能得到答案"

print("\n=== Agent 问答 ===")
print("最终答案：", run("我入职3年了，想休年假，能休几天？怎么申请？"))
```

## 实际运行

```
=== 检索测试：查询『我想休年假，能休几天』 ===
[相关度 0.619] 年假制度：入职满1年但不满5年的员工，每年享有5天带薪年假；入职满5年的员工……
[相关度 0.528] 考勤制度：工作时间为9:00-18:00，每月允许3次弹性打卡……

=== Agent 问答 ===
--- 第1轮 --- 模型输出：{'tool_calls': [search_knowledge {'query': '入职3年年假几天怎么申请'}]}
工具调用：search_knowledge({'query': '入职3年年假几天怎么申请'})
  → [相关度0.71] 年假制度：……
    [相关度0.57] 考勤制度：……
--- 第2轮 --- 模型输出：{'content': '入职满3年的员工每年享有5天年假，需通过OA系统提前3个工作日申请。'}
最终答案： 入职满3年的员工每年享有5天年假，需通过OA系统提前3个工作日申请。
```

> 看点：用户问"休年假"，模型自己决定去检索知识库（Agent 骨架没变）；检索靠语义而非关键词——"入职3年想休年假"和"年假制度"字面不同但向量距离近。

## 本次踩的三个坑（实录）

1. **embedding 模型付费**：`glm-4-flash` 免费但 `/embeddings` 不免费，账户无余额时报 `429 {'code':'1113'}` 余额不足。充值买了 embedding-3 资源包后，注意资源包**绑定模型**，代码里 `model` 要写对应的 `embedding-3`。
2. **没约束时模型不调工具**：不加 system prompt，glm-4-flash 面对制度问题直接闲聊（"请问您要查什么？"）。加一条"回答制度问题前必须先调用 search_knowledge、只基于检索内容回答、检索不到就说不知道"后稳定触发工具调用——**工具要不要强制用，是 Prompt 说了算**。
3. **知识条目有歧义 → 模型答错**：年假原文写"满1年5天，满5年10天"，问"入职3年"，模型答了 10 天（3 年明明适用 5 天档）。把条目改成"满1年但不满5年……；满5年……"后答对。**RAG 的检索层没问题，是知识本身写得有歧义**——垃圾进垃圾出，知识库质量决定 RAG 上限。

## 下一步（阶段3后半）

`MemoryVectorStore` 的 `add/search` 接口和 FAISS / Chroma 几乎一样，替换实现即可入库百万级数据；多轮对话记忆的做法同理：把历史对话向量化入库，新问题先检索相关记忆再拼进 messages。

> Chroma 替换版已实测跑通，见 [[_Demo.阶段3.Chroma版]]。
