"""Theory map: load knowledge/, validate it, and render static pages to theory/.

Content rules live in knowledge/README.md. Personal notes never pass through
here; they stay in the reader's browser.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from . import theory_md
from .theory_md import CLAIMS, LAYERS, esc, safe_url

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "web" / "theory"
REPO_URL = "https://github.com/jsdwxdzy-lab/research-radar"
KATEX_VERSION = "0.19.1"
KATEX_CSS_SRI = "sha384-WwGtaC6ywCHxA5cstpj/3+xIZvTez8dq2IcBQaXRkenHZ7FVVq1ZROtURwfbtTlG"
KATEX_JS_SRI = "sha384-a1WQdjRj162i159OYq041X6I4K8NenkrI09LlPmiHg0YOb7CR+wJOraXwK9abpnE"

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUS = {
    "candidate": ("候选", "只有题目、学习动机和拟连接的节点，还没有正文。"),
    "draft": ("草稿", "已有正文，但来源和推导还没有核查完，不能当作定论。"),
    "verified": ("已核验", "已完成核验记录里写明的项目；只在写明的范围内成立，不表示绝对无误。"),
    "needs-revision": ("待修订", "发现了错误、来源失效、版本变化或条件需要更正，修订前请谨慎使用。"),
    "superseded": ("已替代", "这个节点已被拆分或合并，请转到新节点。"),
}
NODE_TYPES = {
    "problem": ("问题", "组织一段学习过程"),
    "concept": ("概念", "澄清对象、定义和含义"),
    "method": ("方法", "解释设计动机与求解过程"),
    "contrast": ("对照", "明确对应关系和区别"),
    "example": ("实例", "用最小问题检验理解"),
    "synthesis": ("综合", "提炼跨方法的一般结构"),
}
# type: (tag, sentence template with {a}=from and {b}=to, symmetric?)
RELATIONS = {
    "prerequisite": ("需要先理解", "{a} 是 {b} 的先修", False),
    "foundation": ("推导基础", "{a} 是 {b} 某一层推导的基础", False),
    "special-case": ("特例", "{a} 是 {b} 的特例", False),
    "equivalent-under": ("条件下等价", "{a} 在下述条件下等价于 {b}", False),
    "approximates": ("近似", "{a} 近似于 {b}", False),
    "generalizes": ("推广", "{a} 推广了 {b}", False),
    "shares-tool": ("共享工具", "{a} 与 {b} 共享同一数学工具", True),
    "computes": ("用于计算", "{a} 用于计算 {b}", False),
    "explains": ("用于解释", "{a} 用于解释 {b}", False),
    "contrasts": ("对照", "{a} 与 {b} 形成对照", True),
    "analogy": ("仅为类比", "{a} 与 {b} 仅构成启发性类比，不代表数学等价", True),
}
DIRECTIONS = {
    "down": ("向下追溯", "看不懂某一步为什么成立时，补定义、数学工具或物理假设"),
    "in": ("向内深入", "理解直觉但无法重建方法时，展开推导和算法步骤"),
    "across": ("横向连接", "想理解两个方法的关系时，建立对照并写明条件"),
    "up": ("向上抽象", "想看更大的理论图景时，提炼共同问题和一般原理"),
    "out": ("向外迁移", "想知道能用于什么新问题时，连接其他应用和论文"),
}
SOURCE_KINDS = {"textbook": "教材", "paper": "论文", "docs": "官方文档", "benchmark": "基准研究", "practice": "经验记录"}
DIMENSIONS = [
    ("explain", "能解释核心概念"),
    ("derive", "能重建关键推导"),
    ("limits", "理解成立条件和局限"),
    ("connect", "能与其他节点正确联系"),
    ("apply", "能应用于新问题"),
]
DIM_STATES = [("", "未评估"), ("learning", "正在理解"), ("confident", "已有把握"), ("review", "需要复习")]


@dataclass
class Issue:
    level: str  # "error" | "warning"
    where: str
    message: str

    def __str__(self) -> str:
        tag = "错误" if self.level == "error" else "提醒"
        return f"[{tag}] {self.where}：{self.message}"


@dataclass
class KB:
    root: Path
    meta: dict = field(default_factory=dict)        # domains.json "root": title, intro
    domains: list = field(default_factory=list)
    research_lines: list = field(default_factory=list)
    nodes: dict = field(default_factory=dict)       # id -> meta (with "body", "file")
    relations: list = field(default_factory=list)
    paths: dict = field(default_factory=dict)
    sources: dict = field(default_factory=dict)
    reviews: dict = field(default_factory=dict)     # node id -> list
    issues: list = field(default_factory=list)
    rendered: dict = field(default_factory=dict)    # node id -> RenderResult

    def err(self, where: str, msg: str) -> None:
        self.issues.append(Issue("error", where, msg))

    def warn(self, where: str, msg: str) -> None:
        self.issues.append(Issue("warning", where, msg))

    @property
    def errors(self) -> list:
        return [i for i in self.issues if i.level == "error"]

    @property
    def domain_map(self) -> dict:
        return {d["id"]: d for d in self.domains}

    @property
    def line_map(self) -> dict:
        return {r["id"]: r for r in self.research_lines}

    # ---- tree helpers (valid only after validate() reported no tree errors) ----
    def children(self, pid: str) -> list:
        kids = [nid for nid, n in self.nodes.items() if n.get("parent") == pid]
        return sorted(kids, key=lambda x: (x not in self._with_children(), self.nodes[x]["title"]))

    def _with_children(self) -> set:
        return {n.get("parent") for n in self.nodes.values()}

    def ancestors(self, nid: str) -> list:
        """Parent chain from the domain down to (not including) nid: [domain_id, node, ...]."""
        chain, cur, seen = [], self.nodes.get(nid, {}).get("parent"), set()
        while cur and cur not in seen:
            seen.add(cur)
            chain.append(cur)
            cur = self.nodes[cur].get("parent") if cur in self.nodes else None
        return list(reversed(chain))

    def domain_of(self, nid: str) -> str:
        chain = self.ancestors(nid)
        return chain[0] if chain else ""

    def subtree(self, pid: str) -> list:
        out, stack = [], list(self.children(pid))
        while stack:
            x = stack.pop()
            out.append(x)
            stack.extend(self.children(x))
        return out

    def research_distance(self, line: str | None = None) -> dict:
        """Steps from each node to the nearest node tagged with a research line
        (any line, or only `line`), walking tree edges and relations both ways."""
        adj: dict = {nid: set() for nid in self.nodes}
        for nid, n in self.nodes.items():
            p = n.get("parent")
            if p in self.nodes:
                adj[nid].add(p)
                adj[p].add(nid)
        for r in self.relations:
            a, b = r.get("from"), r.get("to")
            if a in adj and b in adj:
                adj[a].add(b)
                adj[b].add(a)
        dist = {nid: 0 for nid, n in self.nodes.items()
                if (line in (n.get("research") or []) if line else n.get("research"))}
        frontier = list(dist)
        while frontier:
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    if v not in dist:
                        dist[v] = dist[u] + 1
                        nxt.append(v)
            frontier = nxt
        return dist


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------
def _read_json(kb: KB, path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        kb.err(str(path.relative_to(kb.root)), f"JSON 无法解析：{e}")
        return default


def _split_front_matter(text: str):
    # Metadata is a ```json fenced block at the very top. Not `---` YAML front
    # matter: GitHub Pages runs Jekyll here and would try to parse that.
    if not text.startswith("```json\n"):
        return None, text
    end = text.find("\n```\n", 8)
    if end < 0:
        return None, text
    return text[8:end], text[end + 5:]


def load(root: Path | None = None) -> KB:
    root = Path(root or ROOT)
    base = root / "knowledge"
    kb = KB(root=root)
    dom = _read_json(kb, base / "domains.json", {})
    kb.meta = dom.get("root") or {}
    kb.domains = dom.get("domains") or []
    kb.research_lines = dom.get("research_lines") or []
    kb.relations = _read_json(kb, base / "relations.json", {}).get("relations", [])
    for s in _read_json(kb, base / "sources.json", {}).get("sources", []):
        sid = s.get("id", "")
        if sid in kb.sources:
            kb.err("knowledge/sources.json", f"来源 ID 重复：{sid}")
        kb.sources[sid] = s
    for f in sorted((base / "nodes").glob("*.md")) if (base / "nodes").exists() else []:
        where = f"knowledge/nodes/{f.name}"
        fm, body = _split_front_matter(f.read_text(encoding="utf-8"))
        if fm is None:
            kb.err(where, "开头缺少 ```json 代码块包住的元信息")
            continue
        try:
            meta = json.loads(fm)
        except ValueError as e:
            kb.err(where, f"元信息 JSON 无法解析：{e}")
            continue
        nid = meta.get("id", "")
        if nid != f.stem:
            kb.err(where, f"文件名必须与 id 一致（id={nid!r}）")
        if nid in kb.nodes:
            kb.err(where, f"节点 ID 重复：{nid}")
        meta["body"] = body
        meta["file"] = where
        kb.nodes[nid] = meta
    for f in sorted((base / "paths").glob("*.json")) if (base / "paths").exists() else []:
        p = _read_json(kb, f, None)
        if not isinstance(p, dict):
            continue
        p["file"] = f"knowledge/paths/{f.name}"
        if p.get("id") != f.stem:
            kb.err(p["file"], f"文件名必须与 id 一致（id={p.get('id')!r}）")
        kb.paths[p.get("id", f.stem)] = p
    for f in sorted((base / "reviews").glob("*.json")) if (base / "reviews").exists() else []:
        r = _read_json(kb, f, [])
        kb.reviews[f.stem] = r if isinstance(r, list) else []
    return kb


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------
def _nonempty(v) -> bool:
    return bool(v.strip()) if isinstance(v, str) else bool(v)


def validate(kb: KB) -> KB:
    domains, lines = kb.domain_map, kb.line_map
    if not domains:
        kb.err("knowledge/domains.json", "没有定义领域")
    for group, label, required in ((kb.domains, "领域", ("title", "summary")),
                                   (kb.research_lines, "研究线", ("title",))):
        ids = [x.get("id", "") for x in group]
        for x in group:
            if not ID_RE.match(x.get("id", "")):
                kb.err("knowledge/domains.json", f"{label} ID 不合法：{x.get('id')!r}")
            for k in required:
                if not _nonempty(x.get(k)):
                    kb.err("knowledge/domains.json", f"{label} {x.get('id')} 缺少 {k}")
        for d in {i for i in ids if ids.count(i) > 1}:
            kb.err("knowledge/domains.json", f"{label} ID 重复：{d}")
    for d in domains:
        if d in kb.nodes:
            kb.err("knowledge/domains.json", f"领域 ID 与节点 ID 冲突：{d}")

    for sid, s in kb.sources.items():
        where = f"来源 {sid}"
        if not ID_RE.match(sid):
            kb.err(where, "ID 不合法")
        if s.get("kind") not in SOURCE_KINDS:
            kb.err(where, f"kind 必须是 {'/'.join(SOURCE_KINDS)}")
        if not _nonempty(s.get("citation")):
            kb.err(where, "缺少 citation")
        if not (s.get("doi") or safe_url(s.get("url", ""))):
            kb.warn(where, "没有 DOI 或可访问链接，读者无法自行查证")
        for c in s.get("consulted") or []:
            if not (_nonempty(c.get("date")) and _nonempty(c.get("by")) and _nonempty(c.get("what"))):
                kb.err(where, "查阅记录需要 date、by、what")

    def cite_label(sid):
        s = kb.sources.get(sid)
        return None if s is None else (s.get("short") or sid)

    def node_title(nid):
        n = kb.nodes.get(nid)
        return None if n is None else n.get("title")

    for nid, n in kb.nodes.items():
        where = n["file"]
        if not ID_RE.match(nid):
            kb.err(where, f"ID 不合法：{nid!r}")
        for k in ("title", "purpose", "version", "updated"):
            if not _nonempty(n.get(k)):
                kb.err(where, f"缺少 {k}")
        if n.get("type") not in NODE_TYPES:
            kb.err(where, f"type 必须是 {'/'.join(NODE_TYPES)}")
        if n.get("status") not in STATUS:
            kb.err(where, f"status 必须是 {'/'.join(STATUS)}")
        parent = n.get("parent")
        if parent not in domains and parent not in kb.nodes:
            kb.err(where, f"父节点不存在（应为领域或另一个节点）：{parent!r}")
        for r in n.get("research") or []:
            if r not in lines:
                kb.err(where, f"研究线不存在：{r!r}")
        if not isinstance(n.get("keywords", []), list):
            kb.err(where, "keywords 必须是列表")
        for sid in n.get("sources") or []:
            if sid not in kb.sources:
                kb.err(where, f"来源不存在：{sid}")
        status = n.get("status")
        if status == "superseded":
            if n.get("replaced_by") not in kb.nodes:
                kb.err(where, "已替代节点必须填写存在的 replaced_by")
            if not _nonempty(n.get("migration")):
                kb.err(where, "已替代节点必须写 migration 迁移说明")
        if status != "candidate" and not n["body"].strip():
            kb.err(where, "除候选外，节点需要正文")

        res = theory_md.render(n["body"], node_url=lambda x: f"{x}.html" if x in kb.nodes else None,
                               node_title=node_title, cite_label=cite_label)
        kb.rendered[nid] = res
        for e in res.errors:
            kb.err(where, e)
        for pr in (n.get("prereq") or {}).values():
            for item in pr:
                for e in theory_md.render(item, node_url=lambda x: x if x in kb.nodes else None,
                                          node_title=node_title, cite_label=cite_label).errors:
                    kb.err(where, f"先修说明：{e}")

        if status == "verified":
            _check_verified(kb, nid, n, res)
        elif "unverified" in res.claims and status not in ("draft", "candidate", "needs-revision"):
            kb.err(where, "含“待核验”论述块，不能处于该状态")

    seen = set()
    for i, r in enumerate(kb.relations):
        rid = r.get("id") or f"#{i + 1}"
        where = f"关系 {rid}"
        if rid in seen:
            kb.err(where, "关系 ID 重复")
        seen.add(rid)
        for end in ("from", "to"):
            if r.get(end) not in kb.nodes:
                kb.err(where, f"{end} 节点不存在：{r.get(end)!r}")
        if r.get("from") == r.get("to"):
            kb.err(where, "起点和终点相同")
        if r.get("type") not in RELATIONS:
            kb.err(where, f"type 必须是 {'/'.join(RELATIONS)}")
        if not _nonempty(r.get("explanation")):
            kb.err(where, "必须写 explanation：这条联系具体是什么")
        if not _nonempty(r.get("condition")):
            kb.err(where, "必须写 condition；无条件时写“无额外条件”")
        if r.get("status") not in STATUS:
            kb.err(where, f"status 必须是 {'/'.join(STATUS)}")
        for sid in r.get("sources") or []:
            if sid not in kb.sources:
                kb.err(where, f"来源不存在：{sid}")
        if r.get("status") == "verified":
            if not r.get("sources"):
                kb.err(where, "已核验关系必须有来源")
            for sid in r.get("sources") or []:
                if sid in kb.sources and not kb.sources[sid].get("consulted"):
                    kb.err(where, f"来源 {sid} 尚无实际查阅记录，关系不能标为已核验")

    _check_prereq_cycles(kb)
    _check_tree(kb)

    for pid, p in kb.paths.items():
        where = p["file"]
        for k in ("title", "question", "general_question"):
            if not _nonempty(p.get(k)):
                kb.err(where, f"缺少 {k}")
        if not p.get("steps"):
            kb.err(where, "路径至少需要一步")
        for s in p.get("steps") or []:
            if s.get("node") not in kb.nodes:
                kb.err(where, f"步骤节点不存在：{s.get('node')!r}")
            if not _nonempty(s.get("why")):
                kb.err(where, f"步骤 {s.get('node')} 缺少 why")
        for b in p.get("branches") or []:
            if b.get("direction") not in DIRECTIONS:
                kb.err(where, f"分支方向必须是 {'/'.join(DIRECTIONS)}")
            if b.get("node") and b["node"] not in kb.nodes:
                kb.err(where, f"分支节点不存在：{b['node']!r}")
            if not (_nonempty(b.get("title")) and _nonempty(b.get("why"))):
                kb.err(where, "分支需要 title 和 why")

    for nid in kb.reviews:
        if nid not in kb.nodes:
            kb.err(f"knowledge/reviews/{nid}.json", "对应的节点不存在")
    return kb


def _check_tree(kb: KB) -> None:
    """Every node hangs off exactly one parent; following parents must reach a domain."""
    domains = kb.domain_map
    for nid, n in kb.nodes.items():
        seen, cur = [nid], n.get("parent")
        while cur in kb.nodes:
            if cur in seen:
                kb.err(n["file"], "父节点成环：" + " → ".join(seen + [cur]))
                break
            seen.append(cur)
            cur = kb.nodes[cur].get("parent")
        else:
            if cur not in domains and n.get("parent") in kb.nodes:
                kb.err(n["file"], f"沿父节点向上没有到达任何领域（停在 {cur!r}）")


def _check_verified(kb: KB, nid: str, n: dict, res) -> None:
    where = n["file"]
    if "unverified" in res.claims:
        kb.err(where, "已核验节点不能含“待核验”论述块")
    good = [r for r in kb.reviews.get(nid, [])
            if r.get("independent") is True and r.get("scope") and r.get("evidence") and _nonempty(r.get("method"))]
    if not good:
        kb.err(where, "标为已核验，但没有 independent=true 且写明 scope、method、evidence 的核验记录")
    cited = list(dict.fromkeys((n.get("sources") or []) + res.cites))
    if not cited:
        kb.err(where, "已核验节点必须引用来源")
    for sid in cited:
        if sid in kb.sources and not kb.sources[sid].get("consulted"):
            kb.err(where, f"来源 {sid} 尚无实际查阅记录，不能支撑已核验内容")


def _check_prereq_cycles(kb: KB) -> None:
    graph: dict = {}
    for r in kb.relations:
        if r.get("type") == "prerequisite" and r.get("from") in kb.nodes and r.get("to") in kb.nodes:
            graph.setdefault(r["from"], []).append(r["to"])
    state: dict = {}
    reported = set()

    def visit(u, stack):
        state[u] = 1
        stack.append(u)
        for v in graph.get(u, []):
            if state.get(v) == 1:
                cyc = stack[stack.index(v):] + [v]
                key = frozenset(cyc)
                if key not in reported:
                    reported.add(key)
                    kb.err("knowledge/relations.json", "先修关系成环：" + " → ".join(cyc))
            elif not state.get(v):
                visit(v, stack)
        stack.pop()
        state[u] = 2

    for u in sorted(graph):
        if not state.get(u):
            visit(u, [])


# ---------------------------------------------------------------------------
# rendering helpers
# ---------------------------------------------------------------------------
def _pill(status: str) -> str:
    label = STATUS.get(status, (status, ""))[0]
    return f'<span class="status status-{esc(status)}">{esc(label)}</span>'


def _node_href(prefix: str, nid: str) -> str:
    return f"{prefix}nodes/{quote(nid)}.html"


def _node_link(kb: KB, nid: str, prefix: str) -> str:
    n = kb.nodes[nid]
    cls = "node-link" + (" is-candidate" if n.get("status") == "candidate" else "")
    hint = "（候选，还没有正文）" if n.get("status") == "candidate" else ""
    return (f'<a class="{cls}" href="{_node_href(prefix, nid)}">{esc(n["title"])}</a>'
            + (f'<span class="visually-hidden">{hint}</span>' if hint else ""))


def _research_tags(kb: KB, n: dict, prefix: str) -> str:
    lines = kb.line_map
    tags = [f'<a class="rline" href="{prefix}tree.html?line={quote(r)}">{esc(lines[r]["title"])}</a>'
            for r in n.get("research") or [] if r in lines]
    return f'<span class="rlines">研究线：{"".join(tags)}</span>' if tags else ""


def _source_href(s: dict) -> str:
    if s.get("doi"):
        return "https://doi.org/" + quote(s["doi"], safe="/:.()-_;")
    return safe_url(s.get("url", ""))


def _inline(kb: KB, text: str, prefix: str) -> str:
    """Render a single line (prereq item, branch text) with links resolved for the page prefix."""
    res = theory_md.render(text, node_url=lambda x: _node_href(prefix, x) if x in kb.nodes else None,
                           node_title=lambda x: kb.nodes.get(x, {}).get("title"),
                           cite_label=lambda x: (kb.sources[x].get("short") or x) if x in kb.sources else None)
    h = res.html
    if h.startswith("<p>") and h.endswith("</p>"):
        h = h[3:-4]
    return h


def _page(kb: KB, *, title: str, prefix: str, body: str, page: str, extra_attrs: str = "",
          description: str = "") -> str:
    katex = ""
    if 'class="math"' in body:
        katex = (f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.css" '
                 f'integrity="{KATEX_CSS_SRI}" crossorigin="anonymous">\n'
                 f'<script defer src="https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.js" '
                 f'integrity="{KATEX_JS_SRI}" crossorigin="anonymous"></script>\n')
    desc = esc(description or "科研雷达理论地图：围绕真实问题，按需生长的知识结构。")
    return f"""<!doctype html>
<html lang="zh-CN" data-theme="auto">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1a2130" media="(prefers-color-scheme: dark)">
<title>{esc(title)} · 理论地图 · 科研雷达</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{prefix}assets/theory.css">
{katex}<script defer src="{prefix}assets/search-index.js"></script>
<script defer src="{prefix}assets/theory.js"></script>
</head>
<body data-page="{esc(page)}" data-prefix="{esc(prefix)}"{extra_attrs}>
<a class="skip" href="#main">跳到正文</a>
<header class="top">
  <a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true"></span><span class="brand-text"><span class="brand-name">理论地图</span><span class="brand-sub">科研雷达</span></span></a>
  <div class="search" role="search">
    <label class="visually-hidden" for="theorySearch">搜索节点</label>
    <input id="theorySearch" type="search" placeholder="搜索概念、方法或问题…" autocomplete="off" aria-controls="searchResults" aria-expanded="false" aria-autocomplete="list">
    <kbd aria-hidden="true">/</kbd>
    <ul id="searchResults" class="search-results" role="listbox" aria-label="搜索结果" hidden></ul>
  </div>
  <nav class="top-nav" aria-label="站点">
    <a href="{prefix}tree.html"{' aria-current="page"' if page == 'tree' else ''}>知识树</a>
    <a href="{prefix}guide.html"{' aria-current="page"' if page == 'guide' else ''}>内容规则</a>
    <a href="{prefix}../index.html">论文雷达</a>
    <button class="icon-btn" type="button" data-action="theme" aria-label="切换深浅色" title="切换深浅色">◐</button>
  </nav>
</header>
{body}
<footer class="foot">
  <p>草稿与候选内容未经核验，只是整理中的思路。正式结论以“已核验”节点及其核验范围为准。</p>
  <p>你的疑问、笔记和自评只保存在这台设备的浏览器里，不会上传。<button type="button" class="link-btn" data-action="export">导出备份</button><button type="button" class="link-btn" data-action="import">从备份恢复</button></p>
  <input type="file" id="importFile" accept="application/json,.json" hidden>
</footer>
<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------
def _paths_with(kb: KB, nid: str) -> list:
    return [p for p in kb.paths.values() if any(s.get("node") == nid for s in p.get("steps") or [])]


def _relation_items(kb: KB, nid: str, prefix: str) -> str:
    rows = []
    for r in kb.relations:
        if nid not in (r.get("from"), r.get("to")):
            continue
        tag, tmpl, _sym = RELATIONS[r["type"]]

        def name(x):
            if x == nid:
                return '<strong class="self">本节点</strong>'
            return f'<a class="node-link" href="{_node_href(prefix, x)}">{esc(kb.nodes[x]["title"])}</a>'

        sentence = tmpl.format(a=name(r["from"]), b=name(r["to"]))
        srcs = ""
        if r.get("sources"):
            srcs = '<p class="rel-src">依据：' + "、".join(
                f'<a href="#src-{esc(s)}">{esc(kb.sources[s].get("short") or s)}</a>' for s in r["sources"]) + "</p>"
        rows.append(
            f'<li class="rel rel-{esc(r["type"])}"><p class="rel-head"><span class="rel-tag">{esc(tag)}</span>{_pill(r["status"])}</p>'
            f'<p class="rel-sentence">{sentence}</p>'
            f'<p class="rel-expl">{esc(r["explanation"])}</p>'
            f'<p class="rel-cond"><span>成立条件</span>{esc(r["condition"])}</p>{srcs}</li>')
    if not rows:
        return '<p class="empty">还没有记录与其他节点的关系。</p>'
    return '<ul class="rel-list">' + "".join(rows) + "</ul>"


def _source_items(kb: KB, sids: list) -> str:
    if not sids:
        return '<p class="empty">还没有列出来源。</p>'
    rows = []
    for sid in sids:
        s = kb.sources[sid]
        href = _source_href(s)
        cit = esc(s.get("citation", ""))
        if href:
            cit = f'<a href="{esc(href)}" rel="noopener" target="_blank">{cit}</a>'
        meta = []
        if s.get("version"):
            meta.append(f"版本：{esc(s['version'])}")
        if s.get("locator"):
            meta.append(f"位置：{esc(s['locator'])}")
        consulted = s.get("consulted") or []
        if consulted:
            c = consulted[-1]
            state = f'<p class="src-state ok">已查阅（{esc(c["date"])}，{esc(c["by"])}）：{esc(c["what"])}</p>'
        else:
            state = '<p class="src-state todo">尚未实际查阅，目前只是拟查阅书目</p>'
        note = f'<p class="src-note">{esc(s["note"])}</p>' if s.get("note") else ""
        rows.append(f'<li id="src-{esc(sid)}"><p class="src-kind">{esc(SOURCE_KINDS.get(s.get("kind"), ""))}'
                    f'<span class="src-short">{esc(s.get("short") or sid)}</span></p><p class="src-cit">{cit}</p>'
                    + (f'<p class="src-meta">{"；".join(meta)}</p>' if meta else "") + note + state + "</li>")
    return '<ol class="src-list">' + "".join(rows) + "</ol>"


def _review_items(kb: KB, nid: str, n: dict) -> str:
    out = []
    reviews = kb.reviews.get(nid, [])
    if reviews:
        items = []
        for r in reviews:
            kind = ("独立核验" if r.get("independent") is True
                    else "生成模型自查，不计为核验")
            scope = "".join(f"<li>{esc(x)}</li>" for x in r.get("scope") or [])
            evidence = "".join(f"<li>{esc(x)}</li>" for x in r.get("evidence") or [])
            issues = "".join(f"<li>{esc(x)}</li>" for x in r.get("open_issues") or [])
            items.append(
                f'<li><p class="rev-head"><span>{esc(r.get("date", ""))}</span><span>{esc(r.get("reviewer", ""))}</span>'
                f'<span class="rev-kind{" ok" if r.get("independent") is True else ""}">{kind}</span></p>'
                + (f'<p class="rev-label">核对了什么</p><ul>{scope}</ul>' if scope else "")
                + (f'<p class="rev-label">方法</p><p>{esc(r.get("method", ""))}</p>' if r.get("method") else "")
                + (f'<p class="rev-label">证据</p><ul>{evidence}</ul>' if evidence else "")
                + (f'<p class="rev-label">尚未解决</p><ul>{issues}</ul>' if issues else "")
                + "</li>")
        out.append('<ul class="rev-list">' + "".join(items) + "</ul>")
    else:
        out.append('<p class="empty">暂无核验记录。</p>')
    log = n.get("changelog") or []
    if log:
        out.append('<p class="rev-label">修订记录</p><ul class="changelog">' + "".join(
            f'<li><span>v{esc(c.get("version", ""))}</span><span>{esc(c.get("date", ""))}</span>{esc(c.get("note", ""))}</li>'
            for c in log) + "</ul>")
    return "".join(out)


def _issue_link(n: dict) -> str:
    title = f"[理论地图纠错] {n['title']}（{n['id']} v{n.get('version', '')}）"
    body = ("节点：" + n["id"] + "\n版本：v" + str(n.get("version", "")) +
            "\n\n哪一处有问题（小节或原句）：\n\n为什么有问题、依据是什么：\n\n建议怎么改：\n")
    return f"{REPO_URL}/issues/new?title={quote(title)}&body={quote(body)}"


def _personal_panel(nid: str) -> str:
    dims = []
    for key, label in DIMENSIONS:
        opts = "".join(f'<option value="{v}">{esc(t)}</option>' for v, t in DIM_STATES)
        dims.append(
            f'<div class="dim"><label for="dim-{key}">{esc(label)}</label>'
            f'<select id="dim-{key}" data-dim="{key}">{opts}</select>'
            f'<input type="text" data-dim-note="{key}" aria-label="{esc(label)}：我的说明" placeholder="说明（可选）…"></div>')
    return f"""<section class="mine" id="mine" aria-labelledby="mineTitle" data-node="{esc(nid)}">
  <div class="mine-head"><h2 id="mineTitle">我的理解</h2><span class="save-state" id="saveState" aria-live="polite">只保存在这台设备</span></div>
  <label class="field-label" for="myQuestion">我还没想通的地方</label>
  <textarea id="myQuestion" rows="3" placeholder="写下读到这里的疑问，首页会列出未解决的疑问…"></textarea>
  <label class="field-label" for="myNote">我的笔记</label>
  <textarea id="myNote" rows="4" placeholder="用自己的话复述，或记下推导中卡住的一步…"></textarea>
  <fieldset class="dims"><legend>自评（读过不等于掌握，按需填写）</legend>{''.join(dims)}</fieldset>
  <label class="check"><input type="checkbox" id="resolved"> 疑问已解决</label>
</section>"""


def render_node(kb: KB, nid: str) -> str:
    n = kb.nodes[nid]
    prefix = "../"
    res = theory_md.render(
        n["body"], node_url=lambda x: _node_href(prefix, x) if x in kb.nodes else None,
        node_title=lambda x: kb.nodes.get(x, {}).get("title"),
        cite_label=lambda x: (kb.sources[x].get("short") or x) if x in kb.sources else None)
    domains = kb.domain_map
    chain = kb.ancestors(nid)
    domain = domains.get(chain[0], {"id": "", "title": ""}) if chain else {"id": "", "title": ""}
    status = n.get("status", "draft")
    s_label, s_text = STATUS[status]
    banner = ""
    if status != "verified":
        extra = ""
        if status == "superseded" and n.get("replaced_by") in kb.nodes:
            extra = (f' 请转到 <a href="{_node_href(prefix, n["replaced_by"])}">{esc(kb.nodes[n["replaced_by"]]["title"])}</a>。'
                     f'{esc(n.get("migration", ""))}')
        banner = f'<div class="banner banner-{esc(status)}" role="note"><strong>{esc(s_label)}</strong>{esc(s_text)}{extra}</div>'
    else:
        banner = f'<div class="banner banner-verified" role="note"><strong>{esc(s_label)}</strong>{esc(s_text)}核验范围见右侧“核验与修订”。</div>'

    meta = (f'<p class="node-meta"><span class="type">{esc(NODE_TYPES[n["type"]][0])}节点</span>'
            f'<span>领域：<a href="../tree.html#t-{esc(domain["id"])}">{esc(domain["title"])}</a></span>'
            + _research_tags(kb, n, prefix)
            + f'<span>v{esc(n.get("version", ""))} · {esc(n.get("updated", ""))}</span></p>')

    pre = n.get("prereq") or {}
    pre_html = ""
    if pre.get("intuitive") or pre.get("full"):
        cols = []
        for key, label in (("intuitive", "直观阅读需要"), ("full", "完整推导还需要")):
            items = pre.get(key) or []
            if items:
                cols.append(f'<div><p class="pre-label">{label}</p><ul>' +
                            "".join(f"<li>{_inline(kb, x, prefix)}</li>" for x in items) + "</ul></div>")
        pre_html = ('<section class="prereq" aria-label="已有认识与必要先修">' + "".join(cols) +
                    '<p class="pre-hint">只是提示，不需要先读完才能往下看。</p></section>')

    layers_used = [t["layer"] for t in res.toc if t.get("layer")]
    layer_bar = ""
    if layers_used:
        btns = ['<button type="button" data-layer-filter="" aria-pressed="true">连续阅读</button>']
        for key, label in LAYERS.items():
            if key in layers_used:
                btns.append(f'<button type="button" data-layer-filter="{key}" aria-pressed="false">'
                            f'<span class="layer-dot layer-{key}" aria-hidden="true"></span>只看{esc(label)}</button>')
        layer_bar = ('<div class="layer-bar" role="group" aria-label="阅读层次">' + "".join(btns) + "</div>")

    toc = "".join(
        f'<li><a href="#{t["id"]}">{esc(t["title"])}</a>'
        + (f'<span class="layer-dot layer-{t["layer"]}" title="{esc(LAYERS[t["layer"]])}"></span>' if t.get("layer") else "")
        + "</li>" for t in res.toc)

    # path context + prev/next
    path_blocks, pager = [], []
    for p in _paths_with(kb, nid):
        steps = p["steps"]
        idx = next(i for i, s in enumerate(steps) if s["node"] == nid)
        lis = []
        for i, s in enumerate(steps):
            sn = kb.nodes[s["node"]]
            cur = ' aria-current="page"' if s["node"] == nid else ""
            lis.append(f'<li><a href="{_node_href(prefix, s["node"])}"{cur}>{esc(sn["title"])}</a></li>')
        path_blocks.append(f'<div class="rail-block"><p class="rail-label">所在路径</p>'
                           f'<a class="path-link" href="../paths/{quote(p["id"])}.html">{esc(p["title"])}</a>'
                           f'<ol class="path-steps">{"".join(lis)}</ol></div>')
        prev_ = steps[idx - 1]["node"] if idx > 0 else None
        next_ = steps[idx + 1]["node"] if idx + 1 < len(steps) else None
        cells = []
        cells.append(f'<a class="pager-prev" href="{_node_href(prefix, prev_)}"><span>上一步</span>{esc(kb.nodes[prev_]["title"])}</a>'
                     if prev_ else f'<a class="pager-prev" href="../paths/{quote(p["id"])}.html"><span>回到路径</span>{esc(p["title"])}</a>')
        cells.append(f'<a class="pager-next" href="{_node_href(prefix, next_)}"><span>下一步</span>{esc(kb.nodes[next_]["title"])}</a>'
                     if next_ else f'<a class="pager-next" href="../paths/{quote(p["id"])}.html#branches"><span>读完了</span>选下一个方向</a>')
        pager.append(f'<nav class="pager" aria-label="路径内导航：{esc(p["title"])}">{"".join(cells)}</nav>')

    sids = list(dict.fromkeys((n.get("sources") or []) + [c for c in res.cites if c in kb.sources]
                              + [s for r in kb.relations if nid in (r.get("from"), r.get("to"))
                                 for s in r.get("sources") or [] if s in kb.sources]))

    # where this node sits in the tree
    trail = [f'<li><a href="../tree.html#t-{esc(domain["id"])}">{esc(domain["title"])}</a></li>']
    trail += [f'<li>{_node_link(kb, x, prefix)}</li>' for x in chain[1:]]
    trail.append(f'<li aria-current="page">{esc(n["title"])}</li>')
    kids = kb.children(nid)
    tree_block = (f'<div class="rail-block"><p class="rail-label">在知识树中的位置</p>'
                  f'<ol class="tree-trail">{"".join(trail)}</ol>'
                  f'<a class="small" href="../tree.html#t-{esc(nid)}">在整棵树里看</a></div>')

    children_html = ""
    if kids:
        children_html = ('<section class="node-children" aria-labelledby="kidsTitle"><h2 id="kidsTitle">子条目</h2><ul>'
                         + "".join(f'<li>{_node_link(kb, k, prefix)}<span class="kid-purpose">{esc(kb.nodes[k]["purpose"])}</span></li>'
                                   for k in kids) + "</ul></section>")
    related = []
    for x in ([chain[-1]] if len(chain) > 1 else []) + [
            r["to"] if r["from"] == nid else r["from"] for r in kb.relations if nid in (r.get("from"), r.get("to"))]:
        if x in kb.nodes and x != nid and x not in related and x not in kids:
            related.append(x)
    related_html = ('<p class="related"><span>相关条目</span>' + "、".join(_node_link(kb, x, prefix) for x in related) + "</p>"
                    if related else "")
    refs_html = (f'<section class="refs" aria-labelledby="refsTitle"><h2 id="refsTitle">参考资料</h2>{_source_items(kb, sids)}</section>'
                 if sids else "")
    line_names = [kb.line_map[r]["title"] for r in n.get("research") or [] if r in kb.line_map]
    footer = (f'<p class="cat-foot"><span>分类</span>{esc(domain["title"])} · {esc(NODE_TYPES[n["type"]][0])}'
              + (" · 研究线：" + "、".join(esc(x) for x in line_names) if line_names else "")
              + f' · 状态：{esc(s_label)}</p>')

    left = (f'<details class="rail rail-left" data-rail open><summary>位置、路径与目录</summary>'
            + tree_block
            + "".join(path_blocks)
            + (f'<div class="rail-block"><p class="rail-label">本页目录</p><ol class="toc">{toc}</ol></div>' if toc else "")
            + '<p class="resume hidden" id="resume"></p></details>')
    right = (f'<details class="rail rail-right" data-rail open><summary>关联与核验</summary>'
             f'<div class="rail-block"><h2 class="rail-label">关联</h2>{_relation_items(kb, nid, prefix)}</div>'
             f'<div class="rail-block"><h2 class="rail-label">核验与修订</h2>{_review_items(kb, nid, n)}</div>'
             f'<div class="rail-block"><h2 class="rail-label">发现问题</h2><p class="small">在 GitHub 上公开提交纠错，会附上节点编号和版本，不含你的笔记。</p>'
             f'<a class="btn" href="{esc(_issue_link(n))}" rel="noopener" target="_blank">提交纠错</a></div></details>')

    body_html = res.html or '<p class="empty">这是候选节点，还没有正文。上面写了它打算讲什么，下面是它在树里的邻居。</p>'
    crumbs = "".join(f'<span aria-hidden="true">/</span>{_node_link(kb, x, prefix)}' for x in chain[1:])
    main = f"""<div class="reader-shell" id="main">
{left}
<article class="node" aria-labelledby="nodeTitle">
  <nav class="crumbs" aria-label="当前位置"><a href="../index.html">理论地图</a><span aria-hidden="true">/</span><a href="../tree.html#t-{esc(domain['id'])}">{esc(domain['title'])}</a>{crumbs}</nav>
  <h1 id="nodeTitle">{esc(n['title'])}</h1>
  {meta}
  {banner}
  <p class="purpose">{esc(n['purpose'])}</p>
  {pre_html}
  {layer_bar}
  <div class="prose" id="prose">
{body_html}
  </div>
  {children_html}
  {related_html}
  {refs_html}
  {footer}
  {''.join(pager)}
  {_personal_panel(nid)}
</article>
{right}
<button type="button" class="rail-toggle" data-action="toggle-rails" aria-pressed="false">收起侧栏</button>
</div>"""
    attrs = (f' data-node="{esc(nid)}" data-node-title="{esc(n["title"])}" data-status="{esc(status)}"')
    return _page(kb, title=n["title"], prefix=prefix, body=main, page="node", extra_attrs=attrs,
                 description=n["purpose"])


def _step_list(kb: KB, p: dict, prefix: str, detailed: bool) -> str:
    lis = []
    for s in p.get("steps") or []:
        sn = kb.nodes[s["node"]]
        why = f'<p class="step-why">{_inline(kb, s["why"], prefix)}</p>' if detailed else ""
        purpose = f'<p class="step-purpose">{esc(sn["purpose"])}</p>' if detailed else ""
        lis.append(f'<li data-node="{esc(s["node"])}"><a href="{_node_href(prefix, s["node"])}">{esc(sn["title"])}</a>'
                   f'{_pill(sn.get("status", ""))}{why}{purpose}</li>')
    return f'<ol class="steps">{"".join(lis)}</ol>'


def _branches(kb: KB, p: dict, prefix: str) -> str:
    groups = []
    for key, (label, hint) in DIRECTIONS.items():
        items = [b for b in p.get("branches") or [] if b.get("direction") == key]
        if not items:
            continue
        lis = []
        for b in items:
            title = esc(b["title"])
            if b.get("node") in kb.nodes:
                title = f'<a href="{_node_href(prefix, b["node"])}">{title}</a>{_pill(kb.nodes[b["node"]].get("status", ""))}'
            lis.append(f'<li><p class="branch-title">{title}</p><p class="branch-why">{_inline(kb, b["why"], prefix)}</p></li>')
        groups.append(f'<div class="branch-group dir-{key}"><p class="dir-label">{esc(label)}</p>'
                      f'<p class="dir-hint">{esc(hint)}</p><ul>{"".join(lis)}</ul></div>')
    return '<div class="branches">' + "".join(groups) + "</div>"


def render_path(kb: KB, pid: str) -> str:
    p = kb.paths[pid]
    prefix = "../"
    goals = "".join(f"<li>{_inline(kb, g, prefix)}</li>" for g in p.get("goals") or [])
    base = "".join(f"<li>{_inline(kb, b, prefix)}</li>" for b in p.get("base") or [])
    body = f"""<main class="page" id="main">
  <nav class="crumbs" aria-label="当前位置"><a href="../index.html">理论地图</a><span aria-hidden="true">/</span><span>学习路径</span></nav>
  <h1>{esc(p['title'])}</h1>
  {_pill(p.get('status', 'draft'))}
  <figure class="question"><blockquote><p>{esc(p['question'])}</p></blockquote><figcaption>原始提问</figcaption></figure>
  <p class="general"><span>提炼出的通用问题</span>{esc(p['general_question'])}</p>
  {'<section class="block"><h2>适用基础</h2><ul>' + base + '</ul></section>' if base else ''}
  <section class="block"><h2>建议阅读顺序</h2>{_step_list(kb, p, prefix, True)}<p class="small">顺序只是建议，可以随时跳到任何节点。</p></section>
  {'<section class="block"><h2>读完后应能做到</h2><ul>' + goals + '</ul></section>' if goals else ''}
  <section class="block" id="branches"><h2>下一步可以往哪走</h2>{_branches(kb, p, prefix)}</section>
</main>"""
    return _page(kb, title=p["title"], prefix=prefix, body=body, page="path",
                 extra_attrs=f' data-path="{esc(pid)}"', description=p["general_question"])


def _node_card(kb: KB, nid: str, prefix: str) -> str:
    n = kb.nodes[nid]
    return (f'<li class="node-card st-{esc(n.get("status", ""))}"><a href="{_node_href(prefix, nid)}">{esc(n["title"])}</a>'
            f'<span class="nc-meta">{esc(NODE_TYPES[n["type"]][0])}{_pill(n.get("status", ""))}</span>'
            f'<p>{esc(n["purpose"])}</p></li>')


def _counts(kb: KB, ids) -> dict:
    c = {"total": 0, "verified": 0, "draft": 0, "candidate": 0, "needs-revision": 0}
    for x in ids:
        c["total"] += 1
        st = kb.nodes[x].get("status", "")
        if st in c:
            c[st] += 1
    return c


def _count_text(c: dict) -> str:
    written = c["verified"] + c["draft"] + c["needs-revision"]
    return f'{c["total"]} 条' + (f"，已写 {written}" if written else "")


def render_index(kb: KB) -> str:
    prefix = ""
    root = kb.meta or {}
    allc = _counts(kb, kb.nodes)
    junctions = sum(1 for n in kb.nodes.values() if n.get("research"))

    rows = []
    for d in kb.domains:
        kids = kb.children(d["id"])
        sub = []
        for k in kids:
            grand = kb.subtree(k)
            extra = f'<span class="sub-n">（{len(grand)}）</span>' if grand else ""
            star = '<span class="rmark" title="研究交汇点" aria-label="研究交汇点">★</span>' if kb.nodes[k].get("research") else ""
            sub.append(f"{_node_link(kb, k, prefix)}{star}{extra}")
        c = _counts(kb, kb.subtree(d["id"]))
        rows.append(
            f'<tr id="d-{esc(d["id"])}"><th scope="row"><a href="tree.html#t-{esc(d["id"])}">{esc(d["title"])}</a>'
            f'<span class="dom-sum">{esc(d["summary"])}</span><span class="dom-n">{esc(_count_text(c))}</span></th>'
            f'<td>{" · ".join(sub) if sub else "<span class=small>还没有条目</span>"}</td></tr>')
    domain_table = ('<div class="table-wrap domain-table" tabindex="0"><table><thead><tr>'
                    '<th scope="col">领域</th><th scope="col">子主题</th></tr></thead>'
                    f'<tbody>{"".join(rows)}</tbody></table></div>')

    line_items = []
    for r in kb.research_lines:
        hits = [x for x, n in kb.nodes.items() if r["id"] in (n.get("research") or [])]
        doms = list(dict.fromkeys(kb.domain_map[kb.domain_of(x)]["title"] for x in sorted(hits, key=lambda x: kb.nodes[x]["title"])))
        where = ("，落在" + "、".join(esc(x) for x in doms)) if doms else ""
        line_items.append(f'<li><a class="rline" href="tree.html?line={quote(r["id"])}">{esc(r["title"])}</a>'
                          f'<span class="small">{len(hits)} 个交汇点{where}</span></li>')

    path_items = "".join(
        f'<li><a href="paths/{quote(p["id"])}.html">{esc(p["title"])}</a>{_pill(p.get("status", "draft"))}'
        f'<span class="small">{esc(p.get("general_question", ""))}</span></li>'
        for p in kb.paths.values())

    written = sorted((x for x, n in kb.nodes.items() if n.get("status") in ("verified", "draft", "needs-revision")),
                     key=lambda x: (kb.nodes[x]["status"] != "verified", kb.nodes[x]["title"]))
    verified = [x for x in written if kb.nodes[x]["status"] == "verified"]
    unverified = [x for x in written if kb.nodes[x]["status"] != "verified"]
    verified_html = ("<ul class='cards'>" + "".join(_node_card(kb, x, prefix) for x in verified) + "</ul>" if verified
                     else '<p class="empty">还没有已核验的节点。下面的草稿完成来源和推导核查后，会移到这里。</p>')
    draft_html = ""
    if unverified:
        draft_html = (f'<details class="pending"><summary>草稿（{len(unverified)} 个，未核验，单独列出）</summary>'
                      "<ul class='cards'>" + "".join(_node_card(kb, x, prefix) for x in unverified) + "</ul></details>")

    stats = (f'<ul class="stats" aria-label="收录情况">'
             f'<li><b>{allc["total"]}</b>条目</li><li><b>{allc["verified"]}</b>已核验</li>'
             f'<li><b>{allc["draft"] + allc["needs-revision"]}</b>草稿</li><li><b>{allc["candidate"]}</b>候选</li>'
             f'<li><b>{junctions}</b>研究交汇点</li></ul>')

    body = f"""<main class="home" id="main">
  <section class="home-intro" aria-labelledby="homeTitle">
    <h1 id="homeTitle">{esc(root.get("title") or "理论地图")}</h1>
    <p class="lede">{esc(root.get("intro") or "")}</p>
    {stats}
    <p class="small">候选条目只有题目和范围，还没有正文；<a href="tree.html">知识树</a>里能一眼看到哪些已经写了。★ 是和研究线交汇的条目。</p>
  </section>

  <section class="domains" aria-labelledby="domTitle">
    <h2 id="domTitle">按领域浏览</h2>
    {domain_table}
  </section>

  <div class="home-grid">
    <section class="lines" aria-labelledby="linesTitle">
      <h2 id="linesTitle">研究线</h2>
      <p class="small">研究方向不是分类，而是知识长到那里时碰到的地方。点开会在整棵树上标出交汇点和离它几步远的条目。</p>
      <ul class="line-list">{"".join(line_items)}</ul>
      {'<h2>学习路线</h2><ul class="line-list">' + path_items + '</ul>' if path_items else ''}
    </section>
    <aside class="continue" aria-label="继续学习">
      <section><h2>最近读过</h2><ul class="mini" id="recentList"><li class="empty">还没有阅读记录。</li></ul></section>
      <section><h2>还没想通的</h2><ul class="mini" id="openQuestions"><li class="empty">在节点页“我的理解”里写下的疑问会出现在这里。</li></ul></section>
    </aside>
  </div>

  <section class="directory" aria-labelledby="dirTitle">
    <div class="sec-head"><h2 id="dirTitle">已核验节点</h2><p>正式学习内容。每个节点注明核验范围。</p></div>
    {verified_html}
    {draft_html}
  </section>
</main>"""
    return _page(kb, title="首页", prefix=prefix, body=body, page="home")


def _tree_outline(kb: KB, pid: str, prefix: str) -> str:
    kids = kb.children(pid)
    if not kids:
        return ""
    lis = []
    for k in kids:
        n = kb.nodes[k]
        star = '<span class="rmark" aria-label="研究交汇点">★</span>' if n.get("research") else ""
        lis.append(f'<li id="o-{esc(k)}" data-id="{esc(k)}" class="st-{esc(n.get("status", ""))}">'
                   f'{_node_link(kb, k, prefix)}{star}{_pill(n.get("status", ""))}{_tree_outline(kb, k, prefix)}</li>')
    return "<ul>" + "".join(lis) + "</ul>"


def tree_payload(kb: KB) -> dict:
    per_line = {r["id"]: kb.research_distance(r["id"]) for r in kb.research_lines}
    nodes = []
    for nid in sorted(kb.nodes):
        n = kb.nodes[nid]
        nodes.append({"id": nid, "title": n["title"], "parent": n["parent"], "status": n.get("status", ""),
                      "research": n.get("research") or [], "type": NODE_TYPES[n["type"]][0],
                      "purpose": n.get("purpose", ""),
                      "dist": {lid: d[nid] for lid, d in per_line.items() if nid in d}})
    order = {nid: i for i, nid in enumerate(x for d in kb.domains for x in [d["id"]] + _preorder(kb, d["id"]))}
    nodes.sort(key=lambda x: order.get(x["id"], 1 << 30))
    return {"root": (kb.meta or {}).get("title") or "理论地图",
            "domains": [{"id": d["id"], "title": d["title"], "summary": d["summary"]} for d in kb.domains],
            "lines": [{"id": r["id"], "title": r["title"]} for r in kb.research_lines],
            "nodes": nodes}


def _preorder(kb: KB, pid: str) -> list:
    out = []
    for k in kb.children(pid):
        out.append(k)
        out.extend(_preorder(kb, k))
    return out


def render_tree(kb: KB) -> str:
    prefix = ""
    allc = _counts(kb, kb.nodes)
    sections = []
    for d in kb.domains:
        c = _counts(kb, kb.subtree(d["id"]))
        sections.append(f'<details class="o-domain" id="t-{esc(d["id"])}" data-id="{esc(d["id"])}" open>'
                        f'<summary><span class="o-dtitle">{esc(d["title"])}</span><span class="small">{esc(_count_text(c))}</span></summary>'
                        f'<p class="small">{esc(d["summary"])}</p>{_tree_outline(kb, d["id"], prefix) or "<p class=small>还没有条目</p>"}</details>')
    options = "".join(f'<option value="{esc(r["id"])}">{esc(r["title"])}</option>' for r in kb.research_lines)
    payload = json.dumps(tree_payload(kb), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).replace("</", "<\\/")
    written = allc["verified"] + allc["draft"] + allc["needs-revision"]
    body = f"""<main class="page tree-page" id="main">
  <nav class="crumbs" aria-label="当前位置"><a href="index.html">理论地图</a><span aria-hidden="true">/</span><span>知识树</span></nav>
  <h1>知识树</h1>
  <p class="lede">全部 {allc["total"]} 个条目按学科从根部铺开，已写 {written} 个、候选 {allc["candidate"]} 个。父子关系是分类，不是先修。选一条研究线，可以看到它落在树的哪些位置，以及别的条目离它有几步。</p>
  <div class="tree-tools" role="group" aria-label="知识树视图" hidden>
    <div class="seg" role="group" aria-label="显示方式">
      <button type="button" data-tree-view="graph" aria-pressed="true">树形图</button>
      <button type="button" data-tree-view="outline" aria-pressed="false">大纲</button>
    </div>
    <label class="tool"><input type="checkbox" id="treeWritten"> 只看已写</label>
    <label class="tool">研究线 <select id="treeLine"><option value="">不标出</option>{options}</select></label>
    <button type="button" class="link-btn" data-tree-fold="open">全部展开</button>
    <button type="button" class="link-btn" data-tree-fold="close">全部收起</button>
  </div>
  <ul class="legend" aria-label="图例">
    <li><span class="lg lg-verified" aria-hidden="true"></span>已核验</li>
    <li><span class="lg lg-draft" aria-hidden="true"></span>草稿</li>
    <li><span class="lg lg-candidate" aria-hidden="true"></span>候选（只有题目）</li>
    <li><span class="rmark" aria-hidden="true">★</span>研究交汇点</li>
    <li class="lg-line"><span class="lg lg-near" aria-hidden="true"></span>选中研究线时：离交汇点 1–2 步</li>
  </ul>
  <p class="small" id="treeSummary" aria-live="polite"></p>
  <div class="tree-graph" id="treeGraph" hidden></div>
  <div class="tree-outline" id="treeOutline">{"".join(sections)}</div>
  <script type="application/json" id="treeData">{payload}</script>
</main>"""
    return _page(kb, title="知识树", prefix=prefix, body=body, page="tree",
                 description="理论地图的全部条目，按学科组织成一棵树，并标出与研究线的交汇点。")


def render_guide(kb: KB) -> str:
    prefix = ""

    def table(head, rows):
        th = "".join(f'<th scope="col">{esc(h)}</th>' for h in head)
        tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return f'<div class="table-wrap" tabindex="0"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

    status_rows = [[_pill(k), esc(v[1])] for k, v in STATUS.items()]
    type_rows = [[esc(v[0]), esc(v[1])] for v in NODE_TYPES.values()]
    rel_rows = [[esc(v[0]), esc(v[1].format(a="A", b="B"))] for v in RELATIONS.values()]
    claim_rows = [[f'<span class="claim-kind inline claim-{k}">{esc(v)}</span>'] for k, v in CLAIMS.items()]
    layer_rows = [[f'<span class="layer-dot layer-{k}"></span>{esc(v)}'] for k, v in LAYERS.items()]
    dir_rows = [[esc(v[0]), esc(v[1])] for v in DIRECTIONS.values()]
    body = f"""<main class="page" id="main">
  <h1>内容规则</h1>
  <p class="lede">这张地图优先保证少量节点的质量、推导和连接理由，再扩大覆盖面。下面是读页面时需要知道的约定。</p>
  <section class="block"><h2>内容状态</h2>{table(["状态", "含义"], status_rows)}
    <p>首页目录只列已写的条目：已核验的在前，草稿单独折叠并在页面顶部提示。候选条目只出现在领域表和知识树里。</p></section>
  <section class="block"><h2>知识树与研究线</h2>
    <ul><li>条目按学科组织成一棵树：根下是领域（数学工具、量子力学、电子结构……），每个条目只有一个父条目。父子关系只表示“属于哪一块”，不表示必须先读。</li>
    <li>研究线（晶体结构生成、压电与响应计算等）不是分类。条目的内容碰到某条研究线时才打上标记（★），所以研究方向是树铺开时自然出现的交汇点。</li>
    <li>跨领域的联系用“关联”表达，写明联系是什么、在什么条件下成立；它们不改变树的形状。</li>
    <li>候选条目只有题目和范围，用来先占住位置，正文写好并检查后才变成草稿。</li></ul></section>
  <section class="block"><h2>什么才算核验</h2>
    <ul><li>关键论述有直接支持的来源，并且来源确实被查阅过（页面会写明查阅日期和核对的位置）。</li>
    <li>主要公式的符号、假设、单位和关键步骤写明；关键推导经过独立重建，可计算的例子做过解析或数值交叉检查。</li>
    <li>类比没有越界，特例没有写成一般结论。</li>
    <li>仅由生成模型复查自己写的文字，不算独立核验，页面会标为“生成模型自查，不计为核验”。</li></ul></section>
  <section class="block"><h2>论述类型</h2><p>正文用带文字标签的块区分不同性质的说法：</p>{table(["标签"], claim_rows)}</section>
  <section class="block"><h2>阅读层次</h2><p>默认连续阅读。也可以只看某一层：</p>{table(["层次"], layer_rows)}</section>
  <section class="block"><h2>节点类型</h2>{table(["类型", "用途"], type_rows)}</section>
  <section class="block"><h2>关系类型</h2><p>每条关系都写明联系是什么、在什么条件下成立。分类上的父节点不等于先修；横向相连不等于等价。</p>{table(["标签", "读法"], rel_rows)}</section>
  <section class="block"><h2>扩展方向</h2>{table(["方向", "适用情形"], dir_rows)}<p>先修只做提示，不锁内容；可以随时换方向，也可以先把疑问留着。</p></section>
  <section class="block"><h2>你的记录</h2><p>疑问、笔记、自评和阅读位置保存在这台设备浏览器的本地存储里，不会上传，也不会出现在公开仓库。换浏览器或清除网站数据会丢失，请定期用页面底部的“导出备份”保存一份 JSON。</p></section>
</main>"""
    return _page(kb, title="内容规则", prefix=prefix, body=body, page="guide")


def search_index(kb: KB) -> str:
    domains = kb.domain_map
    lines = kb.line_map
    nodes = []
    for nid in sorted(kb.nodes):
        n = kb.nodes[nid]
        res = kb.rendered.get(nid)
        text = (res.text if res else "")[:1200]
        nodes.append({
            "id": nid, "title": n["title"], "type": NODE_TYPES.get(n.get("type"), ("", ""))[0],
            "domain": domains.get(kb.domain_of(nid), {}).get("title", ""), "status": n.get("status"),
            "lines": [lines[r]["title"] for r in n.get("research") or [] if r in lines],
            "keywords": n.get("keywords") or [],
            "statusLabel": STATUS.get(n.get("status"), ("", ""))[0], "purpose": n.get("purpose", ""),
            "text": text, "url": f"nodes/{nid}.html",
        })
    paths = [{"id": pid, "title": p["title"], "question": p.get("question", ""),
              "general": p.get("general_question", ""), "url": f"paths/{pid}.html",
              "steps": [s["node"] for s in p.get("steps") or []]}
             for pid, p in sorted(kb.paths.items())]
    payload = json.dumps({"nodes": nodes, "paths": paths}, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).replace("</", "<\\/")
    return "window.THEORY_INDEX=" + payload + ";\n"


def render_site(kb: KB) -> dict:
    out = {"index.html": render_index(kb), "tree.html": render_tree(kb), "guide.html": render_guide(kb),
           "assets/search-index.js": search_index(kb)}
    for nid in sorted(kb.nodes):
        out[f"nodes/{nid}.html"] = render_node(kb, nid)
    for pid in sorted(kb.paths):
        out[f"paths/{pid}.html"] = render_path(kb, pid)
    for f in sorted(ASSETS.iterdir()):
        if f.is_file():
            out[f"assets/{f.name}"] = f.read_text(encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# entry points
# ---------------------------------------------------------------------------
def build(root: Path | None = None, out_dir: Path | None = None) -> tuple:
    kb = validate(load(root))
    if kb.errors:
        return kb, []
    target = Path(out_dir or (kb.root / "theory"))
    files = render_site(kb)
    written = []
    for rel, content in files.items():
        p = target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists() or p.read_text(encoding="utf-8") != content:
            p.write_text(content, encoding="utf-8")
            written.append(rel)
    return kb, written


def check(root: Path | None = None, out_dir: Path | None = None) -> tuple:
    """Validate content and confirm the committed theory/ matches a fresh render."""
    kb = validate(load(root))
    drift = []
    if not kb.errors:
        target = Path(out_dir or (kb.root / "theory"))
        files = render_site(kb)
        for rel, content in files.items():
            p = target / rel
            if not p.exists():
                drift.append(f"缺少 theory/{rel}")
            elif p.read_text(encoding="utf-8") != content:
                drift.append(f"theory/{rel} 与内容源不一致")
        if target.exists():
            for p in sorted(target.rglob("*")):
                if p.is_file() and p.relative_to(target).as_posix() not in files:
                    drift.append(f"theory/{p.relative_to(target).as_posix()} 不再由内容源生成（请人工确认后再处理）")
    return kb, drift
