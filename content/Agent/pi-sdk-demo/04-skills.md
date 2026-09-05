# 04 - 技能配置

技能提供加载到系统提示词中的专业指令。可以发现、筛选、合并或替换技能。

```typescript
import {
	createAgentSession,
	createSyntheticSourceInfo,
	DefaultResourceLoader,
	getAgentDir,
	SessionManager,
	type Skill,
} from "@earendil-works/pi-coding-agent";

// 或内联定义自定义技能
const customSkill: Skill = {
	name: "my-skill",
	description: "Custom project instructions",
	filePath: "/virtual/SKILL.md",
	baseDir: "/virtual",
	sourceInfo: createSyntheticSourceInfo("/virtual/SKILL.md", { source: "sdk" }),
	disableModelInvocation: false,
};

const loader = new DefaultResourceLoader({
	cwd: process.cwd(),
	agentDir: getAgentDir(),
	skillsOverride: (current) => {
		const filteredSkills = current.skills.filter((s) => s.name.includes("browser") || s.name.includes("search"));
		return {
			skills: [...filteredSkills, customSkill],
			diagnostics: current.diagnostics,
		};
	},
});
await loader.reload();

// 从 cwd/.pi/skills、~/.pi/agent/skills 等发现所有技能
const { skills: allSkills, diagnostics } = loader.getSkills();
console.log(
	"Discovered skills:",
	allSkills.map((s) => s.name),
);
if (diagnostics.length > 0) {
	console.log("Warnings:", diagnostics);
}

const { session } = await createAgentSession({
	resourceLoader: loader,
	sessionManager: SessionManager.inMemory(),
});
console.log("Session created with filtered skills");
session.dispose();
```
