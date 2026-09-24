**Nuxt** 是**基于 Vue.js 的开源全栈 Web 框架**，主打约定式开发、多模式渲染，大幅简化 Vue 的 SSR/SSG 开发，目标是提升开发体验、网站性能与 SEO 友好度Nuxt。

> 类比：Vue 生态的 Nuxt ≈ React 生态的 Next.js
> 
> 当前主流版本：**Nuxt3（Vue3）**，新版 Nuxt4 已发布；**Nuxt2（Vue2）已经停止维护**Nuxt

## ✅ 核心底层

- 前端：**Vue3 + Composition API**
- 构建工具：**Vite**（开发热更新极快）
- 服务引擎：**Nitro**（内置服务端，可写服务端 API、支持边缘部署、Serverless）Nuxt

## 🚀 核心特性

### 1. 约定大于配置（最标志性）

**文件系统路由**：`pages/`目录下的`.vue`文件自动生成路由，不用手写`router/index.js`

plaintext

```
pages/index.vue      →  /
pages/about.vue      →  /about
pages/blog/[id].vue  →  /blog/:id 动态路由
```

- `layouts/`：全局布局
- `composables/`：自动导入组合式函数，无需`import`
- `server/api/`：直接写后端接口，Nuxt 自动注册 API 路由，实现前后端一体全栈开发

### 2. 多种渲染模式（**路由级混合渲染（Hybrid Rendering）**，页面级自由切换）

同一个项目不同页面可以单独配置 SSR / SSG / ISR / SPA。
1. **SSR 服务端渲染（默认）**：服务端生成完整 HTML 返回浏览器，SEO 友好、首屏加载快
2. **SSG 静态生成（预渲染）**：打包时一次性生成全部静态 HTML，适合官网、博客
3. **SPA 客户端渲染**：和普通 Vue 单页应用一致，仅浏览器渲染
4. **ISR 增量静态再生**：静态页面定时更新，兼顾静态速度与动态内容

> ✨亮点：**不同页面可以单独指定渲染模式**，比如首页 SSR、后台管理 SPA

### 3. 自动导入（Auto Imports）

- Vue API（`ref`、`computed`、`useRoute`）、composables、工具函数**不用 import，直接写**
- 内置数据请求：`useFetch` / `useAsyncData`，SSR 友好的数据拉取方案

### 4. 其他能力

- 内置`useHead`管理页面 meta、title，解决 SEO 元信息
- TypeScript 原生支持，类型自动生成
- 模块化生态：200 + 官方 / 社区模块（NuxtUI、PWA、i18n、图片优化等）
- 内置图片、资源、脚本自动优化
- 部署灵活：Node 服务器、静态托管、Cloudflare/Vercel 边缘函数、Serverless 均可

## 📁 基础目录结构（Nuxt3）

plaintext

```
nuxt-app/
├── app.vue          # 入口根组件
├── pages/           # 页面&路由（约定路由）
├── layouts/         # 布局组件
├── composables/      # 自动导入组合函数
├── components/      # 组件，可自动导入
├── server/
│   └── api/         # 服务端接口
├── nuxt.config.ts   # 项目配置
└── public/          # 静态资源
```

## 📌 适用场景

✅ 官网、博客、内容站、电商、需要 SEO 的网站（SSR/SSG 首选）

✅ 中小型全栈项目，不想单独搭建后端

✅ 需要首屏速度优化的 Vue 项目

❌ 纯后台管理系统（内部系统、无 SEO 需求，一般直接用 Vue+Element Plus 即可）

## ⚠️ Nuxt2 vs Nuxt3

- Nuxt2：Vue2 + Options API，Webpack 构建，旧项目维护，**已停止支持**
- Nuxt3：Vue3 + Composition API，Vite+Nitro，性能更强、全栈能力、TS 一流，新项目**优先选 Nuxt3**

## 🧪 快速创建项目

bash

```
npm create nuxt@latest
cd 项目名
npm install
npm run dev
```

启动后访问 `http://localhost:3000`

## 和普通 Vue CLI/Vite Vue 项目对比

- 普通 Vue 项目：默认 SPA，需要自己配置路由、SSR、接口服务、meta 标签，SEO 差
- Nuxt：开箱 SSR/SSG、约定路由、内置服务端、自动导入，**牺牲少量自由度换取极高开发效率和原生 SEO 能力**