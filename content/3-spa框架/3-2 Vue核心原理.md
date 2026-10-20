> 一句话：**Vue 的核心 = 响应式系统（数据变了自动更新视图）+ 编译优化（编译期把能确定的都在编译期确定）+ 虚拟 DOM diff（运行期最小化 DOM 操作）。**

## 一、响应式原理：Vue2 vs Vue3

### Vue2：`Object.defineProperty`

js

```
Object.defineProperty(obj, 'count', {
  get() {
    // 依赖收集：谁在模板里用了 count，就把谁记下来
    track()
    return value
  },
  set(newVal) {
    value = newVal
    // 派发更新：通知所有用到 count 的地方重新渲染
    trigger()
  }
})
```

**Vue2 的天生缺陷（面试高频）：**

1. **新增/删除属性监听不到**：`defineProperty` 只能劫持"已存在"的属性
   - 补丁：`Vue.set / Vue.delete`（或 `this.$set`）
2. **数组索引和 length 劫持不到**：`arr[0] = 1`、`arr.length = 0` 不触发更新
   - 补丁：重写 `push/pop/shift/unshift/splice/sort/reverse` 七个方法
3. **初始化要递归整棵数据**：data 多大，初始化开销就多大

### Vue3：`Proxy`（对整个对象代理，不是对单个属性）

js

```
const proxy = new Proxy(target, {
  get(target, key, receiver) {
    track(target, key)
    return Reflect.get(target, key, receiver)
  },
  set(target, key, value, receiver) {
    Reflect.set(target, key, value, receiver)
    trigger(target, key)
    return true
  }
})
```

**Proxy 一次性解决 Vue2 全部缺陷：**

| 能力 | Vue2 defineProperty | Vue3 Proxy |
| ---- | ---- | ---- |
| 新增/删除属性 | ❌ 需要 `$set` | ✅ 原生支持 |
| 数组索引/length | ❌ 重写七个方法打补丁 | ✅ 原生支持 |
| Map/Set | ❌ | ✅ |
| 初始化递归 | 启动时全量递归 | **惰性**：访问到嵌套对象才代理（深层数据不碰就零开销） |

> Vue3 响应式 = Proxy（拦截）+ Reflect（修正 this 指向）+ effect 副作用函数（依赖收集的执行单元）。

### 响应式数据为什么必须是函数返回

`data` 写成 `data() { return {...} }` 是为了**每个组件实例拿到独立的数据对象**；写成对象，所有实例会共享同一份引用（Vue2 直接报错，Vue3 组合式 API 的 `data` 选项同样如此）。

## 二、虚拟 DOM 与 diff

虚拟 DOM 基础见 [[1-2 虚拟dom思想]]，这里只记 Vue 特有的 diff 策略：

1. **同层比较**：只对比同层级节点，跨层级移动直接删掉重建（所以 key 相同的元素别换父级）
2. **双端/最长递增子序列**：Vue2 双端比较；Vue3 预处理 + 最长递增子序列，只移动最少的节点
3. **静态节点跳过**：Vue3 编译期给动态节点打 `patchFlag`，diff 时只对比带标记的动态部分

**key 的作用与"为什么不能用 index"：**

- key 是 vnode 的身份证：diff 靠 key 判断"是同一个节点被移动了"还是"新节点"
- 用 `index` 当 key，列表头部插入/删除时，index 全部错位 → 复用错误节点 → 状态串行（输入框内容错乱是经典表现）

## 三、Vue3 编译优化

| 手段 | 干什么 |
| ---- | ---- |
| 静态提升（hoistStatic） | 静态节点提到 render 外，只创建一次 |
| patchFlag | 给动态节点打标记（class 变？文本变？），diff 时按标记精准对比 |
| blockTree | 把带 patchFlag 的动态节点收集成扁平链表，跳过所有静态内容 |
| 事件缓存（cacheHandlers） | 内联事件函数缓存，避免每次渲染生成新函数触发子组件更新 |

> Vue3 性能提升的主要来源是**编译期优化**，而不是单纯 Proxy 更快。

## 四、双向绑定：v-model 是语法糖

```
<!-- 表单上 -->
<input v-model="msg">
<!-- 等价于 -->
<input :value="msg" @input="msg = $event.target.value">

<!-- 组件上（Vue3） -->
<Child v-model="msg" />
<!-- 等价于 -->
<Child :modelValue="msg" @update:modelValue="msg = $event" />
```

所以"双向绑定" = **单向数据流（props 下行）+ 事件回传（emit 上行）**，本质仍是单向流，子组件永远不该直接改 props。

## 五、选项式 vs 组合式 API

| 维度 | 选项式（Vue2 风格） | 组合式（Vue3 setup） |
| ---- | ---- | ---- |
| 组织方式 | 按选项分（data/methods/computed） | **按功能分**（一个功能的状态+逻辑+副作用写一起） |
| 逻辑复用 | mixin（来源不明、命名冲突） | **组合函数**（`useXxx`，来源清晰、类型友好） |
| this | 有（类型推导差） | 无（全程闭包，TS 友好） |
| 适用 | 小组件、快速上手 | 中大型项目、逻辑复用多的场景 |

## 六、常见面试追问速答

- **Vue3 为什么用 Proxy 不用 defineProperty？** 支持增删属性/数组索引/Map/Set + 惰性深度代理 + 不需要 `$set` 补丁
- **响应式原理一句话？** 读取时收集依赖（track），修改时派发更新（trigger），effect 重新执行触发组件重渲染
- **nextTick 是干嘛的？** DOM 更新是异步的（批量、微任务队列）；nextTick 把回调排在本次 DOM 更新之后，用来拿更新后的 DOM
- **computed 和 watch 区别？** computed 有缓存、依赖不变不重算、必须同步返回值；watch 专注"变了以后做副作用"（请求、操作 DOM）
