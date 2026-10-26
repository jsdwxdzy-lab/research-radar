#!/usr/bin/env python3
"""Deploy research-radar to GitHub Pages and wire up the daily Action.

Usage:
    export GH_TOKEN=ghp_xxx            # repo + workflow scope
    python3 scripts/deploy.py --repo research-radar

What it does
    1. verifies the token (/user)
    2. creates the repository if it does not exist
    3. commits the working tree and pushes it to main
    4. enables GitHub Pages from main / (root)  ->  https://<login>.github.io/<repo>/
    5. triggers the daily workflow once so the first build happens immediately

The token is only used in-process: git receives it through a temporary
GIT_ASKPASS helper that is deleted afterwards.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
ROOT = Path(__file__).resolve().parent.parent


def call(method: str, path: str, token: str, data: dict | None = None, ok=(200, 201, 204)):
    url = API + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "research-radar-deploy",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {"message": raw[:300]}
        if exc.code in ok:
            return exc.code, payload
        raise SystemExit(f"GitHub API {method} {path} -> {exc.code}: {payload.get('message')}")


def run(cmd, env=None, check=True, quiet=True):
    res = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    if res.returncode != 0 and check:
        sys.stderr.write(res.stdout + res.stderr)
        raise SystemExit(f"命令失败：{' '.join(cmd)}")
    if not quiet:
        print(res.stdout.strip())
    return res


def git_askpass(token: str) -> str:
    fd, path = tempfile.mkstemp(prefix="radar-askpass-", suffix=".sh")
    with os.fdopen(fd, "w") as fh:
        fh.write("#!/bin/sh\n")
        fh.write('case "$1" in\n')
        fh.write('  Username*) echo x-access-token ;;\n')
        fh.write(f'  *) echo "{token}" ;;\n')
        fh.write("esac\n")
    os.chmod(path, 0o700)
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="research-radar")
    ap.add_argument("--private", action="store_true", help="私有仓库（Pages 需要付费计划）")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--message", default="radar: 初始部署")
    ap.add_argument("--skip-pages", action="store_true")
    ap.add_argument("--skip-dispatch", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
    if not token:
        print("缺少 GH_TOKEN。请先：export GH_TOKEN=<你的 PAT>（需要 repo + workflow 权限）")
        return 2

    status, user = call("GET", "/user", token)
    login = user.get("login")
    if not login:
        print(f"token 无效：{status}")
        return 2
    print(f"✓ 已认证：{login}")

    full = f"{login}/{args.repo}"
    code, repo = call("GET", f"/repos/{full}", token, ok=(200, 404))
    if code == 404:
        print(f"· 创建仓库 {full}（{'private' if args.private else 'public'}）")
        if not args.dry_run:
            call(
                "POST",
                "/user/repos",
                token,
                {
                    "name": args.repo,
                    "description": "科研雷达：每天自动更新的文献 / 工具 / 会议看板",
                    "private": args.private,
                    "has_issues": True,
                    "has_wiki": False,
                    "auto_init": False,
                },
            )
    else:
        print(f"· 仓库已存在：{repo.get('html_url')}")

    page_url = f"https://{login}.github.io/{args.repo}/"
    if args.repo.lower() == f"{login.lower()}.github.io":
        page_url = f"https://{login.lower()}.github.io/"

    # ---- git ---------------------------------------------------------------
    if not (ROOT / ".git").exists():
        run(["git", "init", "-b", args.branch])
    run(["git", "config", "user.name", login])
    run(["git", "config", "user.email", f"{login}@users.noreply.github.com"])
    run(["git", "add", "-A"])
    staged = run(["git", "diff", "--cached", "--quiet"], check=False)
    if staged.returncode != 0:
        run(["git", "commit", "-m", args.message])
    else:
        print("· 没有需要提交的改动")
    run(["git", "remote", "remove", "origin"], check=False)
    run(["git", "remote", "add", "origin", f"https://github.com/{full}.git"])

    if args.dry_run:
        print(f"[dry-run] 将 push 到 {full}，Pages → {page_url}")
        return 0

    askpass = git_askpass(token)
    try:
        env = dict(os.environ, GIT_ASKPASS=askpass, GIT_TERMINAL_PROMPT="0")
        run(["git", "fetch", "origin", args.branch], env=env, check=False)
        res = run(["git", "push", "-u", "origin", f"HEAD:refs/heads/{args.branch}"], env=env, check=False)
        if res.returncode != 0:
            print(res.stdout + res.stderr)
            if "rejected" in (res.stdout + res.stderr):
                print("远端已有提交。若确认要覆盖：git push -f origin HEAD:main")
            return 1
        print(f"✓ 已推送 {full}")
    finally:
        try:
            os.unlink(askpass)
        except OSError:
            pass

    # ---- Pages -------------------------------------------------------------
    if not args.skip_pages:
        code, _ = call("GET", f"/repos/{full}/pages", token, ok=(200, 404))
        payload = {"source": {"branch": args.branch, "path": "/"}}
        if code == 404:
            call("POST", f"/repos/{full}/pages", token, payload, ok=(201, 409))
            print(f"✓ 已开启 Pages：{page_url}")
        else:
            call("PUT", f"/repos/{full}/pages", token, payload)
            print(f"✓ 已更新 Pages：{page_url}")

    # ---- first build -------------------------------------------------------
    if not args.skip_dispatch:
        code, _ = call(
            "POST",
            f"/repos/{full}/actions/workflows/daily.yml/dispatches",
            token,
            {"ref": args.branch},
            ok=(204, 404),
        )
        print("✓ 已手动触发一次 daily-radar" if code == 204 else "· workflow 尚未生效，1 分钟后再点 Run workflow")

    print("")
    print(f"看板地址：{page_url}")
    print(f"仓库地址：https://github.com/{full}")
    print(f"Actions ：https://github.com/{full}/actions")
    print(f"加 key  ：https://github.com/{full}/settings/secrets/actions  （新建 AGENT_API_KEY）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
