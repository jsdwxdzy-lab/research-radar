# research-radar-sync

单用户阅读状态同步 API。明文 JSON 存 KV。

鉴权（任一即可）：

1. Cloudflare Access 邮箱 OTP（推荐，浏览器走 `/v1/bridge`）
2. Secret `RADAR_SYNC_TOKEN`，请求头 `Authorization: Bearer …`（Access 未配好时的简单登录）

## 端点

- `GET/PUT /v1/reading` — 读写阅读状态
- `GET /v1/bridge` — 登录桥接页（供看板弹窗 / iframe，同源带 Cookie 调用 API）

仅允许看板 Origin：`https://jsdwxdzy-lab.github.io`。

## 部署

```bash
cd ops/cloud_sync
# 创建 KV 后把 id 写入 wrangler.toml 的 READING_KV
npx wrangler kv namespace create research-radar-reading
npx wrangler deploy
npx wrangler secret put RADAR_SYNC_TOKEN   # 本地输入，不要写入仓库
```

然后在 Cloudflare Zero Trust 里为该 Worker 主机名添加 Access 应用，Identity 选你的邮箱 OTP，并允许 CORS 来源 `https://jsdwxdzy-lab.github.io`。

把部署得到的 `https://….workers.dev` 填进 `radar/web/dashboard.html` 的 `SYNC_BASE`。

不要把 GitHub PAT 或同步口令写入本目录。
