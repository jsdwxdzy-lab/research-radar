"""Offline, read-only junction finder for the theory map.

Reads knowledge/ and data.json, prints three lists, writes nothing:

1. 论文命中: recent papers whose radar topics belong to a research line and whose
   title/abstract mention a node's keywords. Tells you which entries the
   literature is currently pressing on.
2. 远距离同线对: two entries tagged with the same research line that sit in
   different branches of the tree and have no written relation. These are
   places where a link might exist but nobody has stated it; a paper that
   hits both makes the pair more interesting.
3. 未覆盖论文: line papers that match no entry at all, i.e. where the tree has
   not grown yet.

The output is raw material. Turning a pair into an idea (and checking whether
it is wrong) is a human or model judgement made elsewhere; ideas are kept in
the user's private notes, never in this repository.
"""
from __future__ import annotations

import json
import re
from itertools import combinations
from pathlib import Path

from . import theory


def _kw_regex(kw: str):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(kw) + r"(?![A-Za-z0-9])", re.I)


def _load_items(root: Path) -> list:
    p = root / "data.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("items") or []


def tree_gap(kb, a: str, b: str) -> int:
    """Number of tree edges between a and b (domains under one root)."""
    pa = ["__root"] + kb.ancestors(a) + [a]
    pb = ["__root"] + kb.ancestors(b) + [b]
    common = 0
    for x, y in zip(pa, pb):
        if x != y:
            break
        common += 1
    return (len(pa) - common) + (len(pb) - common)


def find(root: Path | None = None, *, since: str = "", min_gap: int = 4, limit: int = 12) -> dict:
    kb = theory.validate(theory.load(root))
    if kb.errors:
        return {"errors": [str(i) for i in kb.errors]}
    items = _load_items(kb.root)
    if since:
        items = [i for i in items if (i.get("d") or "") >= since]
    lines = kb.line_map
    topic_line = {t: lid for lid, r in lines.items() for t in r.get("radar_topics") or []}
    rx = {nid: [(k, _kw_regex(k)) for k in n.get("keywords") or []] for nid, n in kb.nodes.items()}

    hits, uncovered = [], {lid: [] for lid in lines}
    node_papers: dict = {}
    for it in items:
        its_lines = sorted({topic_line[t] for t in it.get("tp") or [] if t in topic_line})
        if not its_lines:
            continue
        text = f'{it.get("t", "")} {it.get("a", "")}'
        matched = {}
        for nid, pats in rx.items():
            ks = [k for k, r in pats if r.search(text)]
            if ks:
                matched[nid] = ks
        ref = {"key": it.get("k", ""), "title": it.get("t", ""), "title_zh": it.get("tz", ""),
               "date": it.get("d", ""), "url": it.get("u", ""), "lines": its_lines}
        if matched:
            hits.append(dict(ref, nodes=matched))
            for nid in matched:
                node_papers.setdefault(nid, []).append(ref["key"])
        else:
            for lid in its_lines:
                uncovered[lid].append(ref)

    related = {frozenset((r["from"], r["to"])) for r in kb.relations}
    pairs = []
    for lid in lines:
        tagged = sorted(x for x, n in kb.nodes.items() if lid in (n.get("research") or []))
        for a, b in combinations(tagged, 2):
            if frozenset((a, b)) in related or a in kb.ancestors(b) or b in kb.ancestors(a):
                continue
            gap = tree_gap(kb, a, b)
            if gap < min_gap:
                continue
            shared = sorted(set(node_papers.get(a, [])) & set(node_papers.get(b, [])))
            pairs.append({"line": lid, "a": a, "b": b, "gap": gap, "shared_papers": shared,
                          "a_domain": kb.domain_of(a), "b_domain": kb.domain_of(b),
                          "written": [x for x in (a, b) if kb.nodes[x].get("status") != "candidate"]})
    pairs.sort(key=lambda p: (-len(p["shared_papers"]), -len(p["written"]), -p["gap"], p["a"], p["b"]))

    pressure = sorted(((nid, len(v)) for nid, v in node_papers.items()), key=lambda x: (-x[1], x[0]))
    return {"since": since, "papers_considered": len(items), "hits": hits, "pressure": pressure,
            "pairs": pairs[:limit], "pairs_total": len(pairs),
            "uncovered": {lid: v[:limit] for lid, v in uncovered.items()},
            "uncovered_total": {lid: len(v) for lid, v in uncovered.items()}}


def format_text(res: dict, kb_titles: dict, line_titles: dict) -> str:
    if res.get("errors"):
        return "内容源有错误，先修好再找交汇：\n" + "\n".join(res["errors"])
    t = lambda x: kb_titles.get(x, x)
    out = [f"考虑的论文：{res['papers_considered']} 篇" + (f"（{res['since']} 之后）" if res["since"] else "")]
    out.append("\n## 文献压在哪些条目上（命中论文数）")
    out += [f"- {t(n)}：{c}" for n, c in res["pressure"][:15]] or ["- 没有命中"]
    out.append(f"\n## 远距离同线对（共 {res['pairs_total']} 对，列前 {len(res['pairs'])} 对）")
    out.append("同时命中的论文多：多半是树里缺了一条显然的关联，应补成关系。命中少但跨领域：才是点子的候选。")
    for p in res["pairs"]:
        extra = f"，{len(p['shared_papers'])} 篇论文同时命中" if p["shared_papers"] else ""
        out.append(f"- [{line_titles.get(p['line'], p['line'])}] {t(p['a'])} ↔ {t(p['b'])}：树上相隔 {p['gap']} 步{extra}")
    out.append("\n## 还没有条目覆盖的论文（每条研究线前几篇）")
    for lid, refs in res["uncovered"].items():
        out.append(f"- {line_titles.get(lid, lid)}：共 {res['uncovered_total'][lid]} 篇")
        out += [f"  - {r['date']} {r['title_zh'] or r['title']}" for r in refs[:5]]
    return "\n".join(out)
