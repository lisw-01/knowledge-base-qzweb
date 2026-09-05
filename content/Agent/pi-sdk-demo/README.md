# SDK 示例

通过 `createAgentSession()` 和 `createAgentSessionRuntime()` 以编程方式使用 pi-coding-agent。

运行时示例展示了如何构建一个闭包函数，该函数捕获进程全局的固定输入，并在活跃会话的工作目录变化时重新创建与工作目录绑定的服务和会话。

## 示例列表

| 文件 | 说明 |
|------|------|
| `01-minimal.ts` | 使用所有默认值的最简用法 |
| `02-custom-model.ts` | 选择模型和思考级别 |
| `03-custom-prompt.ts` | 替换或修改系统提示词 |
| `04-skills.ts` | 发现、筛选或替换技能 |
| `05-tools.ts` | 内置工具白名单 |
| `06-extensions.ts` | 日志记录、拦截、结果修改 |
| `07-context-files.ts` | AGENTS.md 上下文文件 |
| `08-prompt-templates.ts` | 基于文件的斜杠命令模板 |
| `09-api-keys-and-oauth.ts` | API 密钥解析、OAuth 配置 |
| `10-settings.ts` | 覆盖压缩、重试、终端设置 |
| `11-sessions.ts` | 内存会话、持久化会话、继续会话、列出会话 |
| `12-full-control.ts` | 替换所有内容，不进行自动发现 |
| `13-session-runtime.ts` | 管理运行时会话替换 |

## 运行方式

```bash
cd packages/coding-agent
npx tsx examples/sdk/01-minimal.ts
```

## 快速参考

```typescript
import { getModel } from "@earendil-works/pi-ai";
import {
  createAgentSession,
  DefaultResourceLoader,
  ModelRuntime,
  SessionManager,
  SettingsManager,
} from "@earendil-works/pi-coding-agent";

const modelRuntime = await ModelRuntime.create();

// 最简用法
const { session } = await createAgentSession({ modelRuntime });

// 自定义模型
const model = getModel("anthropic", "claude-opus-4-5");
const { session } = await createAgentSession({ model, thinkingLevel: "high", modelRuntime });

// 修改提示词
const loader = new DefaultResourceLoader({
  systemPromptOverride: (base) => `${base}\n\nBe concise.`,
});
await loader.reload();
const { session } = await createAgentSession({ resourceLoader: loader, modelRuntime });

// 只读模式
const { session } = await createAgentSession({ tools: ["read", "grep", "find", "ls"], modelRuntime });

// 内存会话
const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  modelRuntime,
});

// 完全控制
const customRuntime = await ModelRuntime.create({
  authPath: "/my/app/auth.json",
  modelsPath: "/my/app/models.json",
});
await customRuntime.setRuntimeApiKey("anthropic", process.env.MY_KEY!);

const resourceLoader = new DefaultResourceLoader({
  systemPromptOverride: () => "You are helpful.",
  extensionFactories: [myExtension],
  skillsOverride: () => ({ skills: [], diagnostics: [] }),
  agentsFilesOverride: () => ({ agentsFiles: [] }),
  promptsOverride: () => ({ prompts: [], diagnostics: [] }),
});
await resourceLoader.reload();

const { session } = await createAgentSession({
  model,
  modelRuntime: customRuntime,
  resourceLoader,
  tools: ["read", "bash", "my_tool"],
  customTools: [myTool],
  sessionManager: SessionManager.inMemory(),
  settingsManager: SettingsManager.inMemory(),
});

// 运行提示
session.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});
await session.prompt("Hello");
```

## 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `modelRuntime` | 使用 `agentDir/auth.json` 和 `models.json` 的运行时 | 规范的模型和认证运行时 |
| `cwd` | `process.cwd()` | 工作目录 |
| `agentDir` | `~/.pi/agent` | 配置目录 |
| `model` | 从设置/第一个可用模型获取 | 要使用的模型 |
| `thinkingLevel` | 从设置/"off" 获取 | off、low、medium、high |
| `tools` | `["read", "bash", "edit", "write"]` 内置工具 | 内置、扩展和自定义工具的白名单 |
| `customTools` | `[]` | 额外的工具定义 |
| `resourceLoader` | DefaultResourceLoader | 用于扩展、技能、提示词、主题和上下文文件的资源加载器 |
| `sessionManager` | `SessionManager.create(cwd)` | 持久化管理 |
| `settingsManager` | `SettingsManager.create(cwd, agentDir)` | 设置覆盖 |

## 事件

```typescript
session.subscribe((event) => {
  switch (event.type) {
    case "message_update":
      if (event.assistantMessageEvent.type === "text_delta") {
        process.stdout.write(event.assistantMessageEvent.delta);
      }
      break;
    case "tool_execution_start":
      console.log(`工具: ${event.toolName}`);
      break;
    case "tool_execution_end":
      console.log(`结果: ${event.result}`);
      break;
    case "agent_settled":
      console.log("完成");
      break;
  }
});
```
