# 05 - 工具配置

使用工具名称来选择启用哪些内置工具。

工具名称会与所有可用工具进行匹配。如果你使用了自定义的 `cwd`，`createAgentSession()` 在构建实际内置工具时会应用该 cwd。

对于自定义工具，请参见 06-extensions.md —— 自定义工具通过扩展系统使用 `pi.registerTool()` 注册。

```typescript
import { createAgentSession, SessionManager } from "@earendil-works/pi-coding-agent";

// 只读模式（无 edit/write）
const { session: readOnlySession } = await createAgentSession({
	tools: ["read", "grep", "find", "ls"],
	sessionManager: SessionManager.inMemory(),
});
console.log("Read-only session created");
readOnlySession.dispose();

// 自定义工具选择
const { session: customToolsSession } = await createAgentSession({
	tools: ["read", "bash", "grep"],
	sessionManager: SessionManager.inMemory(),
});
console.log("Custom tools session created");
customToolsSession.dispose();

// 使用自定义工作目录
const customCwd = "/path/to/project";
const { session: customCwdSession } = await createAgentSession({
	cwd: customCwd,
	tools: ["read", "bash", "edit", "write"],
	sessionManager: SessionManager.inMemory(customCwd),
});
console.log("Custom cwd session created");
customCwdSession.dispose();

// 或为自定义工作目录选择特定工具
const { session: specificToolsSession } = await createAgentSession({
	cwd: customCwd,
	tools: ["read", "bash", "grep"],
	sessionManager: SessionManager.inMemory(customCwd),
});
console.log("Specific tools with custom cwd session created");
specificToolsSession.dispose();
```
