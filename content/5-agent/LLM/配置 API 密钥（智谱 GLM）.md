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
import os
import requests
from dotenv import load_dotenv

# 加载.env文件里面的密钥
load_dotenv()

api_key = os.getenv("ZHIPU_API_KEY")
base_url = os.getenv("ZHIPU_BASE_URL")

resp = requests.post(
    f"{base_url}/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "glm-4-flash",
        "temperature": 0,
        "messages": [
            {"role": "user", "content": "一句话解释什么是LLM"}
        ]
    }
)

result = resp.json()["choices"][0]["message"]["content"]
print("LLM输出结果：", result)
```