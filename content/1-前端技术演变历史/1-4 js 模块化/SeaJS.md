> **SeaJS ≠ CMD，SeaJS 是 CMD 规范的实现库**（阿里/淘宝 玉伯团队出品），与 [[RequireJS]]（AMD）同期竞争，是国内前端模块化时代的主力方案之一。

- 它是一个 JS 模块加载器，实现了 CMD（Common Module Definition）规范
- 语法上刻意贴近 CommonJS（`require` / `exports` / `module`），Node 开发者几乎零成本上手
- 现在已被 webpack 打包 + ES Module 全面取代，只剩历史价值（老项目维护、面试对比题）

## 一、用法

html

```
<script src="sea.js"></script>
<script>
  seajs.use('./main')
</script>
```

js

```
// main.js —— 一个模块就是一个文件
define(function(require, exports, module) {
  // 就近依赖：用到才写 require
  var utils = require('./utils')

  exports.log = function() {
    utils.log('hello seajs')
  }
})
```

- `define` 定义模块，工厂函数自带三个参数（和 CJS 一模一样）
- `seajs.use` 相当于入口加载器（AMD 里是 `require([...])`）

## 二、AMD vs CMD 到底差在哪

两者**都是异步加载**（这是和 CommonJS 最大的区别），差异在**依赖的声明方式和执行时机**：

| 维度 | AMD（RequireJS） | CMD（SeaJS） |
| ---- | ---- | ---- |
| 依赖声明 | **提前声明**：`define(['jquery'], fn)` 依赖数组写死在头部 | **就近声明**：函数体内哪里用到哪里 `require` |
| 加载时机 | 都是一开始就把用到的模块**全部异步加载** | 同样依赖加载，但解析依赖靠扫描 `require` 字符串 |
| 执行时机 | **依赖前置、提前执行**：加载完立即执行依赖模块 | **依赖就近、延迟执行**：进入 `require` 那一刻才执行对应模块 |
| 写法体验 | 更像"配置" | 更像 CommonJS，书写自然 |

> 面试常问的"AMD 提前执行、CMD 延迟执行"指的就是上面第三行：**模块工厂函数什么时候跑**，而不是文件什么时候下载（文件下载两者都是一开始就并行去拉）。

## 三、为什么后来都消失了

1. **语法是"库语法"不是"语言语法"**：`define` / `seajs.use` 都得先引入加载器库才能用
2. **运行时加载 → 构建时打包**：webpack 出现后，浏览器端模块在**打包阶段**就分析好依赖、合并文件，运行时根本不需要加载器
3. **ES Module 成为语言原生标准**（见 [[ES Modules规范]]）：`import/export` 浏览器和 Node 双端原生支持，加载器的历史使命结束

## 四、历史坐标

```
CommonJS(Node, 2009) ──┐
AMD / RequireJS(2011) ├─→ 浏览器端"运行时加载"时代 ─→ webpack + ESM(2015+) 全面替代
CMD / SeaJS(2011~2013) ┘
```

- CMD 只在**国内**流行（阿里系），国际社区基本是 AMD 的天下，这也加速了它生态的边缘化
- 规范层面的对比总表见 [[模块化规范]]
