> 一句话：**React 的核心思想是 `UI = f(state)`——数据变就把整个组件函数重新执行一遍，配合虚拟 DOM diff + Fiber 架构把"重跑"的开销控制住。**

## 一、JSX 的本质

JSX 不是模板字符串，是 `React.createElement` 的语法糖，编译后就是普通 JS 对象（虚拟 DOM 节点）：

jsx

```
const el = <div className="box">hi</div>

// 编译后（经 jsx-runtime 自动引入）
const el = jsx('div', { className: 'box', children: 'hi' })
// el = { type: 'div', props: { className: 'box', children: 'hi' } }
```

> 与 Vue 对比：Vue 模板是**受限 DSL**（编译期能做静态分析、打 patchFlag）；JSX 是**纯 JS 表达力**（灵活但编译期可优化空间小）。这是两大框架优化路线分叉的根源，见 [[3-2 Vue核心原理]]。

## 二、Fiber：为什么需要可中断渲染

**问题**：React 15 递归 diff 一棵大树是**同步不可中断**的，主线程被占死 >16ms 就掉帧卡顿。

**解法（React 16+）**：把渲染拆成一个个小单元（Fiber 节点），用**链表**代替递归：

```
每个 Fiber: { type, props, child, sibling, return }
              ↓                ↓         ↓
              第一个孩子       下一个兄弟   父节点
```

- 工作循环：每处理完一个 Fiber 检查时间片，用完了就把控制权还给浏览器（处理输入/动画），下一帧继续——**可中断、可恢复**
- **双缓存**：current 树（屏幕上）+ workInProgress 树（内存里新构建的），构建完一次性替换（commit），保证不出现半成品 UI
- 两个阶段：
  1. **Render 阶段**（可中断）：新旧树 diff，算出变更
  2. **Commit 阶段**（不可中断）：一次性把变更打到真实 DOM（替换 DOM、跑生命周期/useEffect 调度）

> React 18 的并发特性（`startTransition`、自动批处理）就建立在 Fiber 的可中断能力上。

## 三、Hooks：原理与规则

### 原理：一条链表

组件第一次渲染时，每个 Hook 按调用顺序**挂到 Fiber 的 hooks 链表上**；更新时按同样顺序从链表取值。

```
useState(0)  → hooks[0]
useEffect(…) → hooks[1]
useState(1)  → hooks[2]
```

**这就是"Hook 不能写在 if/循环里"的原因**：一旦条件导致顺序错位，更新时 state 就会张冠李戴。

### useState 的快照机制（闭包陷阱之源）

jsx

```
function Counter() {
  const [count, setCount] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setCount(count + 1)   // ❌ count 永远是这次渲染的 0 → 永远 1
    }, 1000)
    return () => clearInterval(id)
  }, [])                    // 空依赖：effect 只跑一次，捕获的 count 永远是 0

  return <div>{count}</div>
}
```

- 每次渲染的 `count` 都是**那次渲染的快照**，闭包把快包住了
- 修法一：`setCount(c => c + 1)`（函数式更新，拿最新值）
- 修法二：把 `count` 加进依赖数组（effect 会随 count 重建）
- 本质是闭包问题，见 [[闭包与作用域链]]

### 常用 Hook 速查

| Hook | 干什么 | 关键点 |
| ---- | ---- | ---- |
| useState | 状态 | 更新是替换不是合并（对比 Vue 的响应式赋值） |
| useEffect | 副作用 | 依赖数组控制重跑时机；返回函数做清理 |
| useMemo | 缓存计算值 | 依赖不变不重算 |
| useCallback | 缓存函数引用 | 配合 memo 子组件才有效 |
| useRef | 可变盒子 | 改 `.current` 不触发渲染；常拿 DOM/存定时器 |

## 四、diff 与 key

- 同层比较 + 类型不同直接重建（组件类型变了，整棵子树推倒重来）
- **key 的作用与 Vue 相同**：列表复用的身份证；用 index 当 key 在头部插入/删除时同样会状态错乱，见 [[3-2 Vue核心原理]]
- React 对"同层级同 key"节点做移动，不做双端预处理（Vue3 有最长递增子序列优化）

## 五、其他核心概念速记

- **合成事件**：React 把事件代理到根节点统一分发，抹平浏览器差异；17+ 代理到根容器
- **受控/非受控**：`value + onChange` 受控（React 是唯一数据源）；`defaultValue`/ref 直接读 DOM 非受控
- **状态提升**：两个组件要共享状态 → 提到最近公共父组件；跨层级多了就上 Context / 状态库
- **React 19**：Server Components 服务端组件化（配合 [[Next.js]]）、Actions 表单处理、自动 memo 化

## 六、Vue vs React 心智对比

| 维度 | Vue | React |
| ---- | ---- | ---- |
| 更新粒度 | 组件级精确知道谁依赖了谁 | 组件函数整个重跑 + diff |
| 可变性 | 直接改响应式数据 | 不可变数据（setState 生成新值） |
| 模板 | 受限 DSL，编译期可深度优化 | JSX 纯 JS，灵活 |
| 上手曲线 | 渐进式、约定多、上手快 | 概念少（一切都是 JS）、深水区在闭包/重渲染 |
