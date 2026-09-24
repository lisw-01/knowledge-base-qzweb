## 1. Tree-Shaking 树摇

> 一句话：**打包时删除代码里没被使用的死代码（unused code）**，像摇树一样把枯叶子摇掉。

### 前提条件（很重要）

1. 必须是 **ES Module（import/export）**
    
    CommonJS `require` 做不到！因为 `require` 是运行时动态引入，打包阶段无法静态分析判断用没用。
2. 打包工具要能**静态分析**导入导出，不能动态导入
    
    ❌ 动态写法无法 tree-shake：
    
    js
    
    ```
    const name = 'utils'
    import(`./${name}.js`) // 动态import，静态分析失效
    ```
    
3. 不能有副作用（sideEffects）
    
    - 副作用：引入模块就会执行代码，哪怕不导出任何东西（如直接修改 window、css 文件）
    - package.json `sideEffects` 标记：告诉打包工具哪些文件有副作用，不要删
    
    json
    
    ```
    {
      "sideEffects": ["*.css"] // css有副作用，不能tree-shaking删掉
    }
    ```
    

### 工具支持情况

- Rollup：最早实现 Tree-Shaking，效果最好（库打包首选）
- Webpack：webpack2 开始支持，webpack4/5 完善
- esbuild：支持 tree-shaking
- Vite 生产构建底层是 Rollup，继承该能力




## 2.tree-shaking **只在生产打包生效**，开发环境不会删代码。


**默认情况下：Tree‑Shaking 只在生产打包开启，开发环境不做死代码删除。**

Tree‑Shaking 是**为了减小线上包体积**，而不是给开发环境用的。

开发环境目标：**源码可调试、完整，不丢失代码、保留 sourcemap**；

如果开发环境把代码摇掉，断点、变量会莫名其妙消失，调试灾难。

下面拆开讲原理 + 例外情况。

## 1. Webpack

- `mode: production`：
    
    - 自动开启 `TerserPlugin`（压缩），**压缩器才真正执行删除死代码**
    - Webpack 本身只是标记可消除模块，**真正删代码是 Terser 做的**
    
- `mode: development`：
    
    - 不开启代码压缩，即便能静态分析出未使用导出，**也不会删掉**，保留完整代码方便调试
    

> 重点误区：
> 
> Webpack 的 Tree‑shaking 分为两步：
> 
> 1. 编译阶段：标记 unused harmony export（只是标记）
> 2. 压缩阶段（Terser）：把标记的代码真正删掉
>     
>     → **如果没有压缩，就算 production，tree-shaking 也不会生效**

## 2. Rollup

Rollup 本身就具备移除死代码能力，**不需要压缩器也能摇掉**

- 开发构建：默认**不做 tree-shaking**（保留全部代码，方便断点调试）
- 生产构建：开启 tree-shaking，移除未使用代码

## 3. Vite

Vite 开发环境：用原生 ESM，**完全不打包，不存在 tree-shaking**

Vite 生产构建：底层调用 Rollup，Rollup 执行 tree-shaking。

## 4. esbuild

esbuild 的 tree-shaking 由`minify`压缩开关控制：

- `minify: true` 才会移除死代码
- `minify: false`，哪怕是生产配置，也保留全部代码

