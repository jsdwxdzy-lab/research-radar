# 独立云端日更检查器（代码已备好，尚未部署）

GitHub Actions 执行抓取、离线翻译、提交；Cloudflare Worker 只在北京时间 08:07—12:47 每 20 分钟检查实际看板是否完成。

判断顺序：

1. 公开页面日期、真实抓取日期、完成状态、来源状态、中文标题与摘要覆盖全部正常：不操作。新增为 0 也正常。
2. 仍有日更或发布任务运行：等待。超过 110 分钟记失败状态，不取消任务、不持续排队。
3. 仓库页面已经完成但公开站落后：只触发 pages.yml。
4. 当天尚未抓取或翻译不全：触发 daily.yml；45 分钟冷却，避免频繁重复。发布重试冷却 10 分钟。
5. GitHub API 无法核查：失败退出，不盲目触发。

Worker 没有可公开调用的触发接口，不接收私人聊天、收藏、笔记，也不持有翻译密钥。GitHub 凭据只随请求发送到固定的 api.github.com 仓库端点，日志仅记操作类别。

## 启用条件

需用户自己的 Cloudflare 账号。部署前检查仍选择 Workers Free，未主动开通付费方案。这个检查器每天 15 次运行，通常适合免费额度；免费计划本身也不承诺准点或可用性 SLA。

在 Cloudflare 的加密 Secret 绑定设置 `RADAR_GITHUB_TOKEN`，使用只授权 research-radar 仓库的细粒度 GitHub token，Actions 读写权限用于列运行记录与 workflow_dispatch。不要把它填入此仓库、wrangler.toml、聊天或普通环境变量文档。优先创建专用权限凭据，不复用可能很快过期的本机部署 token；凭据过期会中止补跑。

在该目录使用 Cloudflare 官方 Wrangler 或 Cloudflare 控制台部署 worker.mjs，应用 wrangler.toml 的 cron。这里不自动登录、开通账号或创建凭据。

上线顺序：先发布主仓库修复并验证一次完整日更，让页面内嵌真实 `ok` 和来源统计；然后部署 Worker，观察一次正常跳过和一次受控补跑。在 Cloudflare Scheduled Events 查看检查结果。告警通知渠道尚未配置，不能宣称已通知用户。

## 检查

`node --test ops/cloud_watchdog/worker.test.mjs`（从仓库根运行）。测试全部使用离线响应与占位凭据，不访问网络。

来源：[Cloudflare Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/)、[Workers 定价与免费额度](https://developers.cloudflare.com/workers/platform/pricing/)、[GitHub 定时触发的延迟与丢弃限制](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。

本方案把触发器分散到两个供应商；GitHub 执行平台或公共数据源故障时仍可能延迟，不能保证每天新增论文，也不能保证 07:30 准时完成。
