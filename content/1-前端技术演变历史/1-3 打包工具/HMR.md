## Hot Module Replacement 热模块替换

> 一句话：**开发环境，修改文件，不用刷新整个页面，只替换变更模块，保留页面状态**。

### 和普通刷新的区别

- 普通 live-reload：改文件 → 页面整页刷新，表单、滚动状态全部丢失
- HMR：只更新改动模块，页面状态保留

### 原理简述（Webpack）

1. 打包器监听文件变更
2. 文件改动，重新编译该模块，生成更新补丁
3. Webpack-dev-server 通过 websocket 通知前端
4. 前端接收补丁，执行模块替换，执行模块的 accept 回调更新页面

### Vite 的 HMR（和 webpack 不一样）

Vite 开发环境**不打包**，基于浏览器原生 ESM：

- 文件修改 → 直接请求新模块
- 细粒度 HMR，不需要重建 bundle，HMR 速度远快于 webpack

### 限制

HMR**只用于开发环境**，生产打包不存在 HMR。

需要框架做 HMR 兼容：Vue、React 都有专门的 HMR runtime 处理组件更新。