"""Small, dependency-free Markdown renderer for theory-map nodes.

Supports the subset documented in knowledge/README.md: headings with an
optional {layer} tag, paragraphs, lists, tables, block quotes, fenced code,
`::: kind title` claim blocks, $inline$ / $$display$$ math (rendered in the
browser by KaTeX), [[node-id|text]] links and [@source-id, locator] citations.
All text is HTML-escaped; raw HTML in the source is not passed through.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

LAYERS = {"intuition": "直观解释", "math": "数学与推导", "mapping": "对应与边界"}
CLAIMS = {
    "definition": "定义",
    "theorem": "定理",
    "approximation": "近似",
    "empirical": "经验结论",
    "analogy": "类比",
    "assumption": "假设",
    "unverified": "待核验",
    "question": "检验问题",
}

_PH = "\x00{}\x00"
_PH_RE = re.compile("\x00(\\d+)\x00")
_HEADING = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
_LAYER_TAG = re.compile(r"\s*\{(\w+)\}\s*$")
_CLAIM_OPEN = re.compile(r"^:::\s*([a-z]+)\s*(.*?)\s*$")
_LIST = re.compile(r"^(\s*)([-*]|\d+[.)])\s+(.*)$")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
_FIGURE = re.compile(r"^!\[([^\]]*)\]\(figs/([A-Za-z0-9][A-Za-z0-9_-]*\.svg)\)$")


@dataclass
class RenderResult:
    html: str
    toc: list = field(default_factory=list)          # [{"id","title","level","layer"}]
    links: list = field(default_factory=list)        # node ids referenced by [[...]]
    cites: list = field(default_factory=list)        # source ids referenced by [@...]
    claims: list = field(default_factory=list)       # claim kinds used
    figs: list = field(default_factory=list)         # figure file names used (knowledge/figs/)
    errors: list = field(default_factory=list)
    text: str = ""                                    # plain text for the search index


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def safe_url(url: str) -> str:
    url = (url or "").strip()
    return url if re.match(r"^https?://", url, re.I) else ""


class _Renderer:
    def __init__(self, node_url: Callable[[str], Optional[str]], node_title: Callable[[str], Optional[str]],
                 cite_label: Callable[[str], Optional[str]], fig_url: Optional[Callable[[str], Optional[str]]] = None):
        self.node_url = node_url
        self.node_title = node_title
        self.cite_label = cite_label
        self.fig_url = fig_url or (lambda _n: None)
        self.res = RenderResult(html="")
        self.slots: list[str] = []
        self.plain: list[str] = []

    # ---- inline -------------------------------------------------------------
    def _slot(self, value: str) -> str:
        self.slots.append(value)
        return _PH.format(len(self.slots) - 1)

    def inline(self, text: str) -> str:
        # 1. protect code and math before escaping
        def code(m):
            self.plain.append(m.group(1))
            return self._slot(f"<code>{esc(m.group(1))}</code>")

        def imath(m):
            tex = m.group(1)
            self.plain.append(tex)
            return self._slot(f'<span class="math" data-tex="{esc(tex)}">{esc(tex)}</span>')

        text = re.sub(r"`([^`]+)`", code, text)
        text = re.sub(r"(?<![\\$])\$(?!\s)([^$\n]+?)(?<!\s)\$(?!\$)", imath, text)

        # 2. node links and citations
        def wiki(m):
            target, label = m.group(1).strip(), (m.group(2) or "").strip()
            if target not in self.res.links:
                self.res.links.append(target)
            url = self.node_url(target)
            title = self.node_title(target)
            shown = label or title or target
            self.plain.append(shown)
            if not url:
                self.res.errors.append(f"链接到不存在的节点：{target}")
                return self._slot(f'<span class="broken-link">{esc(shown)}</span>')
            return self._slot(f'<a class="node-link" href="{esc(url)}">{esc(shown)}</a>')

        def cite(m):
            sid, loc = m.group(1).strip(), (m.group(2) or "").strip()
            if sid not in self.res.cites:
                self.res.cites.append(sid)
            label = self.cite_label(sid)
            if label is None:
                self.res.errors.append(f"引用了不存在的来源：{sid}")
                return self._slot(f'<span class="broken-link">[{esc(sid)}]</span>')
            inner = esc(label) + (f"，{esc(loc)}" if loc else "")
            return self._slot(f'<a class="cite" href="#src-{esc(sid)}">[{inner}]</a>')

        text = re.sub(r"\[\[([a-z0-9-]+)(?:\|([^\]]+))?\]\]", wiki, text)
        text = re.sub(r"\[@([a-z0-9-]+)(?:\s*,\s*([^\]]+))?\]", cite, text)

        # 3. ordinary links
        def link(m):
            label, url = m.group(1), safe_url(m.group(2))
            self.plain.append(label)
            if not url:
                return self._slot(esc(label))
            return self._slot(f'<a href="{esc(url)}" rel="noopener" target="_blank">{esc(label)}</a>')

        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)

        self.plain.append(_PH_RE.sub("", text))
        out = esc(text)
        out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
        out = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", out)
        return self._restore(out)

    def _restore(self, s: str) -> str:
        while _PH_RE.search(s):
            s = _PH_RE.sub(lambda m: self.slots[int(m.group(1))], s)
        return s

    # ---- blocks -------------------------------------------------------------
    def render(self, src: str) -> RenderResult:
        lines = src.replace("\r\n", "\n").split("\n")
        out: list[str] = []
        sec_open = False
        sec_n = 0
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue

            # fenced code
            if stripped.startswith("```"):
                j = i + 1
                buf = []
                while j < len(lines) and not lines[j].strip().startswith("```"):
                    buf.append(lines[j])
                    j += 1
                out.append(f"<pre><code>{esc(chr(10).join(buf))}</code></pre>")
                i = j + 1
                continue

            # display math
            if stripped.startswith("$$"):
                body = stripped[2:]
                if body.endswith("$$") and len(body) >= 2:
                    tex = body[:-2]
                    i += 1
                else:
                    buf = [body] if body else []
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().endswith("$$"):
                        buf.append(lines[j])
                        j += 1
                    if j >= len(lines):
                        self.res.errors.append("独立公式缺少结束的 $$")
                        tex = "\n".join(buf)
                    else:
                        last = lines[j].strip()[:-2]
                        if last:
                            buf.append(last)
                        tex = "\n".join(buf)
                    i = j + 1
                tex = tex.strip()
                self.plain.append(tex)
                out.append(f'<div class="math-block" tabindex="0" role="math" aria-label="公式">'
                           f'<span class="math" data-display="1" data-tex="{esc(tex)}">{esc(tex)}</span></div>')
                continue

            # claim block
            m = _CLAIM_OPEN.match(stripped)
            if m and stripped != ":::":
                kind, title = m.group(1), m.group(2)
                j = i + 1
                buf = []
                while j < len(lines) and lines[j].strip() != ":::":
                    buf.append(lines[j])
                    j += 1
                if j >= len(lines):
                    self.res.errors.append(f"论述块 {kind} 缺少结束的 :::")
                if kind not in CLAIMS:
                    self.res.errors.append(f"未知论述类型：{kind}")
                label = CLAIMS.get(kind, kind)
                if kind not in self.res.claims:
                    self.res.claims.append(kind)
                inner = _Renderer(self.node_url, self.node_title, self.cite_label, self.fig_url)
                sub = inner.render("\n".join(buf))
                self._absorb(sub)
                head = f'<span class="claim-kind">{esc(label)}</span>'
                if title:
                    head += f'<span class="claim-title">{self.inline(title)}</span>'
                out.append(f'<aside class="claim claim-{esc(kind)}" aria-label="{esc(label)}">'
                           f'<p class="claim-head">{head}</p>{sub.html}</aside>')
                i = j + 1
                continue

            # figure: a line that is only ![caption](figs/name.svg)
            fm = _FIGURE.match(stripped)
            if fm:
                cap, name = fm.group(1).strip(), fm.group(2)
                url = self.fig_url(name)
                self.plain.append(cap)
                if not url:
                    self.res.errors.append(f"图片不存在：figs/{name}")
                else:
                    if name not in self.res.figs:
                        self.res.figs.append(name)
                    out.append(f'<figure class="fig"><img src="{esc(url)}" alt="{esc(cap)}" loading="lazy">'
                               f"<figcaption>{self.inline(cap)}</figcaption></figure>")
                i += 1
                continue

            # heading
            m = _HEADING.match(stripped)
            if m:
                level = len(m.group(1))
                title = m.group(2)
                layer = ""
                lm = _LAYER_TAG.search(title)
                if lm:
                    layer = lm.group(1)
                    title = title[: lm.start()]
                    if layer not in LAYERS:
                        self.res.errors.append(f"未知阅读层次：{layer}")
                        layer = ""
                if level == 2:
                    if sec_open:
                        out.append("</section>")
                    sec_n += 1
                    sid = f"sec-{sec_n}"
                    attr = f' data-layer="{layer}"' if layer else ""
                    out.append(f'<section class="node-section" id="{sid}"{attr}>')
                    sec_open = True
                    badge = f'<span class="layer-tag layer-{layer}">{LAYERS[layer]}</span>' if layer else ""
                    title_html = self.inline(title)
                    out.append(f'<h2><a class="anchor" href="#{sid}">{title_html}</a>{badge}</h2>')
                    self.res.toc.append({"id": sid, "title": _PH_RE.sub("", re.sub(r"<[^>]+>", "", title_html)),
                                         "level": 2, "layer": layer})
                else:
                    out.append(f"<h{level}>{self.inline(title)}</h{level}>")
                i += 1
                continue

            # table
            if stripped.startswith("|") and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1]):
                head = self._cells(stripped)
                j = i + 2
                rows = []
                while j < len(lines) and lines[j].strip().startswith("|"):
                    rows.append(self._cells(lines[j].strip()))
                    j += 1
                th = "".join(f"<th scope=\"col\">{self.inline(c)}</th>" for c in head)
                body = "".join("<tr>" + "".join(f"<td>{self.inline(c)}</td>" for c in r) + "</tr>" for r in rows)
                out.append(f'<div class="table-wrap" tabindex="0"><table><thead><tr>{th}</tr></thead>'
                           f"<tbody>{body}</tbody></table></div>")
                i = j
                continue

            # block quote
            if stripped.startswith(">"):
                buf = []
                j = i
                while j < len(lines) and lines[j].strip().startswith(">"):
                    buf.append(lines[j].strip()[1:].lstrip())
                    j += 1
                out.append(f"<blockquote><p>{self.inline(' '.join(buf))}</p></blockquote>")
                i = j
                continue

            # list
            m = _LIST.match(line)
            if m:
                ordered = m.group(2)[0].isdigit()
                items = []
                j = i
                while j < len(lines):
                    lm2 = _LIST.match(lines[j])
                    if lm2 and lm2.group(2)[0].isdigit() == ordered:
                        items.append(lm2.group(3))
                    elif lines[j].strip() and lines[j].startswith("  ") and items:
                        items[-1] += " " + lines[j].strip()
                    else:
                        break
                    j += 1
                tag = "ol" if ordered else "ul"
                out.append(f"<{tag}>" + "".join(f"<li>{self.inline(t)}</li>" for t in items) + f"</{tag}>")
                i = j
                continue

            # paragraph
            buf = [stripped]
            j = i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if (not nxt or nxt.startswith(("#", "```", "$$", ":::", ">", "|")) or _LIST.match(lines[j])
                        or _FIGURE.match(nxt)):
                    break
                buf.append(nxt)
                j += 1
            out.append(f"<p>{self.inline(' '.join(buf))}</p>")
            i = j

        if sec_open:
            out.append("</section>")
        self.res.html = "\n".join(out)
        text = re.sub(r"\s+", " ", " ".join(self.plain)).strip()
        # stripped citations leave "例子 。"; drop the gap before CJK punctuation
        self.res.text = re.sub(r"\s+(?=[。，、；：？！）」』”])", "", text)
        return self.res

    def _cells(self, row: str) -> list[str]:
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in row.split("|")]

    def _absorb(self, sub: RenderResult) -> None:
        for key in ("links", "cites", "claims", "figs"):
            for v in getattr(sub, key):
                if v not in getattr(self.res, key):
                    getattr(self.res, key).append(v)
        self.res.errors.extend(sub.errors)
        self.plain.append(sub.text)


def render(src: str, node_url=None, node_title=None, cite_label=None, fig_url=None) -> RenderResult:
    return _Renderer(node_url or (lambda _id: None), node_title or (lambda _id: None),
                     cite_label or (lambda _id: None), fig_url).render(src)
