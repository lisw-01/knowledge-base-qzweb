# 01 - 最简 SDK 用法

使用所有默认值：从 cwd 和 ~/.pi/agent 自动发现技能、扩展、工具、上下文文件。模型从设置或第一个可用模型中选择。

```typescript
import { createAgentSession } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession();

try {
	session.subscribe((event) => {
		if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
			process.stdout.write(event.assistantMessageEvent.delta);
		}
	});

	await session.prompt("What files are in the current directory?");
	session.state.messages.forEach((msg) => {
		console.log(msg);
	});
	console.log();
} finally {
	session.dispose();
}
```
