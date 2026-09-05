# 10 - 设置配置

使用 SettingsManager 覆盖设置。

```typescript
import { createAgentSession, SessionManager, SettingsManager } from "@earendil-works/pi-coding-agent";

const cwd = process.cwd();

// 加载当前设置（合并全局 + 项目设置）
const settingsManagerFromDisk = SettingsManager.create(cwd);
console.log("Current settings:", JSON.stringify(settingsManagerFromDisk.getGlobalSettings(), null, 2));

// 覆盖特定设置
const settingsManager = SettingsManager.create(cwd);
settingsManager.applyOverrides({
	compaction: { enabled: false },
	retry: { enabled: true, maxRetries: 5, baseDelayMs: 1000 },
});

const { session: customSettingsSession } = await createAgentSession({
	settingsManager,
	sessionManager: SessionManager.inMemory(),
});
console.log("Session created with custom settings");
customSettingsSession.dispose();

// Setter 会立即更新内存并排队持久化写入。
// 在需要持久化边界时调用 flush()。
settingsManager.setDefaultThinkingLevel("low");
await settingsManager.flush();

// 在应用层显示设置 I/O 错误。
const settingsErrors = settingsManager.drainErrors();
if (settingsErrors.length > 0) {
	for (const { scope, error } of settingsErrors) {
		console.warn(`Warning (${scope} settings): ${error.message}`);
	}
}

// 无文件 I/O 的测试用内存设置：
const inMemorySettings = SettingsManager.inMemory({
	compaction: { enabled: false },
	retry: { enabled: false },
});

const { session: testSession } = await createAgentSession({
	settingsManager: inMemorySettings,
	sessionManager: SessionManager.inMemory(),
});
console.log("Test session created with in-memory settings");
testSession.dispose();
```
