> 核心一句话：**向量库就是一个"专门存向量 + 会按相似度快速查找"的数据库**：存的东西 = 向量 + 原文 + 标签；核心能力 = 给我一个向量，毫秒级从几十万条里找出最相似的 K 条。

## 一、向量库的 API 其实只有 4 个动作

不管 FAISS、Chroma 还是 Milvus，剥掉外壳核心就这几个：

| 操作       | 干什么                 | 使用时机      |
| -------- | ------------------- | --------- |
| `add`    | 存入 向量+原文+标签         | 入库阶段（一次性） |
| `search` | 给一个查询向量，返回最相似的 topK | 用户每次提问    |
| `delete` | 按 id 删除某条           | 知识过期/删文档  |
| `update` | 删了重加                | 修改某段知识    |

## 二、向量库到底存什么

向量库存的是一条条的"记录"，每条记录 4 样东西：

```
┌──────┬──────────────────────────────┬────────────────────────┬──────────────┐
│ id   │ vector（向量，1024个浮点数）      │ text（原文）              │ metadata（标签）│
├──────┼──────────────────────────────┼────────────────────────┼──────────────┤
│ 1    │ [0.021, -0.113, 0.876, ...]   │ 退货需在签收后7天内申请...   │ 来源:售后.md   │
│ 2    │ [-0.33, 0.52, -0.07, ...]     │ 会员积分100积分抵1元...     │ 来源:会员.md   │
│ 3    │ [0.11, 0.04, -0.55, ...]      │ 客服时间9:00-21:00...      │ 来源:客服.md   │
│ ...  │ ...                           │ ...                     │ ...          │
└──────┴──────────────────────────────┴────────────────────────┴──────────────┘
```

三个关键认知：

1. **向量不是替换原文，而是原文的"检索索引"**——就像书的内容和目录的关系：查的时候用目录（向量），读的时候翻正文（原文）。检索完要把**原文**拼进 Prompt 给 LLM，向量本身没法读。
2. **原文必须跟着存**（或存个能找回原文的 id）。
3. **metadata 用来过滤**：比如先筛"分类=售后"的 500 条，再在其中做相似度检索（按分类/时间/部门缩小范围）。

> 就算你不用向量库、用普通数据库存，这张表也一样要建——向量库只是把"按相似度查"这一步做得飞快。



## 三、亲手写一个"迷你向量库"

向量库的本质，就是下面这个类——**先把它的逻辑看懂，向量库对你就不黑盒了**：

```python
# mini_vector_db.py —— 实现一个向量库
# mini_vector_db.py —— 30行实现一个向量库

import math
import requests, os
from dotenv import load_dotenv
load_dotenv()
from mypackage import embed
#余弦相似度计算
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)

class MiniVectorDB:

    def __init__(self):
        self.data = []   # 每条：{"id", "vector", "text", "metadata"}

    def add(self, texts, metadatas=None):
        vecs = embed(texts)
        for i, (t, v) in enumerate(zip(texts, vecs)):
            self.data.append({
                "id": len(self.data), "vector": v, "text": t,
                "metadata": metadatas[i] if metadatas else {}
            })

    def search(self, query, top_k=3):
        q_vec = embed([query])[0]
        scores =[cosine_similarity(q_vec, d["vector"]) for d in self.data]
        print("scores:",scores)
        ranked = sorted(zip(scores, self.data), key=lambda x: x[0], reverse=True)
        print("ranked:",ranked)
        return [{"text": d["text"], "metadata": d["metadata"],  
                 "score": score} for score, d in ranked[:top_k]]

  
  

# ===== 用起来 =====

db = MiniVectorDB()

db.add(["退货需在签收后7天内申请，保持吊牌完好",

        "会员积分100积分抵1元",

        "客服时间9:00-21:00"])

print('###向量库内容### start')

print(db.data)

print('###向量库内容### end')

# [{'text': '退货需在签收后7天内申请...', 'score': 0.87}, ...]
print(db.search("买完东西多久能退", top_k=2))
```

**Chroma、Milvus 这些真向量库 = 把上面这个类，做成了**：

1. **快**：暴力遍历换成 ANN 索引（毫秒级）
2. **持久化**：数据存磁盘，程序重启不丢（我们这个重启就没了）
3. **能过滤**：search 时支持 `where={"分类": "售后"}` 按 metadata 筛
4. **服务化**（Milvus 等企业级）：独立进程/集群，多个应用连它，像 MySQL 一样

## 四、换真向量库（Chroma，5行接入）

Chroma 是入门首选：`pip install chromadb`，数据自动落盘，API 和上面迷你版几乎一样：

```python
import chromadb

client = chromadb.PersistentClient(path="./vec_store")   # 自动持久化

# 隐士调用DefaultEmbeddingFunction这个函数
# 默认模型 all-MiniLM-L6-v2 是英文模型！中文检索效果很差
col = client.get_or_create_collection("faq")

# 等价于隐式带上
#from chromadb.utils.embedding_functions import DefaultEmbeddingFunction 
# col = client.get_or_create_collection("faq",embedding_function=DefaultEmbeddingFunction())



# ① add：向量和原文一起存（Chroma 能自动调 embedding，也可显式传入）
texts = ["退货需在签收后7天内申请，保持吊牌完好",
         "会员积分100积分抵1元",
         "客服时间9:00-21:00"]
col.add(ids=["1", "2", "3"], documents=texts)

# ② search：给问题，直接返回最相似的 topK 原文
res = col.query(query_texts=["买完东西多久能退"], n_results=2)
print(res["documents"])   # [['退货需在签收后7天内申请...', '会员积分...']]
```

对比迷你版：`add` / `search` 一一对应，只是**不用自己调 embedding、不用自己算余弦、数据自动存磁盘**。

## 五、常见向量库怎么选

| 向量库 | 是什么 | 什么时候用 |
| --- | --- | --- |
| 手写列表/NumPy | 几十行代码 | demo、几百条以内，**学习原理用** |
| FAISS | 一个 Python 库（不是服务），Facebook 出品，只管检索 | 单机、数据量大、不想装服务 |
| **Chroma** | 嵌入式库，开箱即用，自动落盘 | **入门/中小项目首选** |
| pgvector | PostgreSQL 插件 | 项目已有 Postgres，不想多加组件 |
| Milvus | 独立数据库服务，支持集群 | 生产级海量数据（千万~亿级） |
| Zilliz / Pinecone | 云托管向量库 | 不想自己运维 |

选型口诀：**学习用 Chroma；已有 PG 用 pgvector；数据上千万再上 Milvus**。



## 六、在 RAG 中的位置（一句话串起来）

```
RAG 流程：文档 → 切块 → Embedding →【向量库 add】
         提问 → Embedding →【向量库 search topK】→ 拼Prompt → LLM回答
```

向量库在 RAG 里只干两件事：**入库时存起来（add），提问时找出来（search）**——剩下的切块、Prompt、生成都是 RAG 流程自己的事（见 [RAG]()）。

## 七、向量库和"用列表暴力遍历"有什么区别

RAG demo 里我们是这么找的：

```python
scores = [cosine_sim(q_vec, dv) for dv in doc_vecs]   # 每条算一次相似度
```

- 3 条数据：无所谓，瞬间出结果
- **30 万条数据**：每次提问要算 30 万次余弦（每次 1024 次乘法）≈ 3 亿次浮点运算，Python 跑一遍要好几秒，每个用户每次提问都来一遍，服务器直接炸

向量库的解法：**近似最近邻检索（ANN）**——

- 暴力遍历：一条条比，保证 100% 准，但 O(n) 慢
- ANN：预先把向量"分好组、建好索引"，查找时只跟相近组的几百条比，**牺牲一点点精度（第 1 名偶尔变第 2、3 名），换来毫秒级返回**
- 类比：查字典不用翻遍每一页，拼音目录直接跳到那一区间——向量库就是给向量建了个"拼音目录"（如 HNSW 算法，原理不用深究，知道"分组+跳查"即可）

| 方式 | 30万条查找耗时 | 精度 |
| --- | --- | --- |
| 列表暴力遍历 | 秒级 | 100% |
| 向量库（ANN索引） | 毫秒级 | ~95%+（top10 里基本包含正确答案） |

> RAG 里取的是 topK（K=3~5），ANN 偶尔排序偏差完全可接受。







