# 13 - 会话运行时

当你需要替换活跃的 AgentSession 时使用 AgentSessionRuntime，例如用于新建会话、恢复、分叉或导入流程。

重要的模式是：运行时替换活跃会话后，需要将所有会话级别的订阅和扩展绑定重新绑定到 `runtime.session`。

```typescript
import {
	type CreateAgentSessionRuntimeFactory,
	createAgentSessionFromServices,
	createAgentSessionRuntime,
	createAgentSessionServices,
	getAgentDir,
	SessionManager,
} from "@earendil-works/pi-coding-agent";

const createRuntime: CreateAgentSessionRuntimeFactory = async ({ cwd, sessionManager, sessionStartEvent }) => {
	const services = await createAgentSessionServices({ cwd });
	return {
		...(await createAgentSessionFromServices({
			services,
			sessionManager,
			sessionStartEvent,
		})),
		services,
		diagnostics: services.diagnostics,
	};
};
const runtime = await createAgentSessionRuntime(createRuntime, {
	cwd: process.cwd(),
	agentDir: getAgentDir(),
	sessionManager: SessionManager.create(process.cwd()),
});

let unsubscribe: (() => void) | undefined;

async function bindSession() {
	unsubscribe?.();
	const session = runtime.session;
	await session.bindExtensions({});
	unsubscribe = session.subscribe((event) => {
		if (event.type === "queue_update") {
			console.log("Queued:", event.steering.length + event.followUp.length);
		}
	});
	return session;
}

let session = await bindSession();
const originalSessionFile = session.sessionFile;
console.log("Initial session:", originalSessionFile);

// 新建会话
await runtime.newSession();
session = await bindSession();
console.log("After newSession():", session.sessionFile);

// 切换回原会话
if (originalSessionFile) {
	await runtime.switchSession(originalSessionFile);
	session = await bindSession();
	console.log("After switchSession():", session.sessionFile);
}

unsubscribe?.();
await runtime.dispose();
```
