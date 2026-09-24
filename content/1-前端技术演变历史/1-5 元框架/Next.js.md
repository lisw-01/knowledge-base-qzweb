# Next.js

> Vercel 出品，**React 的元框架**，当前主流是 **App Router（基于 RSC，React Server Components）**；老方案 Pages Router 仍可维护新项目不再推荐。
> 
> 前面聊的 SSR / SSG / ISR / 流式 HTML，就是 Next 最核心的渲染能力。

## ✨ 两大路由体系

### 1. App Router（`app/`，推荐，Next13.4 + 稳定）

**默认组件 = 服务端组件 RSC**，不需要任何配置，直接在组件内 `await fetch` 请求数据，**不会打包 JS 到前端**。

- 约定式文件路由：文件夹代表路由段；**`page.tsx` 才对外暴露页面**，其他组件、工具文件可以和路由放一起（同置 Colocation），不会变成路由Next.js
- 内置嵌套布局 `layout.tsx`，多层嵌套共享布局，不用 `_app`
- 特殊约定文件（路由段级别）
    
    - `layout.tsx`：布局，包裹子路由，根 layout 必须写`<html><body>`
    - `page.tsx`：页面主体，路由出口
    - `loading.tsx`：Suspense fallback，**自动开启流式 HTML**
    - `error.tsx`：错误边界
    - `not-found.tsx`：404
    - `route.ts`：接口（Route Handlers，返回 JSON）
    
- 动态路由：`app/blog/[id]/page.tsx` 捕获参数
- 路由组 `(admin)`：文件夹带括号，仅用于分类，**不体现在 URL**
- 元数据：`export const metadata` / `generateMetadata`，直接写 SEO 标题、描述

> 客户端组件：需要 hooks（`useState/useEffect`、浏览器 API、事件），文件顶部写 `'use client'`

tsx

```
// app/page.tsx 默认RSC，服务端执行
async function getPosts() {
  const res = await fetch('https://xxx/api/posts', { next: { revalidate: 60 } })
  return res.json()
}

export default async function Home() {
  const posts = await getPosts();
  return <div>{posts.map(p=><div>{p.title}</div>)}</div>
}
```

tsx

```
// 客户端组件，必须写 use client
'use client'
import { useState } from 'react'
export default function Counter() {
  const [n, setN] = useState(0)
  return <button onClick={()=>setN(n+1)}>{n}</button>
}
```

#### Server Actions

`'use server'`，写在服务端的函数，可以直接交给客户端组件 form/click 调用，**不用单独写接口**，适合表单提交。

tsx

```
// actions.ts
'use server'
export async function submitForm(formData: FormData) {
  // 在服务端执行，可以操作DB
}
```

### 2. Pages Router（`pages/`，旧方案）

- `pages/index.tsx` → `/`；`pages/about.tsx` → `/about`
- 数据获取 API：`getStaticProps`(SSG/ISR) / `getServerSideProps`(SSR) / `getStaticPaths`动态预渲染
- 没有 RSC，全部是客户端组件；不支持原生流式 HTML

> 老项目大量在用，新项目尽量 App Router




## 🧩 渲染模式（和前面概念对应）

App Router 自动判断渲染模式，**不需要 Pages 那种单独 API**：

1. **静态渲染 SSG（默认）**：无动态请求参数、无 cookies/headers，构建时生成 HTML
2. **动态渲染 SSR**：用到 `cookies()` / `headers()` / `searchParams`，每次请求在服务端渲染
3. **ISR 增量静态再生**：`fetch(url, {next:{revalidate:60}})`，缓存 + 后台刷新
4. **流式 Streaming HTML**：`loading.tsx` / `<Suspense>`，分块输出 HTML

> 底层支持 Node Runtime / Edge Runtime（Vercel 边缘函数）

## 📦 内置优化能力

1. `next/image`：图片自动压缩、格式转换、懒加载
2. `next/font`：字体优化，避免 FOIT，不发额外网络请求
3. `next/link`：前端预加载 prefetch，页面跳转无白屏
4. 缓存体系：fetch 请求自动缓存，revalidate 控制失效策略
5. Turbopack：新一代打包器，dev 启动速度大幅提升

## 🚀 新建项目

bash

```
npx create-next-app@latest my-next-app
# 可选TS、ESLint、Tailwind、App Router
cd my-next-app
npm run dev
```

## ✅ 优点

1. React 生态完整，招聘多，SaaS、后台、官网、AI 产品首选
2. RSC 大幅减少前端 JS 体积，首屏性能强，天然支持流式 SSR
3. Vercel 一键部署；也可部署到普通 Node 服务器、Edge、Docker
4. 缓存、元数据、图片字体优化开箱即用
5. 同项目页面 + 接口一体开发（Route Handler / Server Action）

## ❌ 缺点

1. App Router 心智负担重：RSC / 客户端组件边界、缓存规则容易踩坑
2. 第三方库需要兼容 RSC；很多旧 React 库只能在`use client`里使用
3. 本地调试缓存机制比较绕