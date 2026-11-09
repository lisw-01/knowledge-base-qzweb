目录结构：

-mypackage
    -comm.py
    -__init__.py



```python
# comm.py
import requests

import os

from dotenv import load_dotenv

load_dotenv()

  

BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

API_KEY = os.getenv("ZHIPU_API_KEY")

def llm(messages, stop=None, tools=None):

    body = {"model": "glm-4-flash", "temperature": 0, "messages": messages}

    if tools:

        body["tools"] = tools

    if stop:

        body["stop"] = stop

    resp = requests.post(f"{BASE_URL}/chat/completions",

        headers={"Authorization": f"Bearer {API_KEY}"},

        json=body)

  
  

    # 打印返回结果

    # print('###模型返回结果###',resp.json())

    # 返回完整 message：普通回答取 ["content"]，工具调用取 ["tool_calls"]

    return resp.json()["choices"][0]["message"]

  
  
  
  def embed(texts):

    """调 embedding 模型，批量把文本变成向量（embedding-3，默认2048维）"""

    resp = requests.post(f"{BASE_URL}/embeddings",

        headers={"Authorization": f"Bearer {API_KEY}"},

        json={"model": "embedding-3", "input": texts})

    return [item["embedding"] for item in resp.json()["data"]]
  
  

# 可用  from xx  import *  来导入 【 控制import * 的导入范围】

__all__ = ["llm","embed"]

```


``` python
# __init__.py
  
  

#在 __init__.py 里导出，外部直接从包导入(支持多文件)：

# from mypackage import llm

  

from .comm import *

  

__all__ = ["llm", "embed"]

```
