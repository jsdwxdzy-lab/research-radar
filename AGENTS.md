# AGENTS.md — 交接说明（给下一位 AI agent）

> 你接手的是一个**已经跑通、但还没上公网**的个人科研雷达项目。
> 你的任务：把它部署成 GitHub Pages 公开看板，让 GitHub Actions 每天自动更新，并把 agent API key 配进仓库 Secrets。
> 预计 15–25 分钟，只有「拿 token」这一步需要人类配合。

---

## 0. 一句话任务

```
把 /Users/zhouy/dsh/research-radar 推到公开仓库 research-radar
→ 开启 Pages（main / root）
→ 加 Actions secret AGENT_API_KEY
→ 手动触发一次 workflow 并确认 https://<login>.github.io/research-radar/ 可访问、有今日点评
```

---

## 1. 当前状态（已在本机验证，可直接复现）

- 本机 pipeline 完整可用：抓取 → 打分 → 去重入库 → 生成看板 + Markdown 日报。
- 看板 `dashboard.html` / `index.html` 已生成，36 条、5 天历史，功能正常（分区筛选、历史、搜索、未读/星标/备注、趋势、统计、导出）。
- **agent API 已配置并真实调用成功**：`https://agent-team-api.myrimate.cn/v1`，模型 `claude-opus-5-5`，今天已生成 6 条点评 + 1 段总览（约 12k tokens/次）。
- **尚未做的事**：没有 git remote、没有 GitHub 仓库、没有 Pages、没有 Actions secret。本机**没有** `gh` CLI、没有全局 git 身份、没有 SSH key。

## 2. 环境事实

| 项 | 值 |
| --- | --- |
| 项目根 | `/Users/zhouy/dsh/research-radar` |
| Python | `/usr/bin/python3`（3.9.6），**纯标准库，无第三方依赖** |
| 数据库 | `state/radar.sqlite3`（约 160 KB，36 条 / 5 天历史，**去重靠它，不要删**） |
| 本地 agent key | `/Users/zhouy/dsh/.secrets/agent_key`（600，仓库外，勿复制进项目） |
| 时区 | Asia/Shanghai；cron 用 UTC |
| 记忆点 | 项目内**任何文件都不要写入 token 或 key**，仓库是 public |

## 3. 先跑这三条（不需要任何凭据，约 30 秒）

```bash
cd /Users/zhouy/dsh/research-radar
python3 -B -m radar status
python3 scripts/verify.py --local
python3 -B -m radar agent-test
```

预期：

- `status` → `条目总数 36`，表格里有 ok 记录
- `verify --local` → 全部 `PASS`，最后一行「结果：全部通过」
- `agent-test` → `成功：'正常'  · model=claude-opus-5-5`

任何一条失败，先修本地，不要往下走。

## 4. 部署（唯一需要人类凭据的步骤）

### 4.1 让人类提供 PAT

要么经典 token 勾 **`repo` + `workflow`**，要么 fine-grained 给：
`Administration: RW`（建仓库）、`Contents: RW`（推送）、`Pages: RW`（开 Pages）、`Workflows: RW`（触发 Action）。

**让人类自己**把 token 写进仓库外的文件（不要贴进对话、不要写进项目）：

```bash
mkdir -p /Users/zhouy/dsh/.secrets
printf '%s' 'ghp_xxx' > /Users/zhouy/dsh/.secrets/gh_token
chmod 600 /Users/zhouy/dsh/.secrets/gh_token
```

如果人类坚持把 token 贴给你，用完提醒他去 GitHub 撤销重签。

### 4.2 执行部署脚本（幂等，可重复跑）

```bash
cd /Users/zhouy/dsh/research-radar
export GH_TOKEN=$(cat /Users/zhouy/dsh/.secrets/gh_token)
python3 scripts/deploy.py --repo research-radar
```

脚本依次做：

1. `GET /user` 验证 token（失败会明确报 401）
2. 仓库不存在就 `POST /user/repos` 创建（**public**，不要加 `--private`）
3. `git init -b main` → `add -A` → `commit` → `push`
   （token 通过临时 `GIT_ASKPASS` 传入，不写进 `.git/config`，结束后删除）
4. 开启 Pages：source = `main` / `/`（已开启则 PUT 更新）
5. `workflow_dispatch` 触发一次 `daily.yml`

成功时会打印 `看板地址：https://<login>.github.io/research-radar/`。

**手动兜底**（脚本因权限/网络失败时）：网页建 public 仓库 → `git remote add origin ...` → `git push -u origin main` → Settings → Pages → Source `main` / `/ (root)` → Actions 里点 `Run workflow`。

### 4.3 用 API 复查（可选）

```bash
curl -s -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/<login>/research-radar/pages | head -20
```

应看到 `"status": "built"`（首次可能要等 1–3 分钟，先是 `null` 或 `building`）。

## 5. 配 Secrets（必须走网页，API 做不到）

GitHub 设置 secret 需要 libsodium sealed box 加密，本机没有 PyNaCl，**不要试图用 API 设置**。
让人类（或你自己在浏览器里）操作：

```
https://github.com/<login>/research-radar/settings/secrets/actions
→ New repository secret
→ Name: AGENT_API_KEY
→ Secret: 内容读 /Users/zhouy/dsh/.secrets/agent_key
```

不加 secret 也能跑，只是看板没有「今日点评」，`verify --url` 那一条会显示 `FAIL ... 没有也不影响主流程`。

## 6. 触发 + 验收（Definition of Done）

```bash
export GH_TOKEN=$(cat /Users/zhouy/dsh/.secrets/gh_token)
curl -s -X POST \
  -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/<login>/research-radar/actions/workflows/daily.yml/dispatches \
  -d '{"ref":"main"}'

python3 scripts/verify.py --url https://<login>.github.io/research-radar/
```

必须全部满足：

- [ ] `verify --url` 全 PASS（页面 200、含 `const DATA`、`dashboard.html` 200、条目 > 0、日期是今天或昨天）
- [ ] Actions 里 `daily-radar` 最近一次是绿勾，且产生了一条 `radar: YYYY-MM-DD 自动更新` 提交
- [ ] 页面顶部出现「今日点评」段落（说明 `AGENT_API_KEY` 生效）
- [ ] `https://<login>.github.io/research-radar/dashboard.html` 也能直接打开
- [ ] （次日）北京时间 07:30 之后自动出现新提交 —— 说明 `schedule` 生效

`verify` 退出码 0 才算完成。

## 7. 部署完的收尾（重要，否则会产生分叉）

本机现在还装着一个 launchd 定时任务，会在本地也抓一次、产生未提交改动。云端接管后要关掉：

```bash
cd /Users/zhouy/dsh/research-radar
bash uninstall_launchd.sh          # 停掉本地 07:40 抓取
git pull                           # 以后本地看最新版就这样更新
```

然后告诉人类：

- 公开地址：`https://<login>.github.io/research-radar/`
- 换模型：改 `config/agent.json` 的 `base_url` / `model`，改完 commit（key 仍在 Secrets 里，不用动）
- 补历史：Actions → daily-radar → Run workflow，`hours=168` 且勾 `backfill`
- 改时间：`.github/workflows/daily.yml` 的 cron（UTC，减 8 小时 = 北京时间）

## 8. 绝对不要做

1. 不要 `git add` 任何含 token/key 的文件；`.secrets/` 在项目外，`state/http_cache/`、`logs/` 已在 `.gitignore`。
2. 不要删 `state/radar.sqlite3` —— 删了会把 7 天内的旧论文当新条目重发一遍。
3. 不要 `git push -f`（会丢自动提交历史）；脚本拒绝强推。
4. 不要手改 `dashboard.html` / `index.html` —— 每次运行都会被覆盖，改模板 `radar/web/dashboard.html`。
5. 不要把仓库改成 private 还指望 Pages 免费能用。

## 9. 已知坑

| 现象 | 原因 / 处理 |
| --- | --- |
| Pages URL 404 | 首次开启要 1–3 分钟；确认 Source 是 `main` / `/ (root)` |
| Action 没按时跑 | GitHub 的 cron 会延迟 5–30 分钟，偶尔更久；不是故障 |
| `workflow_dispatch` 返回 404 | workflow 文件还没进默认分支，push 后等 1 分钟再试 |
| Action 失败在 push | workflow 已声明 `permissions: contents: write`；若仓库设置了 branch protection 需要放开 |
| 点评是空的 | 没配 `AGENT_API_KEY`，或端点不支持 `response_format` → 把 `config/agent.json` 的 `json_mode` 改 `false` |
| 提交里出现 `state/http_cache` | `.gitignore` 被改坏了，别提交，`git rm -r --cached state/http_cache` |
| 60 天后定时任务停了 | 仓库 60 天无提交会停 schedule；本项目每天提交，正常不会触发 |

## 10. 代码地图

| 路径 | 作用 |
| --- | --- |
| `radar/pipeline.py` | 抓取 → 合并 → 打分 → 入库 → 渲染 → 可选 agent 点评 |
| `radar/sources/` | arxiv / crossref / openalex / rss / github 五个适配器 |
| `radar/score.py` | 关键词权重 + 主题分层（core/adjacent）+ 负向过滤 |
| `radar/dashboard.py` + `radar/web/dashboard.html` | 看板数据与模板（单文件、内联 CSS/JS） |
| `radar/agent.py` | OpenAI 兼容 LLM 调用，key 只从 env 或仓库外文件读 |
| `radar/store.py` | SQLite：条目去重、运行记录、agent 点评缓存 |
| `config/config.json` | 主题/关键词/作者/期刊/数据源/阈值 —— 调参都在这 |
| `config/agent.json` | LLM 端点与模型（不含 key） |
| `scripts/deploy.py` | 本次部署脚本 |
| `scripts/verify.py` | 本地 / 线上验收 |
| `.github/workflows/daily.yml` | 每天 07:30 CST 的自动更新 |

## 11. 给人类的一句话交付模板

> 看板已上线：`https://<login>.github.io/research-radar/`，每天北京时间 07:30 自动更新。
> 建议把 GitHub token 和 agent key 都轮换一次（它们都在聊天里出现过）。
