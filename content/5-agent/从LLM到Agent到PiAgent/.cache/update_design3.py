import re

p = 'DESIGN.md'
s = open(p, encoding='utf-8').read()

# 配图页码
s = s.replace('`assets/sec_practice.png` | 30 章节扉页底图', '`assets/sec_practice.png` | 39 章节扉页底图')
s = s.replace('`assets/ending_hero.png` | 37 结束页底图', '`assets/ending_hero.png` | 46 结束页底图')
s = s.replace('C 区页码 `NN / 37` 逐页递增', 'C 区页码 `NN / 46` 逐页递增')

new_rows = [
 '| 26 | 26.slide | content | hero | peak | 非对称双栏 38:62 | Table(事件映射) + 类型清单 | 380 | 16% | 强调 18% 爆发 | 映射表 5 行可读；禁止只给结论不给翻译规则 |',
 '| 27 | 27.slide | content | supporting | valley | 左表右卡 60:40 | Table 8 行 + 卡片组 | 340 | 18% | 主色 48% + 强调 10% | 开关表行高一致；右侧三卡不等高 |',
 '| 28 | 28.slide | content | supporting | peak | 左堆栈右双卡 | 五层堆栈（Box 模拟） | 360 | 16% | 主色 46% + 强调 12% | 堆叠宽度递减；禁止等宽五卡 |',
 '| 29 | 29.slide | content | supporting | valley | 左右双栏 58:42 | 双触发表 + 摘要模板 | 380 | 14% | 主色 46% + 强调 12% | 三规则必须带编号；尾条钉底 |',
 '| 30 | 30.slide | content | supporting | valley | 左类型右流水线 | 四阶段纵向卡片 | 360 | 16% | 主色 48% + 强调 12% | 四阶段等高；禁止横向平铺 |',
 '| 31 | 31.slide | content | supporting | peak | 左代码右双卡 | CodeBlock(JSONL 树) | 340 | 16% | 主色 44% + 强调 14% | 代码 ≥ B 区 40%；树分叉可见 |',
 '| 32 | 32.slide | content | hero | peak | 左代码右说明 | CodeBlock(循环骨架) | 330 | 16% | 强调 18% 爆发 | 代码字号 ≥ 10.5；禁止溢出到通栏 |',
 '| 33 | 33.slide | content | supporting | valley | 左表右清单 62:38 | Table(steer/followUp) | 360 | 16% | 主色 48% + 强调 12% | 表格三行；三条消费路径必现 |',
 '| 34 | 34.slide | content | supporting | valley | 左代码右方案 | CodeBlock(VIRTUAL_MODULES) | 340 | 16% | 主色 46% + 强调 12% | 三方案必须有取舍标注 |',
 '| 35 | 35.slide | content | supporting | peak | 左四档右对比 | 四档事件表 | 380 | 14% | 主色 46% + 强调 12% | 四档分组；禁止两套事件平铺并列 |',
 '| 36 | 36.slide | content | supporting | valley | 左哲学右可观测 | 三道防线纵向卡片 | 360 | 16% | 主色 48% + 强调 12% | 三道防线纵向编号；usage 字段完整 |',
 '| 37 | 37.slide | content | supporting | peak | 左协议右架构 | CodeBlock(帧) + 五层架构 | 340 | 16% | 主色 46% + 强调 12% | 五层单向；禁止画成网络拓扑 |',
]

lines = s.split('\n')
out = []
inserted = False
for ln in lines:
    m = re.match(r'^\| (\d{2}) \| (\d{2})\.slide \|', ln)
    if m:
        n = int(m.group(1))
        if n in (26, 27, 28):
            if n == 26 and not inserted:
                out.extend(new_rows)
                inserted = True
            continue
        if 29 <= n <= 37:
            ln = ln.replace('| %02d | %02d.slide |' % (n, n), '| %02d | %02d.slide |' % (n + 9, n + 9), 1)
    out.append(ln)
s = '\n'.join(out)

open(p, 'w', encoding='utf-8').write(s)
print('design updated')
