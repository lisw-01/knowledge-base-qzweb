> 本文是 [[（1）agent开发学习路径]] 阶段 3（后半：换 Chroma 向量库）的配套示例 Demo，已实测跑通。
> 与 [[（3）Agent 阶段3 示例Demo]]（手写内存版）是同一任务、同一套代码结构，**只换"存储与检索"那一层**，对比着看。
> 源码文件：`F:\agent-study\agent_chroma.py`（依赖 `pip install chromadb`，本机为 1.5.9）。

## 核心认知：换向量库换了什么？

手写版（agent_kb.py）里 `MemoryVectorStore` 干三件事：**存向量、算距离、排序取 topK**。Chroma 干的是**同一件事**，只是：

| | 手写内存版 | Chroma 版 |
| --- | --- | --- |
| 存储 | Python 列表，进程退出就没 | 落盘到 `./chroma_data`，重启还在 |
| 检索 | 暴力遍历 O(n) | HNSW 近似检索，百万级毫秒返回 |
| 距离 | 手写余弦相似度 | 指定 `hnsw:space: cosine`，返回 `distance = 1 - 相似度` |
| embed() | **自己调** | **还是自己调**（向量怎么来的，Chroma 不管） |

> 结论：**Embedding 归你管，存检归向量库管**。所以换库时 `embed()` 一行不动，只改存储层——这就是分层的好处。

## 完整代码（agent_chroma.py）

```python
# agent_chroma.py —— 阶段3后半：把手写内存向量库换成 Chroma
# 与 agent_kb.py 对比：embed()、工具、Agent 骨架全都不变，只换"存储与检索"那一层
import json
import os
from mypackage import llm, embed
import chromadb

# ① 知识库：与 agent_kb.py 完全相同
KNOWLEDGE = [
    "年假制度：入职满1年但不满5年的员工，每年享有5天带薪年假；入职满5年的员工，每年享有10天带薪年假；需提前3个工作日在OA系统申请。",
    "报销制度：差旅报销需在行程结束后15天内提交发票，单笔超过2000元需部门总监审批。",
    "考勤制度：工作时间为9:00-18:00，每月允许3次弹性打卡，超出按事假处理。",
    "设备申请：新员工入职当天可领取笔记本电脑，如需外接显示器需组长审批。",
]

# ② 换 Chroma：PersistentClient 落盘到本地目录（重启进程数据还在）
#    要纯内存模式就换 chromadb.Client()
client = chromadb.PersistentClient(path="./chroma_data")

# ③ 建集合：指定余弦距离（Chroma 默认是 L2），distance = 1 - 余弦相似度
collection = client.get_or_create_collection(
    "company_kb",
    metadata={"hnsw:space": "cosine"},
)

# ④ 入库：文档 + id + 自定义 embedding
#    仍然用我们自己的 embed()——Chroma 只管存和检索，向量怎么来的它不管
if collection.count() == 0:          # 防重复入库（持久化后再运行会保留旧数据）
    collection.add(
        documents=KNOWLEDGE,
        embeddings=embed(KNOWLEDGE),
        ids=[f"doc_{i}" for i in range(len(KNOWLEDGE))],
    )
print(f"知识库条数：{collection.count()}")

# ⑤ 检索：query_embeddings 传入查询向量，n_results 即 topK
#    返回结构：{'documents': [[...]], 'distances': [[...]], 'ids': [[...]]}
def search_knowledge(query: str) -> str:
    results = collection.query(query_embeddings=embed([query]), n_results=2)
    docs = results["documents"][0]
    dists = results["distances"][0]
    return "\n".join(
        f"[相关度{1 - d:.2f}] {doc}" for doc, d in zip(docs, dists)
    )

# --- 先单独验证检索效果 ---
print("=== 检索测试：查询『我想休年假，能休几天』 ===")
print(search_knowledge("我想休年假，能休几天"))

# ⑥ 以下与 agent_kb.py 完全一致：工具注册 + Agent 主循环
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
知识库条数：4
=== 检索测试：查询『我想休年假，能休几天』 ===
[相关度0.62] 年假制度：入职满1年但不满5年的员工，每年享有5天带薪年假……
[相关度0.53] 考勤制度：工作时间为9:00-18:00，每月允许3次弹性打卡……

=== Agent 问答 ===
--- 第1轮 --- 模型输出：{'tool_calls': [search_knowledge {'query': '入职3年年假几天怎么申请'}]}
工具调用：search_knowledge({'query': '入职3年年假几天怎么申请'})
  → [相关度0.71] 年假制度：……
    [相关度0.57] 考勤制度：……
--- 第2轮 --- 模型输出：{'content': '入职满3年的员工每年享有5天年假，需通过OA系统提前3个工作日申请。'}
最终答案： 入职满3年的员工每年享有5天年假，需通过OA系统提前3个工作日申请。
```

> 与手写版对比：检索分数几乎一致（0.62/0.53 vs 0.619/0.528，tiny 差异来自 `1-distance` 的浮点换算），Agent 行为完全一致——证明**换库没换脑子**，改的只是存储层。

**持久化验证**（新开进程，不 add 直接读）：

```
新进程读取条数： 4
年假制度：入职满1年但不满5年的员工 ...   # 上次入库的数据还在
```

## 注意事项

1. **距离度量**：Chroma 默认 `L2`（欧氏距离），和余弦不是一回事；要跟教程/手写版对齐必须 `metadata={"hnsw:space": "cosine"}`，且返回的是 distance（`1 - 相似度`），**越小越相似**——和手写版的相似度方向相反，别搞混。
2. **自定义 embedding**：`add` 时传 `embeddings=`、`query` 时传 `query_embeddings=`，Chroma 就不会启用它自带的默认嵌入模型（默认模型是英文向的，且首次要下载 ONNX 包）。**存和查必须用同一个 embedding 模型**。
3. **重复入库**：`PersistentClient` 的数据跨进程保留，重复 `add` 相同 `id` 会报错/重复，用 `count()==0` 或 `get_or_create_collection` + upsert 管理。
4. 生产环境还可换 Chroma 的 Client/Server 模式（独立进程起服务），接口不变。
