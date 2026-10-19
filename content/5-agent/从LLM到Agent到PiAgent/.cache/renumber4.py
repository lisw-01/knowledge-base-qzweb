# -*- coding: utf-8 -*-
"""删除第 37 页（设计点 ⑨ 远程会话栈），全篇 46 -> 45 页并重编号。"""
import os, re, shutil, glob

DIR = 'slides'
OLD_TOTAL, NEW_TOTAL = 46, 45
DEL = 37

files = sorted(glob.glob(os.path.join(DIR, '*.slide')))
m = {}
for f in files:
    m[int(os.path.basename(f)[:2])] = f

# 1. 删除第 37 页，38..46 -> 37..45（从大到小改名，避免覆盖）
os.remove(m[DEL])
for i in range(DEL + 1, OLD_TOTAL + 1):
    shutil.move(m[i], os.path.join(DIR, '%02d.slide' % (i - 1)))

# 2. 逐页修正页脚与章节区间
for i in range(1, NEW_TOTAL + 1):
    p = os.path.join(DIR, '%02d.slide' % i)
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'\b\d{2} / %d\b' % OLD_TOTAL, '%02d / %d' % (i, NEW_TOTAL), s)
    s = s.replace('PAGES 20 – 38', 'PAGES 20 – 37').replace('PAGES 39 – 45', 'PAGES 38 – 44')
    s = s.replace("p: '20–38'", "p: '20–37'").replace("p: '39–45'", "p: '38–44'")
    open(p, 'w', encoding='utf-8').write(s)

# 3. 索引页（25）承接关系：十二页 -> 十一页；⑨ 标记为「不展开」
p = os.path.join(DIR, '25.slide')
s = open(p, encoding='utf-8').read()
s = s.replace('接下来十二页，逐个拆开看', '接下来十一页，逐个拆开看')
s = s.replace(
    "['9', '远程会话栈', 'CBOR 远程会话：协议 / 客户端 / 服务端三层，可选，不影响核心四层', '独立叠加'],",
    "['9', '远程会话栈', 'CBOR 远程会话：协议 / 客户端 / 服务端三层，可选，不影响核心四层（现场不展开）', '独立叠加 · 略'],")
open(p, 'w', encoding='utf-8').write(s)

print('done, files =', len(glob.glob(os.path.join(DIR, '*.slide'))))
