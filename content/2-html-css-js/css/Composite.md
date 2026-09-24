# Composite（图层合成 / 复合）

> 浏览器渲染流程：**JS → Style → Layout 布局 (重排 reflow) → Paint 绘制 (重绘 repaint) → Composite 合成**
> 
> Composite 是**最后一步**：把多个绘制好的位图（图层）交给 GPU，直接移动图层、拼合到屏幕上。
> 
> 核心一句话：**合成阶段只移动图层，不会跑布局、不会重绘，开销极低，主线程压力最小，INP 友好**

## ✅ 什么时候只触发 Composite，跳过 Layout + Paint

只有修改下面两类 CSS 属性时，浏览器**直接走合成**，不触发重排、不触发重绘：

1. `transform`（translate / scale / rotate / skew）
2. `opacity`

原理：

浏览器提前把这个元素提升为**独立合成层**，提前光栅化成一张位图。后续修改 transform/opacity，**不需要重新计算布局，不需要重新绘制像素**；GPU 只需要移动这张图的位置，拼到屏幕上。

> 这就是 AG Grid 虚拟滚动性能好的根本原因：虚拟行靠`transform: translateY()`实现上下位移，滚动只触发 Composite。

> ⚠️ 注意：不是写了 transform 就一定自动生成独立合成层；浏览器会做层合并优化，有可能自动合并到父图层。`will-change: transform` 是提示浏览器提前预留独立图层。

## 浏览器渲染链路对比

1. 修改 width /margin/top → Layout → Paint → Composite （最重，reflow）
2. 修改 background /color → Paint → Composite（中等，repaint，不重排）
3. 修改 transform /opacity → **仅 Composite**（最轻，GPU 完成，主线程几乎无消耗）

## 🧩 合成层是什么

你可以理解：**每一个合成层 = GPU 里一张位图**

- 普通 DOM 默认都在同一个主图层
- 满足条件时，浏览器把元素单独拆出来，生成独立图层
- 滚动虚拟行，只是移动图层在视口中的位置，位图本身不变

### 怎么看合成层（Chrome DevTools）

1. F12 → More Tools → Layers
2. 可以看到页面所有图层，hover 会高亮图层范围
3. 滚动表格，观察图层移动，验证是不是只走 Composite