# ES Modules 规范详解

## 1. 概述

ES Modules（简称 ESM）是 ECMAScript 2015（ES6）引入的**官方 JavaScript 模块化标准**，由 TC39 制定，旨在统一浏览器和服务端的模块系统。与 CommonJS 的运行时同步加载不同，ESM 采用**编译时静态分析 + 异步加载**，天然支持 Tree Shaking，是现代前端工程的默认模块方案。

---

## 2. 核心概念

### 2.1 模块定义

- 每个 ESM 文件就是一个模块，拥有独立的**模块作用域**
- 模块内声明的变量、函数、类默认**不会污染全局**
- 模块顶层 `this` 为 `undefined`（严格模式）

### 2.2 严格模式

ESM 模块默认启用严格模式（`"use strict"`），无需手动声明：

- 禁止未声明变量
- 禁止 `with` 语句
- 禁止重复参数名
- `this` 为 `undefined`（非全局对象）

### 2.3 静态结构

`import` / `export` 必须出现在**模块顶层**，不能放在 `if`、`for` 等块级作用域中：

```javascript
// ✅ 正确
import { foo } from './mod';

// ❌ 错误 —— 语法限制
if (condition) {
  import { foo } from './mod'; // SyntaxError
}
```

动态场景请使用 `import()` 函数（见第 7 节）。

---

## 3. 导出（export）

### 3.1 命名导出

一个模块可以导出多个命名成员：

```javascript
// 逐个导出
export const name = 'foo';
export function sayHello() { console.log('hello'); }
export class MyClass {}

// 统一导出（推荐，一目了然）
const name = 'foo';
function sayHello() { console.log('hello'); }
class MyClass {}

export { name, sayHello, MyClass };
```

### 3.2 重命名导出

```javascript
export { name as moduleName };
export { sayHello as greet };
```

### 3.3 默认导出

每个模块**最多一个**默认导出：

```javascript
// 直接导出值
export default function add(a, b) { return a + b; }
export default class Person {}
export default 42;
export default { name: 'foo' };

// 先定义再导出
function add(a, b) { return a + b; }
export default add;

// 重命名导出为默认导出
export { add as default };
```

**注意**：默认导出本质上是一个名为 `default` 的命名导出：

```javascript
// 以下两种写法等价
export default function() {}
export { function as default };
```

### 3.4 聚合导出（Re-export）

从其他模块导出，用于构建**模块入口 / barrel 文件**：

```javascript
// 直接透传
export { foo, bar } from './modA';
export * from './modB';

// 重命名透传
export { foo as myFoo } from './modA';

// 将另一个模块的默认导出重命名后透传
export { default as Util } from './utils';

// 将命名导出作为默认导出透传
export { foo as default } from './modA';
```

### 3.5 导出注意事项

- `export` 导出的是**绑定（live binding）**，而非值的拷贝
- 导出的变量在模块内部被修改后，外部引用也会更新
- `export` 语句不能嵌套在块级作用域中

---

## 4. 导入（import）

### 4.1 命名导入

```javascript
import { name, sayHello } from './mod';

// 重命名
import { name as moduleName } from './mod';
```

### 4.2 默认导入

```javascript
import add from './mod';       // add 对应 export default
import add, { name } from './mod'; // 同时导入默认 + 命名
```

### 4.3 命名空间导入

将模块所有命名导出收集为一个对象：

```javascript
import * as mod from './mod';

mod.name;       // 访问命名导出
mod.sayHello(); // 调用命名导出函数
mod.default;    // 访问默认导出
```

### 4.4 仅执行副作用

不导入任何绑定，只执行模块代码：

```javascript
import './polyfill';
import './side-effect';
```

### 4.5 空导入（TypeScript 类型专用）

```typescript
import type { UserInfo } from './types';
```

---

## 5. 静态 import 的特性

### 5.1 提升作用

`import` 语句会被**提升到模块顶部**执行，与书写位置无关：

```javascript
console.log(name); // 可以正常访问
import { name } from './mod'; // 实际最先执行
```

### 5.2 只读绑定

导入的绑定是**只读**的，不能重新赋值：

```javascript
import { name } from './mod';
name = 'bar'; // TypeError: Assignment to constant variable
```

但可以修改对象类型的属性（不推荐）：

```javascript
import { obj } from './mod';
obj.key = 'new'; // 可以修改属性，但不推荐
```

### 5.3 Live Binding（实时绑定）

ESM 导出的是**值的绑定**，而非值的拷贝。模块内部修改变量后，外部能感知到：

```javascript
// counter.mjs
export let count = 0;
export function increment() { count++; }

// main.mjs
import { count, increment } from './counter.mjs';
console.log(count); // 0
increment();
console.log(count); // 1（实时更新，与 CommonJS 的值拷贝不同）
```

### 5.4 Singleton 语义

同一模块无论被多少个模块 `import`，只会**加载和执行一次**，所有导入共享同一份绑定。

---

## 6. 动态导入 import()

`import()` 是一个**异步函数**，返回 Promise，用于运行时按需加载模块：

### 6.1 基本用法

```javascript
const module = await import('./mod');
module.sayHello();

// 也可以用 .then
import('./mod').then(module => {
  module.sayHello();
});
```

### 6.2 配合解构

```javascript
const { name, sayHello } = await import('./mod');
```

### 6.3 默认导出的获取

```javascript
// 方式一
const mod = await import('./mod');
mod.default;

// 方式二
const { default: add } = await import('./mod');
```

### 6.4 典型场景

```javascript
// 条件加载
if (lang === 'en') {
  const messages = await import('./locales/en.js');
}

// 路由懒加载（Vue Router）
const routes = [
  { path: '/about', component: () => import('./views/About.vue') }
];

// 代码分割（React）
const LazyComp = React.lazy(() => import('./LazyComp'));
```

### 6.5 import() vs 静态 import

| 特性 | 静态 `import` | 动态 `import()` |
|------|---------------|------------------|
| 语法 | 声明式 | 函数调用式 |
| 加载时机 | 编译时确定，模块初始化阶段加载 | 运行时按需加载 |
| 返回值 | 直接绑定 | Promise |
| 位置限制 | 必须在顶层 | 任意位置 |
| Tree Shaking | 支持 | 不参与静态分析 |

---

## 7. Node.js 中使用 ESM

### 7.1 启用方式

**方式一**：文件使用 `.mjs` 扩展名

```bash
node app.mjs
```

**方式二**：`package.json` 设置 `"type": "module"`

```json
{
  "type": "module"
}
```

此时 `.js` 文件被视为 ESM；如需使用 CommonJS，改用 `.cjs` 扩展名。

**方式三**：`--input-type` 标志

```bash
node --input-type=module < app.js
```

### 7.2 Node.js ESM 与浏览器的差异

| 特性 | 浏览器 | Node.js |
|------|--------|---------|
| 路径要求 | 必须包含扩展名或完整 URL | 也推荐写扩展名（`--experimental-specifier-resolution` 已废弃） |
| 裸模块标识 | 需 Import Map | 直接从 `node_modules` 解析 |
| 内置模块 | 不可用 | `import fs from 'fs'` 可用 |
| `file://` URL | 不适用 | 本地文件模块使用 |

### 7.3 Node.js 中的路径解析

Node.js ESM 中 `import` 路径的解析规则：

```javascript
// ✅ 相对路径（推荐带扩展名）
import './utils.js';

// ✅ 绝对路径
import '/project/src/utils.js';

// ✅ URL 形式
import 'file:///project/src/utils.js';

// ✅ 包名（从 node_modules 解析）
import 'lodash';

// ❌ 省略扩展名（不再支持）
import './utils'; // Error!
```

### 7.4 双包问题（Dual Package）

同一包同时提供 CJS 和 ESM 入口时，可能出现**双重实例化**问题：

```json5
// package.json
{
  "main": "./index.cjs",      // CJS 入口
  "module": "./index.mjs",    // ESM 入口（打包工具识别）
  "exports": {
    "import": "./index.mjs",  // ESM 入口（Node 识别）
    "require": "./index.cjs"  // CJS 入口（Node 识别）
  }
}
```

**条件导出（Conditional Exports）**完整写法：

```json5
{
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "default": "./dist/index.cjs"
    },
    "./feature": {
      "import": "./dist/feature.mjs",
      "require": "./dist/feature.cjs"
    }
  }
}
```

### 7.5 互操作

**ESM 中导入 CJS**：

```javascript
// CJS 模块导出 module.exports = { foo: 1 }
// ESM 中导入
import cjsModule from './cjs-module.cjs';
cjsModule.foo; // 1
```

Node 会将 CJS 的 `module.exports` 作为 ESM 的默认导出。命名导出可通过静态分析获取，但不保证可靠。

**CJS 中导入 ESM**：

CJS 中不能使用 `import` 语法，必须用动态 `import()`：

```javascript
// ❌ 不支持
const esm = require('./esm-module.mjs'); // Error!

// ✅ 使用动态 import()
const esm = await import('./esm-module.mjs');
```

---

## 8. 浏览器中使用 ESM

### 8.1 `<script type="module">`

```html
<script type="module">
  import { foo } from './mod.js';
  console.log(foo);
</script>
```

特性：
- 默认** defer** 行为（DOM 解析完成后执行）
- 自带**严格模式**
- 独立模块作用域，不污染全局
- 同一模块只执行一次
- CORS 限制：跨域模块需服务端返回正确的 CORS 头

### 8.2 `<script type="module">` vs `<script>`

| 特性 | `<script>` | `<script type="module">` |
|------|-----------|--------------------------|
| 默认 defer | 否 | 是 |
| 严格模式 | 否（需声明） | 默认启用 |
| 全局污染 | 是 | 否（模块作用域） |
| 多次执行 | 每次都执行 | 只执行一次 |
| CORS | 不受限 | 需 CORS 头 |

### 8.3 nomodule 回退

```html
<script type="module" src="app.mjs"></script>
<script nomodule src="app.bundle.js"></script>
```

支持 ESM 的浏览器只执行 `type="module"`；不支持的浏览器只执行 `nomodule`。

### 8.4 Import Map

浏览器原生不支持裸模块标识（`import 'lodash'`），需要 Import Map 映射：

```html
<script type="importmap">
{
  "imports": {
    "lodash": "https://cdn.jsdelivr.net/npm/lodash@4/es/lodash.js"
  }
}
</script>
<script type="module">
  import _ from 'lodash';
</script>
```

---

## 9. ESM 加载机制详解

### 9.1 加载流程

```
import from './mod.js'
   │
   ├─ 1. 构建阶段（Construction / 解析）
   │     ├─ 下载模块文件
   │     ├─ 递归解析 import 语句，构建依赖图
   │     └─ 静态分析导出/导入绑定关系
   │
   ├─ 2. 实例化阶段（Instantiation）
   │     ├─ 为每个导出创建内存绑定（live binding）
   │     └─ 将导入与导出绑定关联（深度优先，从依赖到入口）
   │
   └─ 3. 运行阶段（Evaluation）
        ├─ 按依赖拓扑顺序执行模块顶层代码
        └─ 完成所有 live binding 的初始化
```

### 9.2 与 CommonJS 加载机制的核心差异

| 阶段 | CommonJS | ESM |
|------|----------|-----|
| 解析 | 运行时 `require()` 时才解析依赖 | 编译时静态解析全部依赖 |
| 实例化 | `module.exports` 是值的拷贝 | 导入是 live binding |
| 执行 | 同步，`require` 处立即执行 | 异步，按依赖拓扑顺序执行 |
| 循环依赖 | 返回不完整的 exports 快照 | live binding 可获取最新值 |

### 9.3 循环依赖处理

```javascript
// a.mjs
import { loaded } from './b.mjs';
export let loaded = false;
loaded = true;
console.log('b.loaded in a:', loaded); // 取决于执行顺序

// b.mjs
import { loaded } from './a.mjs';
export let loaded = false;
loaded = true;
console.log('a.loaded in b:', loaded);
```

ESM 的 live binding 机制意味着循环依赖中，一方修改了变量后，另一方通过绑定可以读到最新值，而非像 CJS 那样拿到不完整快照。但由于执行顺序问题，**仍然应尽量避免循环依赖**。

---

## 10. CommonJS vs ES Modules 完整对比

| 特性 | CommonJS | ES Modules |
|------|----------|------------|
| 语法 | `require()` / `module.exports` | `import` / `export` |
| 加载方式 | 同步 | 异步 |
| 加载时机 | 运行时 | 编译时静态分析 |
| 输出类型 | 值的拷贝 | 值的绑定（live binding） |
| 导入是否只读 | 否（可以修改） | 是（重新赋值报错） |
| Tree Shaking | 不支持 | 支持 |
| 动态加载 | `require()` 天然支持 | `import()` 返回 Promise |
| 顶层 `this` | `module.exports` | `undefined` |
| 严格模式 | 需手动声明 | 默认启用 |
| 循环依赖 | 返回不完整快照 | live binding 可获取最新值 |
| 提升 | 无（require 在调用处执行） | import 提升到模块顶部 |
| 模块路径 | 可省略扩展名 | 需写完整路径/扩展名 |
| Node.js 默认 | 是（`.js` 默认 CJS） | 需 `.mjs` 或 `"type": "module"` |
| 浏览器支持 | 不支持 | 原生支持 |

---

## 11. 常见陷阱与注意事项

### 11.1 导入路径必须完整

```javascript
// ❌ Node.js ESM 中省略扩展名
import './utils';    // Error
import './utils.js'; // ✅
```

### 11.2 不能解构默认导出

```javascript
// mod.js
export default { name: 'foo', age: 18 };

// ❌ 错误写法
import { name, age } from './mod'; // 这是导入命名导出 name 和 age

// ✅ 正确写法
import obj from './mod';
const { name, age } = obj;
```

### 11.3 export default 与命名导出不能混淆

```javascript
// ❌ 错误
export default const foo = 1; // SyntaxError

// ✅ 正确
export default 1;
// 或
const foo = 1;
export default foo;
```

### 11.4 模块中不能使用 CommonJS 变量

ESM 中没有 `__dirname`、`__filename`、`require`、`module`、`exports`：

```javascript
// ❌ ESM 中不可用
console.log(__dirname);  // ReferenceError
console.log(__filename); // ReferenceError

// ✅ 替代方案
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```

### 11.5 import.meta

ESM 提供的元信息对象，包含当前模块的 URL：

```javascript
// 浏览器
console.log(import.meta.url); // 'https://example.com/mod.js'

// Node.js
console.log(import.meta.url); // 'file:///project/src/mod.js'

// 获取 __filename
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
```

### 11.6 Top-level await

ESM 支持 Top-level await（顶层 await），CJS 不支持：

```javascript
// config.mjs
const config = await fetch('/api/config').then(r => r.json());
export default config;
```

注意：Top-level await 会阻塞后续模块的执行，可能影响整体加载性能。

---

## 12. 总结

| 要点 | 说明 |
|------|------|
| 本质 | JavaScript 官方模块标准，ES6 引入 |
| 核心语法 | `export` / `import` / `import()` |
| 加载方式 | 异步、编译时静态分析、值的绑定（live binding） |
| 静态 import | 必须在顶层，会被提升，只读绑定 |
| 动态 import() | 运行时按需加载，返回 Promise |
| 浏览器支持 | `<script type="module">` + Import Map |
| Node.js 支持 | `.mjs` 或 `"type": "module"` |
| 与 CJS 互操作 | ESM 可导入 CJS 默认导出；CJS 需用 `import()` 导入 ESM |
| 推荐场景 | 新项目优先使用 ESM，获得 Tree Shaking 和静态分析优势 |
