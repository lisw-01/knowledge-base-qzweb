import os, sys

d = 'slides'
# 1) 26..34 -> 29..37（降序）
for i in range(34, 25, -1):
    src = f'{d}/{i:02d}.slide'
    dst = f'{d}/{i+3:02d}.slide'
    if not os.path.exists(src):
        print('MISSING', src); sys.exit(1)
    os.rename(src, dst)

# 2) 总页数 34 -> 37
for n in range(1, 38):
    p = f'{d}/{n:02d}.slide'
    if not os.path.exists(p):
        continue
    s = open(p, encoding='utf-8').read()
    s = s.replace(' / 34', ' / 37')

    # 3) 29..37 = 原 26..34，页码 +3
    if n >= 29:
        s = s.replace(f'{n-3:02d} / 37', f'{n:02d} / 37')

    # 4) 章节区间 / 目录区间
    s = s.replace('PAGES 20 – 26', 'PAGES 20 – 29')
    s = s.replace('PAGES 27 – 33', 'PAGES 30 – 36')
    s = s.replace('四章 · 34 页', '四章 · 37 页')
    s = s.replace("p: '20–26'", "p: '20–29'")
    s = s.replace("p: '27–33'", "p: '30–36'")
    open(p, 'w', encoding='utf-8').write(s)

print('files:', len(os.listdir(d)), 'last:', sorted(os.listdir(d))[-1])
