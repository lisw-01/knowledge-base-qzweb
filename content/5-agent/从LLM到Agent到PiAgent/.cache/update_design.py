import re

p = 'DESIGN.md'
s = open(p, encoding='utf-8').read()

# 映射表：>= 04 的页码 +1，并在 03 后插入新行
lines = s.split('\n')
out = []
inserted = False
new_row = '| 04 | 04.slide | content | supporting | peak | 四卡横排+代码 | CodeBlock(messages) + 4 张 role 卡 | 240 | 20% | 主色 46% + 强调 14% | 四卡等高、role 名用等宽；代码块占下方 ≥ 30% |'
in_table = False
for ln in lines:
    if ln.startswith('| # | 文件 |'):
        in_table = True
    m = re.match(r'^\| (\d{2}) \| (\d{2})\.slide \|', ln)
    if m:
        n = int(m.group(1))
        if n == 3:
            out.append(ln)
            out.append(new_row)
            inserted = True
            continue
        if n >= 4:
            ln = ln.replace(f'| {n:02d} | {n:02d}.slide |', f'| {n+1:02d} | {n+1:02d}.slide |', 1)
        out.append(ln)
        continue
    out.append(ln)
s = '\n'.join(out)

# L1 映射表页码
s = s.replace('| `assets/sec_agent.png` | 10 第 2 章扉页底图', '| `assets/sec_agent.png` | 11 第 2 章扉页底图')
s = s.replace('| `assets/sec_pi.png` | 19 第 3 章扉页底图', '| `assets/sec_pi.png` | 20 第 3 章扉页底图')
s = s.replace('| `assets/sec_practice.png` | 26 第 4 章扉页底图', '| `assets/sec_practice.png` | 27 第 4 章扉页底图')
s = s.replace('| `assets/ending_hero.png` | 33 结束页底图', '| `assets/ending_hero.png` | 34 结束页底图')

# 页码格式
s = s.replace('C 区页码 `NN / 33` 逐页递增', 'C 区页码 `NN / 34` 逐页递增')

open(p, 'w', encoding='utf-8').write(s)
print('inserted:', inserted)
