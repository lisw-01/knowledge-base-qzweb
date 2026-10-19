import os

base = 'slides'

# 1) 原 29..37 -> 38..46（倒序，避免冲突）
for old in range(37, 28, -1):
    new = old + 9
    src = f'{base}/{old:02d}.slide'
    dst = f'{base}/{new:02d}.slide'
    s = open(src, encoding='utf-8').read()
    s = s.replace(f'{old:02d} / 37', f'{new:02d} / 46')
    open(dst, 'w', encoding='utf-8').write(s)
    os.remove(src)

# 2) 删除原 26/27/28（已备份，将由新的 26-37 取代）
for old in (26, 27, 28):
    p = f'{base}/{old:02d}.slide'
    if os.path.exists(p):
        os.remove(p)

# 3) 01..25 页脚总数
for i in range(1, 26):
    p = f'{base}/{i:02d}.slide'
    s = open(p, encoding='utf-8').read()
    s = s.replace(f'{i:02d} / 37', f'{i:02d} / 46')
    open(p, 'w', encoding='utf-8').write(s)

# 4) 目录页章节区间
p = f'{base}/02.slide'
s = open(p, encoding='utf-8').read()
s = s.replace("'20–29'", "'20–38'").replace("'30–36'", "'39–45'")
open(p, 'w', encoding='utf-8').write(s)

# 5) 两张章节扉页的 PAGES 区间
for f, old, new in [('20', '20 – 29', '20 – 38'), ('39', '30 – 36', '39 – 45')]:
    p = f'{base}/{f}.slide'
    s = open(p, encoding='utf-8').read()
    s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)

print('done')
