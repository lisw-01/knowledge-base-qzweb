# 服务端 .mjs / .js / .ts 区别

---

## 1. 核心本质

| 扩展名 | 本质 |
|--------|------|
| `.mjs` | **强制 ESM 的 JavaScript 文件**。无论 `package.json` 的 `type` 如何设定，该文件始终被视为 ES Module。 |
| `.js`  | **模块类型取决于上下文的 JavaScript 文件**。若 `package.json` 设置了 `"type": "module"` 则为 ESM；否则（默认或 `"type": "commonjs"`）为 CommonJS。是最模糊、最"依赖约定"的扩展名。 |
| `.ts`  | **TypeScript 源文件**。无法被 Node.js 直接运行，必须经过编译（`tsc` / `tsup` / `esbuild` 等）转译为 `.js` / `.mjs` / `.cjs`。编译后的模块格式由 `tsconfig.json` 的 `module` / `moduleResolution` 决定。 |

一句话总结：
- `.mjs` = 文件级强制 ESM
- `.js`  = 语义随 `package.json` 漂移
- `.ts`  = 编译前态，模块格式由编译配置决定

---

## 2. 核心维度对比表

| 维度 | `.mjs` | `.js` | `.ts` |
|------|--------|-------|-------|
| **模块系统** | 强制 ESM | 取决于 `package.json` `"type"` 字段 | 取决于 `tsconfig.json` `module` 编译输出 |
| **导入语法** | `import` / `export` | CJS: `require()` / `module.exports`；ESM: `import` / `export` | `import` / `export`（顶层 `require` 需声明 `import req = require()` 或在函数内使用） |
| **Node 直接运行** | ✅ 支持（Node 12+） | ✅ 支持 | ❌ 需编译（或通过 `tsx` / `ts-node` 等运行时转译） |
| **顶层 `this`** | `undefined` | CJS: `module.exports`；ESM: `undefined` | 编译后同 `.js` 行为 |
| **文件路径解析** | ESM: 必须写完整扩展名（`import x from './foo.mjs'`） | CJS: 可省略扩展名；ESM: 需写完整扩展名 | 取决于 `moduleResolution` 策略（`node` / `nodenext` 等） |
| **Tree-shaking** | ✅ 静态结构，打包器可分析 | CJS: ❌ 动态结构；ESM: ✅ | ✅ 源码静态结构，编译后取决于输出格式 |
| **类型系统** | ❌ 无 | ❌ 无 | ✅ 静态类型 + 编译时检查 |
| **`__dirname` / `__filename`** | ❌ 不可用，需用 `import.meta.url` + `fileURLToPath()` | CJS: ✅ 可用；ESM: ❌ | 编译后同目标格式行为；源码中可用（编译器注入 shim） |
| **`require()`** | ❌ 不可用（除非动态 `createRequire`） | CJS: ✅；ESM: ❌ | 可通过 `import = require()` 或函数体内调用，编译后取决于输出格式 |
| **`package.json` 影响** | 忽略 `type` 字段，始终 ESM | **受 `type` 字段控制** | 不直接影响；`tsconfig` `resolvePackageJsonExports` 等可影响解析 |
| **对应双扩展名** | `.cjs`（强制 CJS 的 JS） | — | `.mts` → 编译为 `.mjs`；`.cts` → 编译为 `.cjs` |

---

## 3. 详细差异说明

### 3.1 模块系统确定机制

**`.mjs`** — 硬性绑定 ESM，无协商空间：
```js
// file.mjs — 以下语法是唯一合法方式
export const a = 1;
import b from './other.mjs';
```

**`.js`** — 由最近祖先 `package.json` 的 `"type"` 决定：
```jsonc
// package.json
{ "type": "module" }   // 该包下 .js → ESM
{ "type": "commonjs" } // 该包下 .js → CJS（默认值，可省略）
```
若找不到 `package.json`，Node 默认按 CJS 处理 `.js`。

**`.ts`** — 由 `tsconfig.json` 控制编译输出：
```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "module": "ESNext",        // 输出 ESM
    "moduleResolution": "node" // 或 "nodenext" / "bundler"
  }
}
```
TypeScript 本身不关心文件是 ESM 还是 CJS 语义，它只负责类型检查和语法转译，模块格式的"生效"发生在编译产物中。

### 3.2 导入路径与扩展名

| 场景 | `.mjs` (ESM) | `.js` (CJS) | `.ts` (源码) |
|------|-------------|-------------|-------------|
| 导入相对路径 | **必须写扩展名** `./foo.mjs` | 可省略 `./foo` | `moduleResolution: "nodenext"` 时需写扩展名；`"bundler"` 时可省略 |
| 导入 npm 包 | 写包名 `import lodash from 'lodash'` | 写包名 `require('lodash')` | 写包名，由 `moduleResolution` 策略解析 |

> ESM 强制写扩展名是因为它是静态分析的——引擎必须在解析阶段（不执行代码）就能确定依赖图。CJS 的 `require` 是运行时调用，可以动态计算路径。

### 3.3 顶层 await

| 格式 | 顶层 `await` |
|------|-------------|
| `.mjs` (ESM) | ✅ Node 14.8+ 支持 |
| `.js` (ESM) | ✅ （需 `"type": "module"`） |
| `.js` (CJS) | ❌ |
| `.ts` | ✅ 源码可用（编译目标须为 ESM，否则报错） |
**ESM 支持在文件最外层直接使用 `await`（Top-level await），适合脚本、配置加载场景**：

javascript

```
// .mjs / type:module 合法
const config = await import('./config.js')
```

**CommonJS 不支持，必须包裹在异步函数中**：

javascript

```
// .js 默认 CJS 必须这样写
(async () => {
  const config = require('./config.js')
})()
```
### 3.4 内置全局变量

CommonJS 有 5 个内置全局变量：`require`、`module`、`exports`、`__dirname`、`__filename`

ESM 中全部不存在，替代方案：

```js
// .mjs / .js (ESM)
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

// 等价于 __filename
const __filename = fileURLToPath(import.meta.url);

//等价于 __dirname
const __dirname = dirname(__filename);
```

TypeScript 源码中若目标为 ESM，同样需要上述写法。若目标为 CJS，编译产物会自动包含 `__dirname`。

### 3.5 JSON 文件加载

| 格式 | 加载 JSON |
|------|----------|
| CJS (`.js`) | `const data = require('./data.json')` ✅ |
| ESM (`.mjs`) | `import data from './data.json' with { type: 'json' }` ✅（Node 18.1+，需 `--experimental-json-modules` 已稳定） |
| ESM (旧写法) | `import { createRequire } from 'node:module'; const req = createRequire(import.meta.url); const data = req('./data.json')` |
| `.ts` | 源码用 `import`，需 `tsconfig` 设置 `resolveJsonModule: true` |

### 3.6 Node.js 版本要求

| 格式 | 最低 Node 版本 |
|------|---------------|
| `.js` (CJS) | Node 0.x 起 |
| `.mjs` / `.js` (ESM) | Node 12+ 稳定（12.11.1 `--experimental-modules` 移除，14 起默认可用） |
| `.ts` | 依赖运行方案：`tsx` / `ts-node` 须 Node 12+；纯编译无版本限制 |

---

## 4. 模块互操作

### 4.1 ESM 导入 CJS

Node.js 原生支持 ESM `import` 导入 CJS 模块，但有限制：

```js
// math.cjs (CJS)
module.exports = { add: (a, b) => a + b };

// app.mjs (ESM)
import math from './math.cjs';     // ✅ 默认导入 = module.exports 整体
math.add(1, 2);

import { add } from './math.cjs';  // ⚠️ 具名导入：Node 会尝试做 "合成具名导出"
                                   // 对于简单赋值可用，但对动态导出可能失败
```

**关键规则：**
- ESM 导入 CJS 时，`default` 绑定指向 `module.exports`
- 具名导入是 Node 对 `module.exports` 属性的**合成**（synthetic），不保证实时绑定
- CJS 的 `require` 无法直接加载 ESM（见下节）

### 4.2 CJS 导入 ESM

CJS 的 `require()` **不能**加载 ESM 模块——因为 ESM 是异步加载且支持顶层 `await`。

唯一方式是使用动态 `import()`：

```js
// legacy.cjs (CJS)
async function main() {
  const { default: esmMod } = await import('./esm-module.mjs');
  esmMod.doSomething();
}
main();
```

### 4.3 TypeScript 的桥梁角色

TypeScript 在互操作中扮演"编译期类型桥"：

```ts
// lib.ts
export const greet = (name: string): string => `Hello, ${name}`;
```

编译为 CJS 产物：
```js
// lib.js
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.greet = void 0;
const greet = (name) => `Hello, ${name}`;
exports.greet = greet;
```

编译为 ESM 产物：
```js
// lib.mjs
export const greet = (name) => `Hello, ${name}`;
```

**`tsconfig.json` 关键配置：**
```jsonc
{
  "compilerOptions": {
    // 输出模块格式
    "module": "NodeNext",        // 推荐值：根据文件扩展名自动选择 ESM/CJS
                                  // .ts → .js (CJS)  /  .mts → .mjs (ESM)

    // 模块解析策略
    "moduleResolution": "NodeNext", // 与 module 匹配，正确处理 ESM/CJS 互操作

    // ESM 互操作
    "esModuleInterop": true,      // 允许 `import fs from 'fs'` 而非 `import * as fs from 'fs'`
                                  // 编译器为 CJS default 导出注入合成 default

    // 包导出映射
    "resolvePackageJsonExports": true,  // 读取 package.json "exports" 字段
    "resolvePackageJsonImports": true   // 读取 package.json "imports" 字段
  }
}
```

### 4.4 `package.json` `exports` 字段与双模式包

现代 npm 包通过 `exports` 同时提供 ESM 和 CJS 入口：

```jsonc
// package.json
{
  "type": "module",          // 默认 .js → ESM
  "exports": {
    ".": {
      "import": "./dist/index.mjs",   // ESM 消费者走这个
      "require": "./dist/index.cjs",  // CJS 消费者走这个
      "default": "./dist/index.mjs"
    }
  }
}
```

**解析规则：**
- ESM 消费者（`import`）→ 选取 `"import"` 条件
- CJS 消费者（`require`）→ 选取 `"require"` 条件
- 无匹配 → 回退 `"default"`

### 4.5 互操作速查决策树

```
ESM 文件需要导入 CJS 模块？
├─ 是 → 直接 `import pkg from 'pkg'`（default = module.exports）
│       具名导入不保证可靠，用 `const { x } = pkg` 解构更安全
└─ 否

CJS 文件需要导入 ESM 模块？
├─ 是 → 只能用 `await import('pkg')`
│       无法使用 `require()`，因为 ESM 顶层 await 与同步 require 语义冲突
└─ 否

TypeScript 项目要同时输出 ESM + CJS？
├─ 是 → 方案 A：`module: "NodeNext"` + `.mts` / `.cts` 双文件
│       方案 B：打包工具（tsup / unbuild）一次源码输出双格式
│       方案 C：两次 tsc 编译，不同 `outDir` 和 `module` 配置
└─ 否 → 只需单格式输出，按目标设置 `module` 即可
```

---

> **参考**：Node.js 官方文档 — [ECMAScript Modules](https://nodejs.org/api/esm.html)、[Determining module system](https://nodejs.org/api/packages.html#determining-module-system)；TypeScript 官方手册 — [Module Resolution](https://www.typescriptlang.org/docs/handbook/modules/theory.html#module-resolution)、[reference for module](https://www.typescriptlang.org/tsconfig#module)。
