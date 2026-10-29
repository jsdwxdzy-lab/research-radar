# 部署 checklist（本机代码已就绪）

1. 授权 Wrangler（需含 `workers_kv:write` / `workers:write`）：

```bash
node /private/tmp/research-radar-cloudflare-tooling/npm-cache/_npx/0a46806eee71b756/node_modules/wrangler/bin/wrangler.js login --device --browser=false --use-keyring --scopes account:read user:read workers_scripts:write workers_tail:read workers_kv:write workers:write
```

2. 创建 KV 并写入 `wrangler.toml` 的 `id` / `preview_id`：

```bash
cd /Users/zhouy/dsh/research-radar/ops/cloud_sync
npx wrangler kv namespace create research-radar-reading
```

3. 部署 Worker：

```bash
npx wrangler deploy
```

4. 设置同步口令 Secret（终端交互输入，勿写入仓库）：

```bash
npx wrangler secret put RADAR_SYNC_TOKEN
```

5. 把得到的 `https://research-radar-sync.<subdomain>.workers.dev` 填进  
   `radar/web/dashboard.html` 的 `SYNC_BASE`，然后：

```bash
cd /Users/zhouy/dsh/research-radar
python3 -B -m radar dashboard
```

6. （推荐）Zero Trust → Access 保护该 Worker 主机名，仅你的邮箱 OTP；  
   CORS 允许 `https://jsdwxdzy-lab.github.io`。Access 配好后仍可用口令，二者任一即可。

7. 推送仓库后公开看板才会带上同步按钮与 `data.json`。
