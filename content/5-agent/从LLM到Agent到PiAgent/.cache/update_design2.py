import re

p = 'DESIGN.md'
s = open(p, encoding='utf-8').read()

lines = s.split('\n')
out = []
inserted = False
rows = [
 '| 26 | 26.slide | content | supporting | valley | 三条分栏（左名/中问题机制/右取舍） | 无图 | 330 | 16% | 主色 50% + 强调 10% | 三行等高、分隔线不用卡片；禁止与 27/28 版式雷同 |',
 '| 27 | 27.slide | content | supporting | peak | 三卡纵排 | 无图 · 卡片组 | 330 | 16% | 主色 46% + 强调 12% | 卡片描边 + 圆角；编号与名称同行 |',
 '| 28 | 28.slide | content | supporting | valley | 上二下一 + 结论条 | 无图 · 卡片组 + 通栏 | 340 | 16% | 主色 46% + 强调 12% | 上排两卡等高；下排通栏占满；尾条钉底 |',
]
for ln in lines:
    m = re.match(r'^\| (\d{2}) \| (\d{2})\.slide \|', ln)
    if m:
        n = int(m.group(1))
        if n == 25:
            out.append(ln)
            out.extend(rows)
            inserted = True
            continue
        if n >= 26:
            ln = ln.replace(f'| {n:02d} | {n:02d}.slide |', f'| {n+3:02d} | {n+3:02d}.slide |', 1)
        out.append(ln)
        continue
    out.append(ln)
s = '\n'.join(out)

s = s.replace('| `assets/sec_practice.png` | 27 章节扉页底图', '| `assets/sec_practice.png` | 30 章节扉页底图')
s = s.replace('| `assets/ending_hero.png` | 34 结束页底图', '| `assets/ending_hero.png` | 37 结束页底图')
s = s.replace('C 区页码 `NN / 34` 逐页递增', 'C 区页码 `NN / 37` 逐页递增')

open(p, 'w', encoding='utf-8').write(s)
print('inserted:', inserted)
