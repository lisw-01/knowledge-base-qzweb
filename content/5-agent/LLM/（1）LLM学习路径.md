LLM = **Large Language Model，大语言模型**


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
    
6. **Embedding（嵌入向量）**
    
    把文本转为一串数字向量，用来做相似度检索，**RAG 的核心**。
    
    > Agent 长期记忆靠 Embedding + 向量数据库（Chroma、Milvus）。
    



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



## 三 、   LLM功能
LLM 是能理解、生成人类语言，可完成推理、归纳、文本转换，还能配合外部工具做规划决策的大语言模型。

