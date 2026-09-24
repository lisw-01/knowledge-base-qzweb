# CommonJS 规范详解

## 1. 概述

CommonJS 是一种 JavaScript 模块化规范，最初由 Kevin Dangoor 于 2009 年发起，目标是为 JavaScript 制定**服务端模块标准**，使其具备开发大型应用的能力。Node.js 采用了该规范作为其默认模块系统。

---

## 2. 核心概念

### 2.1 模块定义
每个文件就是一个模块，拥有独立的作用域，模块内的变量、函数、类默认**不会污染全局**。

### 2.2 模块标识
- **模块标识**是传递给 `require()` 的参数
- 分为**相对标识**（`./foo`, `../bar`）和**顶级标识**（`lodash`, `express`）
- 相对标识相对当前文件所在目录解析；顶级标识从 `node_modules` 中查找

---

## 3. 核心 API

### 3.1 `require()`

用于导入模块，同步加载并执行目标模块，返回其 `module.exports`。

```javascript
// 加载核心模块
const fs = require('fs');

// 加载文件模块（相对路径）
const utils = require('./utils');

// 加载第三方模块（顶级标识）
const lodash = require('lodash');
```

**加载规则（模块解析算法）**：

1. 若是核心模块（如 `fs`, `path`），直接返回内置模块
2. 若以 `./`、`../`、`/` 开头，按路径查找文件或目录
3. 若是顶级标识，从当前目录的 `node_modules` 向上逐级查找
4. 查找文件时依次尝试：`确切文件名` → `文件名.js` → `文件名.json` → `文件名.node`
5. 若路径指向目录，查找目录下的 `package.json` 的 `main` 字段，或默认 `index.js`

**require 的特性**：

- **同步加载**：`require` 是同步操作，会阻塞执行直到模块加载完成
- **缓存机制**：模块首次加载后会被缓存（`require.cache`），后续 `require` 返回缓存的 `exports`，不会重复执行模块代码
- **循环依赖**：当 A require B、B 又 require A 时，Node 会返回 B 中**已经执行部分的 exports**（可能是不完整的对象）

### 3.2 `module.exports` 与 `exports`

#### `module`

每个模块内部都有一个 `module` 变量，代表当前模块对象，主要属性：

| 属性 | 说明 |
|------|------|
| `id` | 模块标识（通常是绝对路径） |
| `filename` | 模块文件的绝对路径 |
| `loaded` | 模块是否已加载完毕 |
| `parent` | 最先调用该模块的模块 |
| `children` | 该模块依赖的子模块列表 |
| `paths` | 模块搜索路径数组 |
| `exports` | 模块导出的对象 |

#### `module.exports`

真正的导出对象。`require()` 返回的就是 `module.exports`。

```javascript
// 导出单个值（函数、类、原始值等）
module.exports = function add(a, b) {
  return a + b;
};

// 导出对象
module.exports = {
  name: 'foo',
  version: '1.0.0',
};
```

#### `exports`

`exports` 是 `module.exports` 的**引用快捷方式**，初始指向同一个对象。

```javascript
// ✅ 正确 —— 给 exports 添加属性
exports.name = 'foo';
exports.version = '1.0.0';
// 等价于 module.exports.name = 'foo';

// ❌ 错误 —— 重新赋值 exports 会断开与 module.exports 的引用
exports = { name: 'foo' };
// require() 仍返回原来的 module.exports（空对象 {}）
```

**关键区别**：

- `exports` 只能用于追加属性，不能重新赋值
- 需要导出函数、类或全新对象时，必须使用 `module.exports = ...`

---

## 4. 模块加载机制详解

### 4.1 加载流程

```
require(id)
   │
   ├─ 1. 检查缓存 require.cache，命中则返回缓存
   │
   ├─ 2. 解析模块路径（模块定位）
   │     ├─ 核心模块
   │     ├─ 文件模块（.js / .json / .node）
   │     └─ 目录模块（package.json → main / index.js）
   │
   ├─ 3. 创建模块对象 new Module(filename)
   │
   ├─ 4. 编译执行模块代码
   │     ├─ .js  → 读取内容 → 包装函数 → 执行
   │     ├─ .json → JSON.parse 后赋值给 module.exports
   │     └─ .node → dlopen 加载 C++ 编译后的二进制
   │
   └─ 5. 返回 module.exports
```

### 4.2 模块包装函数

Node.js 加载 `.js` 文件时，会将代码包装在一个函数中：

```javascript
(function(exports, require, module, __filename, __dirname) {
  // 模块代码实际运行在这里
  const fs = require('fs');
  module.exports = { /* ... */ };
});
```

这就解释了：

- 为什么模块内可以直接使用 `require`、`module`、`exports`、`__filename`、`__dirname`
- 为什么模块内变量不会泄漏到全局

### 4.3 缓存机制

```javascript
// 首次加载：执行模块代码
const a1 = require('./a'); // 执行 a.js
// 再次加载：直接返回缓存
const a2 = require('./a'); // 不执行，返回同一对象

console.log(a1 === a2); // true

// 清除缓存（不推荐，但有时用于热更新）
delete require.cache[require.resolve('./a')];
```

### 4.4 循环依赖处理

```javascript
// a.js
exports.loaded = false;
const b = require('./b');   // 进入 b.js
exports.loaded = true;
console.log('a.js done');

// b.js
exports.loaded = false;
const a = require('./a');   // 返回 a.js 已执行部分的 exports → { loaded: false }
console.log('a.loaded in b:', a.loaded); // false（拿到的是不完整的快照）
exports.loaded = true;
console.log('b.js done');
```

**规则**：一旦模块被部分加载，后续的 `require` 会返回**当前已构建的 exports 快照**，而非等待模块完全执行完。

---

## 5. 目录作为模块

当 `require()` 指向一个目录时，解析顺序：

1. 查找目录下 `package.json` 的 `main` 字段
2. 若无 `package.json` 或 `main` 无效，查找 `index.js`
3. 还可查找 `index.node`、`index.json`

```javascript
// 目录结构：
// my-lib/
//   package.json  → { "main": "lib/index.js" }
//   lib/
//     index.js

const myLib = require('./my-lib'); // 加载 my-lib/lib/index.js
```

---

## 6. CommonJS vs ES Modules 对比

| 特性 | CommonJS | ES Modules (ESM) |
|------|----------|-------------------|
| 语法 | `require()` / `module.exports` | `import` / `export` |
| 加载方式 | **同步**（运行时加载） | **异步**（编译时静态分析） |
| 输出类型 | **值的拷贝**（基本类型） | **值的绑定（live binding）** |
| 加载时机 | 运行时动态加载 | 编译时静态确定依赖 |
| Tree Shaking | 不支持（动态加载无法静态分析） | 支持 |
| 循环依赖 | 返回已执行部分的不完整快照 | 引用绑定，可获取最新值 |
| 顶层 `this` | 指向 `module.exports` | 指向 `undefined` |
| 适用环境 | Node.js（默认） | 浏览器 + Node.js（需配置） |

**值拷贝 vs 值绑定示例**：

```javascript
// ========== CommonJS —— 值的拷贝 ==========
// counter.js
let count = 0;
module.exports = { count, increment() { count++; } };

// main.js
const { count, increment } = require('./counter');
console.log(count); // 0
increment();
console.log(count); // 0（仍是拷贝值，不会更新）

// ========== ES Modules —— 值的绑定 ==========
// counter.mjs
export let count = 0;
export function increment() { count++; }

// main.mjs
import { count, increment } from './counter.mjs';
console.log(count); // 0
increment();
console.log(count); // 1（绑定到原始变量，实时更新）
```

---

## 7. 动态加载

CommonJS 天然支持运行时动态加载：

```javascript
// 根据条件加载不同模块
const lang = process.env.LANG || 'en';
const messages = require(`./locales/${lang}.json`);

// 条件加载
if (process.env.NODE_ENV === 'test') {
  const mock = require('./mock');
}
```

ES Modules 的 `import()` 动态导入也能实现类似效果，但语法和语义不同。

---

## 8. 常见陷阱与注意事项

### 8.1 `exports` 重新赋值

```javascript
// ❌ 错误
exports = function() {};
// ✅ 正确
module.exports = function() {};
```

### 8.2 模块顶层代码的副作用

模块首次 `require` 时会执行全部顶层代码，注意副作用（如修改全局状态、发起网络请求等）。

### 8.3 JSON 模块

```javascript
const config = require('./config.json'); // 自动 JSON.parse
```

### 8.4 `require.resolve()`

获取模块的绝对路径而不加载模块：

```javascript
const path = require.resolve('./utils'); // '/project/src/utils.js'
```

### 8.5 模块路径变量

```javascript
// __filename：当前模块文件的绝对路径
// __dirname：当前模块文件所在目录的绝对路径
const path = require('path');
const dataPath = path.join(__dirname, 'data', 'db.json');
```

---

## 9. 总结

| 要点 | 说明 |
|------|------|
| 本质 | 服务端模块规范，Node.js 默认采用 |
| 核心 API | `require()`、`module.exports`、`exports` |
| 加载方式 | 同步、运行时、值拷贝 |
| 缓存 | 模块首次加载后缓存，重复 require 不重复执行 |
| 循环依赖 | 返回已执行部分的不完整 exports |
| 与 ESM 共存 | Node.js 支持 `.mjs` 或 `"type": "module"` 使用 ESM，也可通过 `"type": "commonjs"` 或 `.cjs` 显式使用 CJS |
