1. 在 `agent-study` 文件夹新建文件，名字 **`.env`**

> Windows 新建文件时，文件名写 `.env`，注意：文件名前面带点，没有后缀 txt
> 
> 文件里面写入：

env

```
ZHIPU_API_KEY=在这里粘贴你的智谱key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

> 获取 key 地址：[https://open.bigmodel.cn/](https://open.bigmodel.cn/) 登录 → 控制台 → API 密钥管理，复制密钥

2. 新建代码文件 `llm_demo.py`，复制下面代码

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
