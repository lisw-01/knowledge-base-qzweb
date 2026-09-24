## Code Splitting 代码分割

> 一句话：**不把所有代码打包成一个 bundle，拆成多个 js 文件，按需加载**，减少首屏加载体积。

### 三种常见分割方式

1. **入口分割（多 entry）**
    
    配置多个入口，每个入口打包单独 bundle。适合多页应用 MPA。

js

```
// webpack
entry: {
  index: './src/index.js',
  admin: './src/admin.js'
}
```

2. **动态导入分割（按需懒加载，最常用）**
    
    `import()` 返回 Promise，触发自动分割。路由懒加载就是这个。

js

```
// 访问路由时才加载这个组件
const Home = () => import('./Home.vue')
```

3. **公共分包（vendor 分割）**
    
    把第三方依赖（vue/react、axios）单独拆出来。
    
    业务代码频繁改动，但第三方库改动少，可以利用浏览器缓存。

- Webpack：`splitChunks`
- Vite：build.rollupOptions 手动配置，内置也自动分包

### 价值

首屏只加载当前页面必要代码，**减小首屏 bundle 大小，提升首屏速度**。

> 区分：Code Splitting 是**拆包**；Tree-Shaking 是**删无用代码**，两者配合减小包体积。