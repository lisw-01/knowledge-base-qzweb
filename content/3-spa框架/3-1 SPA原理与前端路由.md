> 一句话：**SPA = 整个应用只有一个 HTML 页面，所有"页面跳转"都是 JS 局部更新 DOM + 前端自己管理路由，不经过服务器。**

## 一、MPA vs SPA

| 维度 | MPA（多页应用，传统） | SPA（单页应用） |
| ---- | ---- | ---- |
| 页面切换 | 整页请求新 HTML（白屏、闪烁） | JS 拦截，局部更新（无刷新） |
| 路由管理 | **服务端路由**：每个 URL 对应一个 HTML | **前端路由**：URL 只是个状态 |
| 数据获取 | 每个 HTML 附带重新渲染 | Ajax/fetch 按需拉 JSON |
| 首屏 | 快（直接吐 HTML） | 慢（要下 JS → 执行 → 请求数据 → 渲染） |
| SEO | 天然友好 | 差（HTML 是空壳） |
| 服务器压力 | 每次跳转都要渲染页面 | 静态资源 + 接口 |

> SPA 的 SEO / 首屏问题正是元框架（SSR/SSG/流式渲染）出现的原因，见 [[页面渲染方案]]、[[Next.js]]、[[Nuxt]]、[[流式html]]。

## 二、前端路由的两种实现

前端路由核心就一件事：**监听 URL 变化 → 匹配对应组件 → 重新渲染**，且**不能真的向服务器发请求**。

### 1. Hash 模式（`#/home`）

```
https://example.com/#/home
                    ↑ hash 部分
```

- `hash` 变化**不会发请求**，只触发浏览器的 `hashchange` 事件
- 兼容性最好，不需要服务端任何配合

js

```
// 30 行理解 hash 路由
window.addEventListener('hashchange', () => {
  const path = location.hash.slice(1)   // '#/home' → '/home'
  const component = routes[path]        // 路由表匹配
  render(component)                     // 换掉挂载点内容
})
```

### 2. History 模式（`/home`）

- 用 `history.pushState()` 改 URL：**不刷新、不发请求、不留历史记录污染**（`replaceState` 则替换）
- 前进/后退靠 `popstate` 事件（注意：`pushState` 本身不触发 `popstate`，只有浏览器前后退才触发）
- URL 干净好看（没有 `#`），是现代项目默认选择

js

```
// 跳转
history.pushState(null, '', '/home')

// 拦截所有 <a> 点击 → preventDefault → pushState → 手动渲染
window.addEventListener('popstate', () => {
  render(routes[location.pathname])
})
```

### 3. History 模式的致命坑：刷新 404

`/home` 这个 URL 在服务器上**根本不存在**（服务器只有一个 `index.html`），用户一刷新就 404。

解法：服务端把所有找不到的路径**兜底返回 `index.html`**，让前端路由自己接管。

nginx

```
location / {
  try_files $uri $uri/ /index.html;   # 关键：找不到就回 index.html
}
```

> 完整 Nginx 前端部署配置见 [[Nginx部署与配置]]。这是 SPA 部署最常踩的坑，没有之一。

| 对比 | Hash | History |
| ---- | ---- | ---- |
| URL 样子 | `/#/home`（丑） | `/home`（干净） |
| 服务器配合 | 不需要 | **必须**配置 fallback |
| 兼容性 | 全兼容 | IE10+（已无所谓） |
| 原理 | `hashchange` | `pushState` + `popstate` |

## 三、SPA 的加载性能三板斧

1. **代码分割**：路由级懒加载，首屏只下首屏代码 → 见 [[Code Splitting]]
2. **静态资源长缓存**：文件名带 hash，一年强缓存 → 见 [[打包后的web内容]]、[[Nginx部署与配置]]
3. **首屏优化**：SSR/SSG/流式 → 见 [[页面渲染方案]]

## 四、一句话串联

```
URL 变 ──→ 前端路由匹配组件 ──→ 虚拟DOM diff 局部更新 ──→ 数据变化驱动视图
```

- "局部更新"靠虚拟 DOM 思想 → 见 [[1-2 虚拟dom思想]]
- "数据驱动"靠响应式系统 → Vue 用依赖收集（Proxy），React 用重跑函数 + diff，见 [[3-2 Vue核心原理]]、[[3-3 React核心原理]]
