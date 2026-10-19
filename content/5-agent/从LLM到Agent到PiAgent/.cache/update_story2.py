import re

p = 'STORY.md'
s = open(p, encoding='utf-8').read()

s = s.replace('**PPT 长度**：34 页（封面 + 目录 + 4 章 + 结束页）', '**PPT 长度**：37 页（封面 + 目录 + 4 章 + 结束页）')
s = s.replace('**页面总数与分章（34 页 / 4 章）**', '**页面总数与分章（37 页 / 4 章）**')

s = s.replace('| 第 3 章 Pi Agent：一个极简范式 | 20–26 | 7 |', '| 第 3 章 Pi Agent：一个极简范式 | 20–29 | 10 |')
s = s.replace('| 第 4 章 落地实践：智数问答 agent-DQ | 27–33 | 7 |', '| 第 4 章 落地实践：智数问答 agent-DQ | 30–36 | 7 |')
s = s.replace('| 结束页 | 34 | 1 |', '| 结束页 | 37 | 1 |')

s = s.replace('| 03 · Pi Agent：一个极简范式 | 第 20 页 | `03 · Pi Agent：一个极简范式` | 20–26 |',
              '| 03 · Pi Agent：一个极简范式 | 第 20 页 | `03 · Pi Agent：一个极简范式` | 20–29 |')
s = s.replace('| 04 · 落地实践：智数问答 agent-DQ | 第 27 页 | `04 · 落地实践：智数问答 agent-DQ` | 27–33 |',
              '| 04 · 落地实践：智数问答 agent-DQ | 第 30 页 | `04 · 落地实践：智数问答 agent-DQ` | 30–36 |')

s = s.replace('**Hero 页定位（7 页 / 21%）：** 01（封面）· 12（Agent 公式）· 16（七层地图）· 22（418 行核心）· 24（完整数据流）· 29（三级路由）· 34（结束页）。',
              '**Hero 页定位（7 页 / 19%）：** 01（封面）· 12（Agent 公式）· 16（七层地图）· 22（418 行核心）· 24（完整数据流）· 32（三级路由）· 37（结束页）。')
s = s.replace('间隔校验：01→12→16→22→24→29→34', '间隔校验：01→12→16→22→24→32→37')

# rhythm
old = s.split('**rhythm 曲线**\n\n')[1].split('\n')[0]
items = old.split('｜')
new_items = []
for it in items:
    n, r = it.split(' ')
    n = int(n)
    n2 = n if n < 26 else n + 3
    new_items.append(f'{n2:02d} {r}')
new_items += ['26 valley', '27 peak', '28 valley']
new_items.sort(key=lambda x: int(x.split(' ')[0]))
s = s.replace(old, '｜'.join(new_items))

s = s.replace('**非对称版式预算：** 内容页 29 页中 27 页使用非对称版式（93% ≥ 40%）。✅',
              '**非对称版式预算：** 内容页 32 页中 30 页使用非对称版式（94% ≥ 40%）。✅')
s = s.replace('**`N卡片横排` 出现次数：** 1（第 04 页 role 四卡，≤2）。✅',
              '**`N卡片横排` 出现次数：** 2（第 04 页 role 四卡、第 28 页上二下一，≤2）。✅')
s = s.replace('7 页（`非对称双栏` 于 06/14/18/21/26/28/31），占 21%（≤40%）。✅',
              '7 页（`非对称双栏` 于 06/14/18/21/29/31/34），占 19%（≤40%）。✅')

# ③ 表格：>= 26 行号 +3，并在 25 后插三行
lines = s.split('\n')
out = []
inserted = False
rows = [
 '| 26 | 设计点 ①–③：模型 · 上下文 · 工具 | content | supporting | valley | 三条分栏 | 无图 · 三段式说明 | evidence | 字数约330 / 图0 / 留白16% | 禁止写成功能清单；禁止只讲机制不讲取舍 | 模型适配（统一类型+归一化流）、上下文工程（常驻最小化+compaction）、工具系统（三视角+四阶段流水线）。判断：这三层决定「和模型打交道」的质量。 |',
 '| 27 | 设计点 ④–⑥：会话 · 循环 · 扩展 | content | supporting | peak | 三卡纵排 | 无图 · 卡片组 | evidence | 字数约330 / 图0 / 留白16% | 禁止与上一页版式雷同；禁止重复七层地图的表述 | 会话（追加式 JSONL + 树形分叉）、循环（418 行双层 while + 队列插话 + 三类停止原语）、扩展（钩子 + registerTool + virtual modules）。判断：内核的「少」是靠这三层撑住的。 |',
 '| 28 | 设计点 ⑦–⑨：事件 · 安全 · 远程 | content | supporting | valley | 上二下一 | 无图 · 卡片组 + 通栏 | evidence | 字数约340 / 图0 / 留白16% | 禁止三卡等分；禁止把安全讲成"没有安全" | 事件（四档粒度 + 产品层事件）、安全与可观测（无沙箱 + 三道防线 + usage/telemetry/evals）、远程会话栈（CBOR + 传输无关 + 租约）。判断：九点连起来是一套可复用骨架。 |',
]
for ln in lines:
    m = re.match(r'^\| (\d{2}) \|', ln)
    if m:
        n = int(m.group(1))
        if n == 25:
            out.append(ln)
            out.extend(rows)
            inserted = True
            continue
        if n >= 26:
            ln = f'| {n+3:02d} |' + ln[len(f'| {m.group(1)} |'):]
        out.append(ln)
        continue
    out.append(ln)

s = '\n'.join(out)
print('inserted:', inserted)
open(p, 'w', encoding='utf-8').write(s)
