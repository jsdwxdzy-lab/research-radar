import json
import tempfile
import unittest
from pathlib import Path

from radar import theory, theory_md

ROOT = Path(__file__).resolve().parent.parent


def node_file(meta: dict, body: str = "") -> str:
    return "```json\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n```\n" + body


def base_meta(nid: str, **kw) -> dict:
    meta = {
        "id": nid, "title": f"标题 {nid}", "type": "concept", "parent": "d1",
        "purpose": f"{nid} 的学习目的", "status": "draft", "version": "0.1",
        "updated": "2026-11-09", "sources": [],
    }
    meta.update(kw)
    return meta


class Fixture:
    """A tiny knowledge base written to a temp dir."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.k = self.root / "knowledge"
        for d in ("nodes", "paths", "reviews"):
            (self.k / d).mkdir(parents=True)
        self.domains([{"id": "d1", "title": "领域一", "summary": "领域一的范围"},
                      {"id": "d2", "title": "领域二", "summary": "领域二的范围"}],
                     [{"id": "line1", "title": "研究线一", "radar_topics": ["csp"]}])
        self.sources([])
        self.relations([])

    def close(self):
        self.tmp.cleanup()

    def domains(self, items, lines=()):
        data = {"root": {"title": "测试地图", "intro": "从基础铺开。"}, "domains": items, "research_lines": list(lines)}
        (self.k / "domains.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def sources(self, items):
        (self.k / "sources.json").write_text(json.dumps({"sources": items}, ensure_ascii=False), encoding="utf-8")

    def relations(self, items):
        (self.k / "relations.json").write_text(json.dumps({"relations": items}, ensure_ascii=False), encoding="utf-8")

    def node(self, meta, body="正文。"):
        (self.k / "nodes" / f"{meta['id']}.md").write_text(node_file(meta, body), encoding="utf-8")

    def path(self, data):
        (self.k / "paths" / f"{data['id']}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def review(self, nid, items):
        (self.k / "reviews" / f"{nid}.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")

    def kb(self):
        return theory.validate(theory.load(self.root))


def rel(a, b, typ="prerequisite", **kw):
    r = {"id": f"{a}-{b}", "from": a, "to": b, "type": typ, "explanation": "联系说明",
         "condition": "无额外条件", "sources": [], "status": "draft"}
    r.update(kw)
    return r


def messages(kb, level="error"):
    return [i.message for i in kb.issues if i.level == level]


class MarkdownTests(unittest.TestCase):
    def test_raw_html_is_escaped(self):
        res = theory_md.render("正文 <script>alert(1)</script> **粗体**")
        self.assertNotIn("<script>", res.html)
        self.assertIn("&lt;script&gt;", res.html)
        self.assertIn("<strong>粗体</strong>", res.html)

    def test_math_kept_verbatim_and_attribute_escaped(self):
        res = theory_md.render('行内 $a_{i}*b_{j} < c$ 结束\n\n$$\n\\frac{"x"}{y}\n$$')
        self.assertIn('data-tex="a_{i}*b_{j} &lt; c"', res.html)
        self.assertNotIn("<em>", res.html)  # * inside math must not become emphasis
        self.assertIn('data-display="1"', res.html)
        self.assertIn("&quot;x&quot;", res.html)
        self.assertEqual(res.errors, [])

    def test_sections_layers_and_claims(self):
        res = theory_md.render("## 直觉 {intuition}\n\n::: approximation 小标题\n内容\n:::\n\n## 推导 {math}\n\n文字")
        self.assertEqual([t["layer"] for t in res.toc], ["intuition", "math"])
        self.assertIn('data-layer="intuition"', res.html)
        self.assertIn('<span class="claim-kind">近似</span>', res.html)
        self.assertEqual(res.claims, ["approximation"])
        self.assertEqual(res.html.count("<section"), res.html.count("</section>"))

    def test_unknown_layer_and_claim_are_errors(self):
        res = theory_md.render("## 标题 {vibes}\n\n::: opinion\n内容\n:::")
        self.assertTrue(any("阅读层次" in e for e in res.errors))
        self.assertTrue(any("论述类型" in e for e in res.errors))

    def test_links_citations_and_unsafe_urls(self):
        res = theory_md.render(
            "见 [[known]]、[[missing]]、[@src, 第 2 节]、[@nope] 和 [坏链接](javascript:alert(1))",
            node_url=lambda x: f"{x}.html" if x == "known" else None,
            node_title=lambda x: "已知节点" if x == "known" else None,
            cite_label=lambda x: "Src 2020" if x == "src" else None)
        self.assertIn('<a class="node-link" href="known.html">已知节点</a>', res.html)
        self.assertIn('href="#src-src">[Src 2020，第 2 节]', res.html)
        self.assertNotIn("javascript:", res.html)
        self.assertEqual(res.links, ["known", "missing"])
        self.assertEqual(res.cites, ["src", "nope"])
        self.assertEqual(len(res.errors), 2)

    def test_table_and_lists(self):
        res = theory_md.render("| a | b |\n| --- | --- |\n| $x$ | 2 |\n\n- 一\n- 二\n\n1. 甲\n2. 乙")
        self.assertIn("<table>", res.html)
        self.assertIn('data-tex="x"', res.html)
        self.assertIn("<ul><li>一</li><li>二</li></ul>", res.html)
        self.assertIn("<ol><li>甲</li><li>乙</li></ol>", res.html)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def test_minimal_content_is_valid(self):
        self.f.node(base_meta("a"), "## 一 {intuition}\n\n见 [[b]]。")
        self.f.node(base_meta("b"))
        self.f.relations([rel("a", "b")])
        kb = self.f.kb()
        self.assertEqual(messages(kb), [])
        self.assertEqual(messages(kb, "warning"), [])

    def test_relation_needs_explanation_condition_and_real_nodes(self):
        self.f.node(base_meta("a"))
        self.f.relations([rel("a", "ghost", explanation="", condition=" ", type="looks-alike")])
        errs = " ".join(messages(self.f.kb()))
        for word in ("explanation", "condition", "ghost", "type"):
            self.assertIn(word, errs)

    def test_prerequisite_cycle_is_rejected(self):
        for n in ("a", "b", "c"):
            self.f.node(base_meta(n))
        self.f.relations([rel("a", "b"), rel("b", "c"), rel("c", "a")])
        self.assertTrue(any("成环" in m for m in messages(self.f.kb())))

    def test_cycles_only_count_prerequisites(self):
        self.f.node(base_meta("a"))
        self.f.node(base_meta("b"))
        self.f.relations([rel("a", "b"), rel("b", "a", typ="contrasts")])
        self.assertEqual(messages(self.f.kb()), [])

    def test_node_without_relations_is_fine(self):
        self.f.node(base_meta("lonely"))
        kb = self.f.kb()
        self.assertEqual(messages(kb), [])
        self.assertEqual(messages(kb, "warning"), [])

    def test_parent_must_exist(self):
        self.f.node(base_meta("a", parent="nowhere"))
        self.assertTrue(any("父节点不存在" in m and "nowhere" in m for m in messages(self.f.kb())))

    def test_parent_cycle_is_rejected(self):
        self.f.node(base_meta("a", parent="b"))
        self.f.node(base_meta("b", parent="a"))
        self.f.node(base_meta("c", parent="a"))
        errs = messages(self.f.kb())
        self.assertTrue(any("父节点成环" in m for m in errs))

    def test_nested_parents_reach_a_domain(self):
        self.f.node(base_meta("a"))
        self.f.node(base_meta("b", parent="a"))
        self.f.node(base_meta("c", parent="b"))
        kb = self.f.kb()
        self.assertEqual(messages(kb), [])
        self.assertEqual(kb.ancestors("c"), ["d1", "a", "b"])
        self.assertEqual(kb.domain_of("c"), "d1")
        self.assertEqual(sorted(kb.subtree("d1")), ["a", "b", "c"])

    def test_domain_id_cannot_clash_with_node(self):
        self.f.node(base_meta("d2"))
        self.assertTrue(any("领域 ID 与节点 ID 冲突" in m for m in messages(self.f.kb())))

    def test_unknown_research_line_and_bad_keywords(self):
        self.f.node(base_meta("a", research=["line1", "ghost-line"], keywords="不是列表"))
        errs = " ".join(messages(self.f.kb()))
        self.assertIn("研究线不存在", errs)
        self.assertIn("ghost-line", errs)
        self.assertIn("keywords 必须是列表", errs)

    def test_research_distance_walks_tree_and_relations(self):
        self.f.node(base_meta("hub", research=["line1"]))
        self.f.node(base_meta("kid", parent="hub"))
        self.f.node(base_meta("far", parent="d2"))
        self.f.node(base_meta("linked", parent="d2"))
        self.f.relations([rel("linked", "kid")])
        kb = self.f.kb()
        self.assertEqual(messages(kb), [])
        dist = kb.research_distance("line1")
        self.assertEqual(dist["hub"], 0)
        self.assertEqual(dist["kid"], 1)
        self.assertEqual(dist["linked"], 2)
        self.assertNotIn("far", dist)

    def _verified_setup(self, consulted, reviews):
        self.f.sources([{"id": "s", "short": "S 2020", "kind": "paper", "citation": "S, 2020", "doi": "10.1/x",
                         "consulted": consulted}])
        self.f.node(base_meta("v", status="verified", sources=["s"]), "## 一\n\n正文 [@s]。")
        self.f.node(base_meta("w"))
        self.f.relations([rel("v", "w")])
        if reviews is not None:
            self.f.review("v", reviews)
        return messages(self.f.kb())

    def test_verified_requires_independent_review(self):
        errs = self._verified_setup([{"date": "2026-11-09", "by": "reviewer-a", "what": "第 2 节"}], None)
        self.assertTrue(any("核验记录" in e for e in errs))

    def test_model_self_check_does_not_count_as_review(self):
        errs = self._verified_setup(
            [{"date": "2026-11-09", "by": "reviewer-a", "what": "第 2 节"}],
            [{"date": "2026-11-09", "reviewer": "生成模型", "independent": False, "scope": ["全文"],
              "method": "复读", "evidence": ["无"]}])
        self.assertTrue(any("核验记录" in e for e in errs))

    def test_verified_needs_consulted_sources(self):
        errs = self._verified_setup([], [{"date": "2026-11-09", "reviewer": "reviewer-a", "independent": True,
                                          "scope": ["式 (1)"], "method": "独立重推", "evidence": ["s 第 2 节"]}])
        self.assertTrue(any("查阅记录" in e for e in errs))

    def test_fully_verified_node_passes(self):
        errs = self._verified_setup([{"date": "2026-11-09", "by": "reviewer-a", "what": "第 2 节式 (3)"}],
                                    [{"date": "2026-11-09", "reviewer": "reviewer-a", "independent": True,
                                      "scope": ["式 (1)"], "method": "独立重推", "evidence": ["s 第 2 节"]}])
        self.assertEqual(errs, [])

    def test_verified_node_cannot_hold_unverified_block(self):
        self.f.sources([{"id": "s", "kind": "paper", "citation": "S", "doi": "10.1/x",
                         "consulted": [{"date": "d", "by": "b", "what": "w"}]}])
        self.f.node(base_meta("v", status="verified", sources=["s"]), "::: unverified\n还没查\n:::")
        self.f.review("v", [{"date": "d", "reviewer": "r", "independent": True, "scope": ["x"],
                             "method": "m", "evidence": ["e"]}])
        self.assertTrue(any("待核验" in e for e in messages(self.f.kb())))

    def test_superseded_needs_target_and_migration(self):
        self.f.node(base_meta("old", status="superseded"))
        errs = " ".join(messages(self.f.kb()))
        self.assertIn("replaced_by", errs)
        self.assertIn("migration", errs)

    def test_id_must_match_filename_and_metadata_must_be_fenced(self):
        (self.f.k / "nodes" / "x.md").write_text(node_file(base_meta("y")), encoding="utf-8")
        (self.f.k / "nodes" / "z.md").write_text("---\n{}\n---\n正文", encoding="utf-8")
        errs = " ".join(messages(self.f.kb()))
        self.assertIn("文件名必须与 id 一致", errs)
        self.assertIn("```json", errs)

    def test_path_steps_must_exist(self):
        self.f.node(base_meta("a"))
        self.f.path({"id": "p", "title": "路径", "question": "原问题", "general_question": "通用问题",
                     "steps": [{"node": "a", "why": "因为"}, {"node": "ghost", "why": "因为"}],
                     "branches": [{"direction": "sideways", "title": "x", "why": "y"}]})
        errs = " ".join(messages(self.f.kb()))
        self.assertIn("ghost", errs)
        self.assertIn("分支方向", errs)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.f.sources([{"id": "s", "short": "S 2020", "kind": "paper", "citation": "S, 2020", "doi": "10.1/x",
                         "consulted": []}])
        self.f.node(base_meta("a", title="标题 <b>A</b>", sources=["s"], research=["line1"]),
                    "## 直觉 {intuition}\n\n$E = mc^2$，见 [[b]] [@s]。\n\n## 推导 {math}\n\n$$x^2$$")
        self.f.node(base_meta("b", status="candidate", parent="a"), "")
        self.f.relations([rel("a", "b")])
        self.f.review("a", [{"date": "2026-11-09", "reviewer": "生成模型", "independent": False,
                             "scope": ["一维例子"], "method": "复算", "evidence": ["无"]}])
        self.f.path({"id": "p", "title": "路径", "question": "原问题", "general_question": "通用问题",
                     "steps": [{"node": "a", "why": "先读"}, {"node": "b", "why": "再读"}]})

    def tearDown(self):
        self.f.close()

    def test_build_then_check_is_clean_and_detects_drift(self):
        kb, written = theory.build(self.f.root)
        self.assertEqual(kb.errors, [])
        out = self.f.root / "theory"
        for rel_path in ("index.html", "tree.html", "guide.html", "nodes/a.html", "nodes/b.html", "paths/p.html",
                         "assets/theory.css", "assets/theory.js", "assets/search-index.js"):
            self.assertTrue((out / rel_path).exists(), rel_path)
        _, drift = theory.check(self.f.root)
        self.assertEqual(drift, [])
        # building twice is a no-op (deterministic output)
        _, again = theory.build(self.f.root)
        self.assertEqual(again, [])
        (out / "nodes" / "a.html").write_text("手改过", encoding="utf-8")
        (out / "stray.html").write_text("x", encoding="utf-8")
        _, drift = theory.check(self.f.root)
        self.assertTrue(any("nodes/a.html" in d for d in drift))
        self.assertTrue(any("stray.html" in d for d in drift))

    def test_errors_block_the_build(self):
        self.f.relations([rel("a", "ghost")])
        kb, written = theory.build(self.f.root)
        self.assertTrue(kb.errors)
        self.assertEqual(written, [])
        self.assertFalse((self.f.root / "theory").exists())

    def test_node_page_content(self):
        theory.build(self.f.root)
        html = (self.f.root / "theory" / "nodes" / "a.html").read_text(encoding="utf-8")
        self.assertIn("标题 &lt;b&gt;A&lt;/b&gt;", html)
        self.assertIn('class="banner banner-draft"', html)
        self.assertIn("生成模型自查，不计为核验", html)
        self.assertIn("尚未实际查阅", html)
        self.assertIn('href="../nodes/b.html"', html)
        self.assertIn("katex.min.js", html)
        self.assertIn('integrity="sha384-', html)
        self.assertIn('data-layer-filter="math"', html)
        self.assertIn("issues/new?title=", html)
        cand = (self.f.root / "theory" / "nodes" / "b.html").read_text(encoding="utf-8")
        self.assertNotIn("katex.min.js", cand)
        self.assertIn("候选节点，还没有正文", cand)

    def test_node_page_shows_tree_position(self):
        theory.build(self.f.root)
        a = (self.f.root / "theory" / "nodes" / "a.html").read_text(encoding="utf-8")
        self.assertIn('href="../tree.html?line=line1"', a)
        self.assertIn("子条目", a)
        self.assertIn('class="node-link is-candidate" href="../nodes/b.html"', a)
        self.assertIn('class="cat-foot"', a)
        self.assertIn("参考资料", a)
        b = (self.f.root / "theory" / "nodes" / "b.html").read_text(encoding="utf-8")
        self.assertIn('class="tree-trail"', b)
        self.assertIn('href="../tree.html#t-d1"', b)
        self.assertIn('href="../nodes/a.html"', b)  # parent in breadcrumbs and trail

    def test_home_lists_unverified_separately(self):
        theory.build(self.f.root)
        html = (self.f.root / "theory" / "index.html").read_text(encoding="utf-8")
        self.assertIn("还没有已核验的节点", html)
        self.assertIn("草稿（1 个", html)
        self.assertIn('href="tree.html#t-d1"', html)
        self.assertIn('href="tree.html?line=line1"', html)
        self.assertIn("1 个交汇点", html)

    def test_tree_page_covers_every_node(self):
        theory.build(self.f.root)
        html = (self.f.root / "theory" / "tree.html").read_text(encoding="utf-8")
        for x in ('id="t-d1"', 'id="t-d2"', 'id="o-a"', 'id="o-b"', 'id="treeData"', 'data-page="tree"'):
            self.assertIn(x, html)
        raw = html.split('<script type="application/json" id="treeData">', 1)[1].split("</script>", 1)[0]
        data = json.loads(raw)
        self.assertEqual([d["id"] for d in data["domains"]], ["d1", "d2"])
        by = {n["id"]: n for n in data["nodes"]}
        self.assertEqual(by["b"]["parent"], "a")
        self.assertEqual(by["a"]["dist"], {"line1": 0})
        self.assertEqual(by["b"]["dist"], {"line1": 1})
        # outline nests b under a
        self.assertLess(html.index('id="o-a"'), html.index('id="o-b"'))

    def test_search_index_is_valid_json(self):
        theory.build(self.f.root)
        js = (self.f.root / "theory" / "assets" / "search-index.js").read_text(encoding="utf-8")
        prefix = "window.THEORY_INDEX="
        self.assertTrue(js.startswith(prefix))
        data = json.loads(js[len(prefix):].rstrip().rstrip(";"))
        self.assertEqual(sorted(n["id"] for n in data["nodes"]), ["a", "b"])
        self.assertEqual(data["paths"][0]["steps"], ["a", "b"])

    def test_public_output_holds_no_personal_records(self):
        theory.build(self.f.root)
        for p in (self.f.root / "theory").rglob("*.html"):
            text = p.read_text(encoding="utf-8")
            self.assertNotIn('"question":', text)
            self.assertNotIn('"note":', text)


class JunctionTests(unittest.TestCase):
    def setUp(self):
        from radar import junctions
        self.j = junctions
        self.f = Fixture()
        self.f.node(base_meta("hub", research=["line1"], keywords=["crystal structure prediction"]))
        self.f.node(base_meta("deep", parent="hub", status="candidate", research=["line1"], keywords=["PBE"]))
        self.f.node(base_meta("far", parent="d2", status="candidate", research=["line1"], keywords=["MACE"]))
        self.f.node(base_meta("other", parent="d2", status="candidate", keywords=["phonon"]))
        items = [
            {"k": "p1", "t": "MACE ranks crystal structure prediction candidates", "a": "", "tp": ["csp"], "d": "2026-11-08"},
            {"k": "p2", "t": "PBEsol lattice constants", "a": "nothing else", "tp": ["csp"], "d": "2026-11-08"},
            {"k": "p3", "t": "Unrelated topic with phonon", "a": "", "tp": ["mlip"], "d": "2026-11-08"},
            {"k": "p4", "t": "Old CSP paper", "a": "crystal structure prediction", "tp": ["csp"], "d": "2026-10-01"},
        ]
        (self.f.root / "data.json").write_text(json.dumps({"items": items}), encoding="utf-8")

    def tearDown(self):
        self.f.close()

    def test_hits_pairs_and_uncovered(self):
        res = self.j.find(self.f.root, since="2026-11-01", min_gap=3)
        self.assertEqual(res["papers_considered"], 3)
        keys = {h["key"]: h["nodes"] for h in res["hits"]}
        self.assertEqual(sorted(keys["p1"]), ["far", "hub"])
        self.assertNotIn("p2", keys)          # PBE must not match inside PBEsol
        self.assertNotIn("p3", keys)          # mlip topic is not mapped to any research line
        self.assertEqual([r["key"] for r in res["uncovered"]["line1"]], ["p2"])
        pair = {(p["a"], p["b"]) for p in res["pairs"]}
        self.assertIn(("far", "hub"), pair)
        self.assertNotIn(("deep", "hub"), pair)  # parent/child is not a junction
        top = res["pairs"][0]
        self.assertEqual((top["a"], top["b"], top["shared_papers"]), ("far", "hub", ["p1"]))

    def test_existing_relation_removes_pair(self):
        self.f.relations([rel("hub", "far", typ="contrasts")])
        res = self.j.find(self.f.root, min_gap=3)
        self.assertNotIn(("far", "hub"), {(p["a"], p["b"]) for p in res["pairs"]})

    def test_finder_writes_nothing(self):
        before = sorted(p.relative_to(self.f.root).as_posix() for p in self.f.root.rglob("*"))
        self.j.find(self.f.root)
        after = sorted(p.relative_to(self.f.root).as_posix() for p in self.f.root.rglob("*"))
        self.assertEqual(before, after)


class DashboardLinkTests(unittest.TestCase):
    def test_paper_board_links_to_theory_map(self):
        html = (ROOT / "radar" / "web" / "dashboard.html").read_text(encoding="utf-8")
        self.assertIn('href="theory/index.html"', html)


if __name__ == "__main__":
    unittest.main()
