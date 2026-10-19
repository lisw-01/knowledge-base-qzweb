# -*- coding: utf-8 -*-
"""STORY.md：删除第 37 页后同步 46 -> 45 页。"""
import re

p = 'STORY.md'
s = open(p, encoding='utf-8').read()

# 1. 表格行：删除第 37 行，38..46 前移
out = []
for line in s.split('\n'):
    m = re.match(r'^\| (\d{2}) \|', line)
    if m:
        n = int(m.group(1))
        if n == 37:
            continue
        if n >= 38:
            line = re.sub(r'^\| \d{2} \|', '| %02d |' % (n - 1), line)
    out.append(line)
s = '\n'.join(out)

# 2. 总数与分章
s = s.replace('**页面总数与分章（46 页 / 4 章）**', '**页面总数与分章（45 页 / 4 章）**')
s = s.replace('| 第 3 章 Pi Agent：一个极简范式 | 20–38 | 19 |',
              '| 第 3 章 Pi Agent：一个极简范式 | 20–37 | 18 |')
s = s.replace('| 第 4 章 落地实践：智数问答 agent-DQ | 39–45 | 7 |',
              '| 第 4 章 落地实践：智数问答 agent-DQ | 38–44 | 7 |')
s = s.replace('| 结束页 | 46 | 1 |', '| 结束页 | 45 | 1 |')

# 3. 目录↔扉页契约
s = s.replace('| `03 · Pi Agent：一个极简范式` | 20–38 |', '| `03 · Pi Agent：一个极简范式` | 20–37 |')
s = s.replace('| 04 · 落地实践：智数问答 agent-DQ | 第 39 页 |', '| 04 · 落地实践：智数问答 agent-DQ | 第 38 页 |')
s = s.replace('| `04 · 落地实践：智数问答 agent-DQ` | 39–45 |', '| `04 · 落地实践：智数问答 agent-DQ` | 38–44 |')

# 4. Hero 页
s = s.replace('· 41（三级路由）· 46（结束页）', '· 40（三级路由）· 45（结束页）')
s = s.replace('01→12→16→22→24→26→32→41→46', '01→12→16→22→24→26→32→40→45')

# 5. rhythm 曲线：删 37，38..46 前移
s = s.replace('｜37 peak｜38 valley｜39 transition｜40 valley｜41 peak｜42 valley｜43 valley｜44 peak｜45 valley｜46 peak',
              '｜37 valley｜38 transition｜39 valley｜40 peak｜41 valley｜42 valley｜43 peak｜44 valley｜45 peak')

# 6. 预算
s = s.replace('内容页 41 页中 38 页使用非对称版式', '内容页 40 页中 37 页使用非对称版式')
s = s.replace('12 页（06/14/18/21/26/28/30/31/34/36/37/38），占 29%',
              '11 页（06/14/18/21/26/28/30/31/34/36/37），占 28%')

open(p, 'w', encoding='utf-8').write(s)
print('STORY ok')
