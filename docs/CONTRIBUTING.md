## Helios 协作开发快速参考（tuzi 版）

本参考覆盖日常开发从同步到提 PR 的最小闭环，所有成员统一按此执行。

### 约定
- **主仓库**: `Mike1075/helios-game`
- **个人 Fork**: 你的 GitHub 仓库，例如 `tuzi20462023/helios-game`
- **主分支**: `main`
- **分支命名**: `feature/<姓名或工号>/<任务名>`，如 `feature/tuzi/add-login`
- **提交信息**: 使用 Conventional Commits（如 `feat:`、`fix:`、`chore:`）

### 首次克隆（Fork 工作流）
1. 在 GitHub 上 Fork 主仓库到你账号。
2. 克隆你的 Fork：
```bash
# 任选其一
# HTTPS
git clone https://github.com/<你的GitHub用户名>/helios-game.git
# SSH（推荐）
# git clone git@github.com:<你的GitHub用户名>/helios-game.git
```
3. 添加主仓库为上游源：
```bash
cd helios-game
git remote add upstream https://github.com/Mike1075/helios-game.git
```
4. 验证远端：
```bash
git remote -v
# 期望看到：origin=你的Fork，upstream=主仓库
```

### 每日开始工作：先同步再开分支
```bash
git checkout main
git fetch upstream --prune
git pull --rebase upstream main
git push origin main
git checkout -b feature/<姓名>/<任务名>
```

### 开发→提交→推送
```bash
# 开发完成后
git add -A
# 示例：
# feat: add login page
# fix: correct auth header
# chore: update docs
git commit -m "<type>: <message>"
# 首次推送当前分支需 -u
git push -u origin feature/<姓名>/<任务名>
```

### 发起 Pull Request（PR）
- 目标：把你的分支合并到主仓库 `main`
- 打开浏览器：
`https://github.com/Mike1075/helios-game/compare/main...<你的GitHub用户名>:feature/<姓名>/<任务名>`
- 填写：
  - **Title**: 简要说明（例如：`feat: add login page`）
  - **Description**: 变更点、影响范围、测试要点
  - 若无法指派 Reviewer：在评论里 `@Mike1075` 请求审核
  - 勾选 “Allow edits by maintainers”
- Vercel 预览提示需管理员授权，贡献者无需操作

### 分支落后于 main 时的更新
```bash
git checkout feature/<姓名>/<任务名>
git fetch upstream
git rebase upstream/main
# 若有冲突，按文件解决后：
# git add <文件>
# git rebase --continue
# 完成后强推（rebase 会改历史）
git push -f origin feature/<姓名>/<任务名>
```

### Cursor/VS Code 推荐设置（自动推送、自动拉取）
将以下加入设置（JSON）：
```json
{
  "git.postCommitCommand": "push",
  "git.autofetch": true,
  "git.confirmSync": false,
  "git.pruneOnFetch": true,
  "git.pushAutoSetupRemote": true
}
```

### 网络与认证（可选）
- 无代理直连：确保未设置 `http(s).proxy`
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```
- 建议配置 SSH：
```bash
ssh-keygen -t ed25519 -C "<你的标识>"
# 将公钥添加到 GitHub → Settings → SSH and GPG keys
ssh -T git@github.com
```
- 若公司网络限制 22 端口，可用 443：在 `~/.ssh/config` 中加入：
```bash
Host github.com
  HostName ssh.github.com
  Port 443
  User git
  IdentityFile ~/.ssh/id_ed25519
```

### PR 检查清单
- [ ] 分支从最新 `main` 开出
- [ ] 提交信息规范（Conventional Commits）
- [ ] 自测通过（含启动、本地逻辑、关键路径）
- [ ] PR 描述清楚影响范围与回滚方式
- [ ] 勾选 “Allow edits by maintainers”

### 常见问题
- 403/权限不足：说明你在向主仓库直接推送。应推到 `origin`（你的 Fork），然后对主仓库发 PR。
- Vercel 检查失败：多为“需要授权预览”提示，不影响代码评审，管理员处理即可。
- 代理导致克隆失败：取消代理或改用 SSH 方案。

—— 以上为最小可行流程。若与正式《协作开发说明书》不一致，以最新版说明书优先（当前为 1.2）。 