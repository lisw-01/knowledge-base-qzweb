import io

def fix(path, pairs):
    s = open(path, encoding='utf-8').read()
    for a, b in pairs:
        s = s.replace(a, b)
    open(path, 'w', encoding='utf-8').write(s)

base = 'slides'

fix(f'{base}/26.slide', [('contextWindow · comapt', 'contextWindow · compat')])
fix(f'{base}/25.slide', [('接下来三页，逐个拆开看', '接下来十二页，逐个拆开看')])

titles = {
    '30': ('工具系统:三种视角,四段流水', '工具系统：三种视角，四段流水'),
    '31': ('会话系统：追加日志,树形分叉', '会话系统：追加日志，树形分叉'),
    '32': ('Agent 循环:418 行,两层 while', 'Agent 循环：418 行，两层 while'),
    '34': ('扩展系统:一个函数,一张虚拟模块表', '扩展系统：一个函数，一张虚拟模块表'),
    '35': ('事件系统:两套事件,四档粒度', '事件系统：两套事件，四档粒度'),
    '36': ('安全外置:三道防线,一本账', '安全外置：三道防线，一本账'),
    '37': ('远程会话栈:同一套 Agent,换个壳', '远程会话栈：同一套 Agent，换个壳'),
}
for k, (a, b) in titles.items():
    fix(f'{base}/{k}.slide', [(a, b)])

print('ok')
