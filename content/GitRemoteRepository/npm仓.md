https://www.npmjs.com/



## 上传 npm 包

1. **登入 npm**: 在命令行中运行下述指令，使用之前注册的账号登入

```
npm login
```

2. **发布包**: 登入成功后，在项目的根目录下运行下述指令，发布包

```
npm publish



403的话，见下面
```


## 生成 Granular Access Token + 勾选 Bypass two-factor authentication（适合 CI / 脚本、脚手架自动化发布）

1. npm 头像 → **Access Tokens** → Generate New Token → 选择 **Granular Access Token**
2. 权限：**Read and write (publish and stage)**
3. 包范围：All packages / 指定包 `lsw-template-cli`
4. ✅ **重点：勾选 Bypass two-factor authentication**（默认不勾！不勾这个 token 照样 403）npm
5. 复制生成的 token（只显示一次！）
6. 终端配置这个 token：

```
npm config set //registry.npmjs.org/:_authToken="这里粘贴你的token"
```

7. 之后直接 `npm publish`，不再需要 2FA 验证码

> ⚠️ 安全提醒：这个 token 具备发布权限，不要硬编码提交到 git



## 更新 npm包

后续如果对包进行了更改，可以根据更改的内容，进行包的更新

包更新，有下面三种级别

| 操作        | 命令                  | 说明                             |
| --------- | ------------------- | ------------------------------ |
| 补丁版本更新    | `npm version patch` | 用于修复小问题，不影响现有功能，仅更新补丁版本号       |
| 小版本更新     | `npm version minor` | 增加新功能，但保持向后兼容性，更新小版本号          |
| 大版本更新     | `npm version major` | 有重大变更，可能不兼容旧版本，更新大版本号          |
| 重新发布更新后的包 | `npm publish`       | 每次更新版本号后，运行此命令将更新后的包发布到 npm 仓库 |

