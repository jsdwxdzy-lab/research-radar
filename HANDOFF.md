# HANDOFF — 这个项目现在到哪一步了

写于 2026-10-26。给你自己，也给下一个接手的人看。

## 一句话

抓取、打分、看板、agent 点评**全部在本地跑通了**；**上公网这一步我没做**（按你的要求，留给下一个 AI 按 `AGENTS.md` 执行）。

## 已经完成

| 能力 | 状态 |
| --- | --- |
| 每天抓 arXiv / Crossref / OpenAlex / Nature 系 RSS / GitHub Releases | ✅ |
| 主题打分、跨源去重、相邻主题降权、负向过滤 | ✅ 502 条候选 → 23 条入库 |
| 单文件 HTML 看板（分区筛选、历史浏览、搜索、未读/星标/备注、趋势、统计、导出、快捷键、深色、手机） | ✅ [dashboard.html](dashboard.html) |
| Markdown 日报 + 历史归档 | ✅ `daily/`、`latest.md` |
| 本地定时（每天 07:40） | ✅ 已装 launchd，验证过一次 exit 0 |
| LLM 点评（总览 + 每条一句「为什么值得看」） | ✅ 已接你的 `agent-team-api`，`claude-opus-5-5`，今天已生成真点评 |
| GitHub Pages + Actions 自动更新 | ⬜ **待部署** |
| `AGENT_API_KEY` 写进仓库 Secrets | ⬜ **待配置**（只能网页操作） |

## 下一步只有三件事

1. **给 token**：GitHub → Settings → Developer settings → PAT，勾 `repo` + `workflow`（fine-grained 见 `AGENTS.md` §4.1）。
   存到仓库外：`~/.dsh/.secrets/gh_token`，权限 600。
2. **让下一个 AI 跑**：把这句话发给它 ——

   > 请读 `/Users/zhouy/dsh/research-radar/AGENTS.md`，按里面的步骤把这个项目部署到 GitHub Pages，
   > 仓库名 research-radar、公开。GitHub token 我放在 `/Users/zhouy/dsh/.secrets/gh_token`。
   > 部署完把公开地址和验收结果告诉我。

3. **加一个 Secret**（网页 30 秒）：`Settings → Secrets and variables → Actions → New repository secret`，
   Name `AGENT_API_KEY`，值就是 `/Users/zhouy/dsh/.secrets/agent_key` 里的内容。

部署完成后记得关掉本机定时，否则本地和云端都会抓、产生分叉：

```bash
cd ~/dsh/research-radar && bash uninstall_launchd.sh
```

## 凭据与安全（重要）

- **GitHub token**：还没有生成，等你提供。任何情况下都不要提交进仓库。
- **Agent key**：你现在这个 key（`sk-DSxT…`）在对话里出现过，**建议部署完就去服务商后台轮换一次**，
  换完同步更新两处：`/Users/zhouy/dsh/.secrets/agent_key` 和 GitHub 的 `AGENT_API_KEY`。
- 仓库是 public：里面只有论文元数据、代码、配置（不含 key）。agent 的 `base_url` 和模型名会公开，这没问题。
- 看板用浏览器 `localStorage` 存阅读状态，不涉及任何个人信息上传。

## 一次日常运行的成本

- 抓取：0 元（OpenAlex 约 12 次请求，免费额度内）。
- LLM：每天 1 次调用，约 9–13k input tokens（那个端点会注入 ~6.7k 的系统提示），结果按天缓存在 SQLite，重跑不重复花钱。
- GitHub Actions：public 仓库免费。

## 目录速查

```
research-radar/
├── dashboard.html / index.html   # 看板（每次运行重新生成，别手改）
├── latest.md / daily/            # Markdown 版日报
├── AGENTS.md                     # ← 给下一个 AI 的执行手册
├── README.md                     # 给人看的使用说明
├── HANDOFF.md                    # 本文件
├── config/{config,agent,events}.json
├── radar/                        # 代码（纯标准库）
├── scripts/{deploy,verify,count_today}.py
├── .github/workflows/daily.yml   # 每天 07:30 CST
├── docs/preview.png
└── state/radar.sqlite3           # 去重与历史（当前 36 条 / 5 天），不要删
```

## 如果部署卡住

- 跑 `python3 scripts/verify.py --local`，先确认本地没坏。
- Pages 404：等 1–3 分钟；确认 Source 是 `main` / `/ (root)`。
- Action 没跑：GitHub 的 cron 有 5–30 分钟延迟，属正常。
- 详见 `AGENTS.md` §9「已知坑」。
