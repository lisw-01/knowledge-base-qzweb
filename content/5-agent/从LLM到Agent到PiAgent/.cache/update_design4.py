# -*- coding: utf-8 -*-
"""DESIGN.md：删除第 37 页后同步 46 -> 45 页。"""
import re

p = 'DESIGN.md'
s = open(p, encoding='utf-8').read()

out = []
for line in s.split('\n'):
    m = re.match(r'^\| (\d{2}) \| \d{2}\.slide \|', line)
    if m:
        n = int(m.group(1))
        if n == 37:
            continue
        if n >= 38:
            line = re.sub(r'^\| \d{2} \| \d{2}\.slide \|', '| %02d | %02d.slide |' % (n - 1, n - 1), line)
    out.append(line)
s = '\n'.join(out)

s = s.replace('`assets/ending_hero.png` | 46 结束页底图', '`assets/ending_hero.png` | 45 结束页底图')
s = s.replace('C 区页码 `NN / 46`', 'C 区页码 `NN / 45`')

open(p, 'w', encoding='utf-8').write(s)
print('DESIGN ok')
