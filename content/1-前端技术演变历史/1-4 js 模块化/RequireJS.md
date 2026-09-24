

> **RequireJS ≠ AMD，RequireJS 是 AMD 规范的实现库**

- 它是一个 JS 模块加载器，实现了 AMD 规范，早期前端最流行的模块方案
- 用法：

html

```
<script data-main="main" src="require.js"></script>
```

`data-main` 指定入口文件 main.js，入口内部用 `define` 定义模块，`require()` 加载模块

js

```
// main.js
require(['./utils'], function(utils) {
  utils.log()
})
```

- 局限：需要引入额外库；语法不是 JS 原生；现在基本被 ES Module 替代