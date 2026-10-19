import os, sys

d = 'slides'
files = sorted(os.listdir(d))
print('before:', len(files), files[0], files[-1])

# 1) 把 04..33 依次后移为 05..34（降序避免覆盖）
for i in range(33, 3, -1):
    src = f'{d}/{i:02d}.slide'
    dst = f'{d}/{i+1:02d}.slide'
    if not os.path.exists(src):
        print('MISSING', src); sys.exit(1)
    os.rename(src, dst)

# 2) 总页数 33 -> 34
for n in range(1, 35):
    p = f'{d}/{n:02d}.slide'
    if not os.path.exists(p):
        continue
    s = open(p, encoding='utf-8').read()
    s = s.replace(' / 33', ' / 34')

    # 3) 页码上移一位（新第 n 页 = 原第 n-1 页）
    if n >= 5:
        s = s.replace(f'{n-1:02d} / 34', f'{n:02d} / 34')

    # 4) 章节区间
    s = s.replace('PAGES 03 – 09', 'PAGES 03 – 10')
    s = s.replace('PAGES 10 – 18', 'PAGES 11 – 19')
    s = s.replace('PAGES 19 – 25', 'PAGES 20 – 26')
    s = s.replace('PAGES 26 – 32', 'PAGES 27 – 33')
    s = s.replace('四章 · 33 页', '四章 · 34 页')
    s = s.replace("p: '03–09'", "p: '03–10'")
    s = s.replace("p: '10–18'", "p: '11–19'")
    s = s.replace("p: '19–25'", "p: '20–26'")
    s = s.replace("p: '26–32'", "p: '27–33'")
    open(p, 'w', encoding='utf-8').write(s)

print('after:', len(os.listdir(d)), sorted(os.listdir(d))[-1])
