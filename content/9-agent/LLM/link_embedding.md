> 核心一句话：**Embedding 就是把文本变成一串数字向量（如 1024 个浮点数），语义相近的文本在向量空间里距离也近；它是语义搜索、RAG 知识库、Agent 长期记忆的底层基础。**

## 一、Embedding 是什么

- 输入：一段文本（词、句子、整篇文档）
- 输出：一个固定长度的浮点数数组（向量），例如 1024 维

```
"今天天气真好"  →  [0.021, -0.113, 0.876, ..., 0.043]   # 1024 个数
"今日气候不错"  →  [0.019, -0.108, 0.881, ..., 0.045]   # 跟上面距离很近
"我想吃火锅"    →  [-0.33, 0.52, -0.07, ..., -0.21]     # 跟上面距离很远
```

**核心价值**：把"语义相似度"这个模糊问题，变成"向量距离"这个数学问题。

- 传统关键词搜索：搜"如何退货"，匹配不到"退款流程"（字面不同）
- 向量语义搜索：两者语义相近 → 向量距离近 → 能搜到

## 二、和 LLM 的关系（为什么 Agent 必须懂它）

| 能力 | 作用 |
| --- | --- |
| RAG 知识库 | 文档切块 → 向量化 → 存向量库；用户提问也向量化，找出最相关的几块喂给 LLM 回答 |
| Agent 长期记忆 | 对话历史向量化存储，新问题来了先检索相关记忆，解决上下文窗口超限 |
| 语义搜索 / 推荐去重 | 相似问题聚类、重复问题识别 |

> 记住分工：**LLM 负责理解和生成，Embedding 负责记忆和检索**。上下文窗口不够、知识库太大，都靠 Embedding 兜底。

**LLM 不自带 Embedding，是两个独立模型**。厂商会同时提供两种模型，但接口分开、计费分开：

- LLM：`glm-4-flash`，走 `/chat/completions`
- Embedding：`embedding-2` / `embedding-3`，走 `/embeddings`

调用 `/chat/completions` 拿不到向量，调用 `/embeddings` 也不会回答问题 —— 用哪个得自己显式调用。

> 补充：LLM 内部其实有 embedding 层（把 token 转成内部向量），但那是模型私有的中间状态，不对外开放，不能当 embedding 服务用。所以做 RAG / 记忆检索时，必须额外单独调 embedding 模型。

## 三、调用 Embedding API（智谱 GLM 示例）

模型选择：`embedding-2`（便宜够用）/ `embedding-3`（更新，默认 2048 维可指定 dimensions）

```python
# embedding_demo.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ZHIPU_API_KEY")
base_url = os.getenv("ZHIPU_BASE_URL")

resp = requests.post(
    f"{base_url}/embeddings",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "embedding-2",
        "input": ["如何退货", "退款流程是什么"]
    }
)

data = resp.json()["data"]
# 每个文本对应一个向量
vec1 = data[0]["embedding"]   # 1024 维列表
vec2 = data[1]["embedding"]
print("向量维度：", len(vec1))
```

> 注意接口是 `/embeddings`，不是 `/chat/completions`；`input` 传字符串数组，可批量。

## 四、相似度计算：余弦相似度（最常用）

```python
import math

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)

print(cosine_similarity(vec1, vec2))   # 输出 0~1，越接近 1 越相似
```

- 范围 `-1 ~ 1`，实际文本场景一般 `0 ~ 1`
- 经验阈值：**> 0.7 高度相关，0.5 ~ 0.7 弱相关，< 0.5 基本无关**（不同模型阈值不同，需实测）

## 五、最小 RAG 流程（Embedding 的实战用法）

```python
# 1. 知识入库：文档切块 → 向量化 → 存起来（内存/数据库/向量库）
docs = [
    "退货需在签收后7天内申请，商品需保持完好",
    "会员积分可在下单时抵扣现金，100积分抵1元",
    "客服工作时间为每天9:00-21:00",
]
doc_vecs = get_embeddings(docs)   # 调用上面的 embedding 接口

# 2. 检索：用户问题向量化 → 找出最相似的 topK 块
question = "买完东西想退"
q_vec = get_embeddings([question])[0]
scores = [cosine_similarity(q_vec, dv) for dv in doc_vecs]
top_idx = scores.index(max(scores))

# 3. 生成：把最相关的知识块塞进 prompt，让 LLM 回答
prompt = f"请根据以下资料回答问题：\n资料：{docs[top_idx]}\n问题：{question}"
answer = chat(prompt)   # 调用 chat/completions
```

> 上面用列表暴力遍历只是演示；真实项目用**向量数据库**（FAISS、Chroma、Milvus、pgvector）做近似检索，支持百万级数据毫秒返回。

## 六、实操注意事项

1. **换模型 = 全部重新向量化**：不同 Embedding 模型的向量空间不兼容，embedding-2 的向量不能和 embedding-3 的算相似度。
2. **文本先切块再向量化**：单条建议 200~500 字，太长稀释语义，检索不准。
3. **Embedding 模型不生成内容**：它只理解不回答，回答永远是 LLM 的事。
4. **计费按 token**：入库是一次性成本，用户每次提问查询一次。
5. 向量维度越高表达越细，但存储和计算成本越大，够用就好。

