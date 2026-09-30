# 06 - 扩展配置

扩展可以拦截 Agent 事件并注册自定义工具。它们提供了扩展、自定义工具、命令等功能的统一系统。

默认情况下，扩展文件从以下位置自动发现：
- ~/.pi/agent/extensions/
- <cwd>/.pi/extensions/
- settings.json 中 "extensions" 数组指定的路径

扩展是一个导出默认函数的 TypeScript 文件：
  `export default function (pi: ExtensionAPI) { ... }`
## 扩展文件示例 (./my-logging-extension.ts)

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.on("agent_start", async () => {
		console.log("[Extension] Agent starting");
	});

	pi.on("tool_call", async (event) => {
		console.log(`[Extension] Tool: ${event.toolName}`);
		// 返回 { block: true, reason: "..." } 可以阻止执行
		return undefined;
	});

	pi.on("agent_end", async (event) => {
		console.log(`[Extension] Low-level run ended, ${event.messages.length} messages`);
	});

	// 注册自定义工具
	pi.registerTool({
		name: "my_tool",
		label: "My Tool",
		description: "Does something useful",
		parameters: Type.Object({
			input: Type.String(),
		}),
		execute: async (_toolCallId, params, _signal, _onUpdate, _ctx) => ({
			content: [{ type: "text", text: `Processed: ${params.input}` }],
			details: {},
		}),
	});

	// 注册命令
	pi.registerCommand("mycommand", {
		description: "Do something",
		handler: async (args, ctx) => {
			ctx.ui.notify(`Command executed with: ${args}`);
		},
	});
}
```



```typescript
import {
	createAgentSession,
	DefaultResourceLoader,
	getAgentDir,
	SessionManager,
} from "@earendil-works/pi-coding-agent";

//（1） 扩展会从标准位置自动发现。
//  (2）你也可以通过 settings.json 或 DefaultResourceLoader 选项添加路径。

const resourceLoader = new DefaultResourceLoader({
	cwd: process.cwd(),
	agentDir: getAgentDir(),
	additionalExtensionPaths: ["./my-logging-extension.ts", "./my-safety-extension.ts"],
	extensionFactories: [
		(pi) => {
			pi.on("agent_start", () => {
				console.log("[Inline Extension] Agent starting");
			});
		},
	],
});
await resourceLoader.reload();

const { session } = await createAgentSession({
	resourceLoader,
	sessionManager: SessionManager.inMemory(),
});

try {
	session.subscribe((event) => {
		if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
			process.stdout.write(event.assistantMessageEvent.delta);
		}
	});

	await session.prompt("List files in the current directory.");
	console.log();
} finally {
	session.dispose();
}
```


