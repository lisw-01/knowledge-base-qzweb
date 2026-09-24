
## 一、在线编程环境（推荐！免安装 Python，浏览器直接跑代码）

### 1. Google Colab（首选，免费）

网址：[https://colab.research.google.com/](https://colab.research.google.com/)

- 优点：自带 Python 环境，直接新建 notebook，复制代码运行；支持`pip install`安装包
- 用法：新建笔记本 → 粘贴代码 → 把你的智谱 API Key 填进去，直接调用 GLM
- 缺点：国内访问需要特殊网络

### 2. Kaggle Notebook（免费）

网址：[https://www.kaggle.com/notebooks](https://www.kaggle.com/notebooks)

- 同样 Jupyter 环境，预装很多包；国内访问比 Colab 稍微好一点

### 3. 国内替代：ModelScope 魔搭 Notebook【强烈推荐，国内直连】

网址：[https://modelscope.cn/notebooks](https://modelscope.cn/notebooks)

✅ 国内可直接打开，不用翻墙

✅ 预装 Python，支持 pip，**自带国内大模型（智谱、通义千问等）**

✅ 两种玩法：

① 直接调用模型 API（和你本地写代码一模一样，适合学习 LLM 调用、Function Calling、Agent）

② 可选本地加载小模型（如 Qwen-1.8B，体验本地 LLM 推理，可选，不强制）

### 4. DSW 阿里云 PAI-DSW（有免费额度）

[https://www.aliyun.com/product/bigdata/dsw](https://www.aliyun.com/product/bigdata/dsw)

在线 jupyter 环境，适合长期写较长项目。

### 5. 极简在线代码运行（只跑小段 Python，不装复杂包）

- Replit：[https://replit.com/](https://replit.com/)
    
    可以新建 Python 项目，直接在线写代码，环境简单，适合跑短小 Demo（LLM API 调用完全没问题）

> 注意：Replit 免费版休眠，适合测试小段代码。





## 二、本地环境（后期推荐，长期写 Agent 项目）

**不需要部署大模型！仅仅是在电脑上装 Python，调用远程 LLM API**

安装步骤：

1.   [[下载 Python]]
2.   [[VS Code + Python 插件]]
3.   [[创建项目 + 虚拟环境]]
4.   [[安装依赖包]]
5.   [[配置 API 密钥（智谱 GLM）]]
6.   [[运行代码]]

> 区分重点：
> 
> - 调用 API：代码在你电脑 / 在线环境，**大模型跑在厂商服务器**（入门学习首选）
> - 本地跑 LLM（Ollama）：电脑显卡本地运行大模型，**属于进阶内容**，入门阶段不用搞，后面想玩再学。