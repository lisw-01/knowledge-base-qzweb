import re

p = 'STORY.md'
s = open(p, encoding='utf-8').read()

# ① 总页数
s = s.replace('**PPT 长度**：33 页（封面 + 目录 + 4 章 + 结束页）', '**PPT 长度**：34 页（封面 + 目录 + 4 章 + 结束页）')
s = s.replace('**页面总数与分章（33 页 / 4 章）**', '**页面总数与分章（34 页 / 4 章）**')

# ② 分章表
s = s.replace('| 第 1 章 LLM：一切的地基 | 03–09 | 7 |', '| 第 1 章 LLM：一切的地基 | 03–10 | 8 |')
s = s.replace('| 第 2 章 Agent：从"能聊"到"能干" | 10–18 | 9 |', '| 第 2 章 Agent：从"能聊"到"能干" | 11–19 | 9 |')
s = s.replace('| 第 3 章 Pi Agent：一个极简范式 | 19–25 | 7 |', '| 第 3 章 Pi Agent：一个极简范式 | 20–26 | 7 |')
s = s.replace('| 第 4 章 落地实践：智数问答 agent-DQ | 26–32 | 7 |', '| 第 4 章 落地实践：智数问答 agent-DQ | 27–33 | 7 |')
s = s.replace('| 结束页 | 33 | 1 |', '| 结束页 | 34 | 1 |')

# ③ 目录契约
s = s.replace('| 01 · LLM：一切的地基 | 第 03 页 | `01 · LLM：一切的地基` | 03–09 |',
              '| 01 · LLM：一切的地基 | 第 03 页 | `01 · LLM：一切的地基` | 03–10 |')
s = s.replace('| 02 · Agent：从"能聊"到"能干" | 第 10 页 | `02 · Agent：从"能聊"到"能干"` | 10–18 |',
              '| 02 · Agent：从"能聊"到"能干" | 第 11 页 | `02 · Agent：从"能聊"到"能干"` | 11–19 |')
s = s.replace('| 03 · Pi Agent：一个极简范式 | 第 19 页 | `03 · Pi Agent：一个极简范式` | 19–25 |',
              '| 03 · Pi Agent：一个极简范式 | 第 20 页 | `03 · Pi Agent：一个极简范式` | 20–26 |')
s = s.replace('| 04 · 落地实践：智数问答 agent-DQ | 第 26 页 | `04 · 落地实践：智数问答 agent-DQ` | 26–32 |',
              '| 04 · 落地实践：智数问答 agent-DQ | 第 27 页 | `04 · 落地实践：智数问答 agent-DQ` | 27–33 |')

# ④ Hero
s = s.replace('**Hero 页定位（7 页 / 21%）：** 01（封面）· 11（Agent 公式）· 15（七层地图）· 21（418 行核心）· 23（完整数据流）· 28（三级路由）· 33（结束页）。',
              '**Hero 页定位（7 页 / 21%）：** 01（封面）· 12（Agent 公式）· 16（七层地图）· 22（418 行核心）· 24（完整数据流）· 29（三级路由）· 34（结束页）。')
s = s.replace('间隔校验：01→11→15→21→23→28→33', '间隔校验：01→12→16→22→24→29→34')

# ⑤ rhythm 曲线：旧曲线 +1 位移，并插入新第 04 页（peak）
old = '01 peak｜02 valley｜03 transition｜04 valley｜05 valley｜06 peak｜07 valley｜08 valley｜09 peak｜10 transition｜11 peak｜12 valley｜13 peak｜14 valley｜15 peak｜16 valley｜17 peak｜18 valley｜19 transition｜20 valley｜21 peak｜22 valley｜23 peak｜24 valley｜25 valley｜26 transition｜27 valley｜28 peak｜29 valley｜30 valley｜31 peak｜32 valley｜33 peak'
items = old.split('｜')
new_items = []
for it in items:
    n, r = it.split(' ')
    n = int(n)
    n2 = n if n < 4 else n + 1
    new_items.append(f'{n2:02d} {r}')
new_items.append('04 peak')
new_items.sort(key=lambda x: int(x.split(' ')[0]))
s = s.replace(old, '｜'.join(new_items))

# ⑥ 预算
s = s.replace('**非对称版式预算：** 内容页 28 页中 27 页使用非对称版式（96% ≥ 40%）。✅',
              '**非对称版式预算：** 内容页 29 页中 27 页使用非对称版式（93% ≥ 40%）。✅')
s = s.replace('**对称版式预算：** 仅第 09 页使用', '**对称版式预算：** 仅第 10 页使用')
s = s.replace('**`N卡片横排` 出现次数：** 0（≤2）。✅', '**`N卡片横排` 出现次数：** 1（第 04 页 role 四卡，≤2）。✅')
s = s.replace('**`左大图+右侧文字` + `非对称双栏` 合计：** 7 页（`非对称双栏` 于 05/13/17/20/25/27/30），占 21%（≤40%）。✅',
              '**`左大图+右侧文字` + `非对称双栏` 合计：** 7 页（`非对称双栏` 于 06/14/18/21/26/28/31），占 21%（≤40%）。✅')

# ⑦ ③ 页面大纲表：>= 04 的行号 +1，并插入新行
lines = s.split('\n')
out = []
inserted = False
new_row = '| 04 | messages 里的 role：谁在说话 | content | supporting | peak | 四卡横排+代码 | CodeBlock(messages 数组) + 4 张 role 卡 | evidence | 字数约240 / 图1 / 留白20% | 禁止把 role 当日志字段讲；禁止只列四个名字不说回填规则 | system 定规则 / user 提需求 / assistant 留痕 / tool 回事实。判断：role 决定这段话被当成指令、提问、自己的话，还是外部事实。 |'
in_table = False
for ln in lines:
    m = re.match(r'^\| (\d{2}) \|', ln)
    if m:
        in_table = True
        n = int(m.group(1))
        if n == 3:
            out.append(ln)
            out.append(new_row)
            inserted = True
            continue
        if n >= 4:
            ln = f'| {n+1:02d} |' + ln[len(f'| {m.group(1)} |'):]
        out.append(ln)
        continue
    out.append(ln)
s = '\n'.join(out)
print('inserted row:', inserted)
open(p, 'w', encoding='utf-8').write(s)
