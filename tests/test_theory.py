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
        "id": nid, "title": f"标题 {nid}", "type": "concept", "trunk": "t1",
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
        self.trunks([{"id": "t1", "title": "主干一", "question": "问题一？"}])
        self.sources([])
        self.relations([])

    def close(self):
        self.tmp.cleanup()

    def trunks(self, items):
        (self.k / "trunks.json").write_text(json.dumps({"trunks": items}, ensure_ascii=False), encoding="utf-8")

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

    def test_isolated_node_is_a_warning_not_an_error(self):
        self.f.node(base_meta("lonely"))
        kb = self.f.kb()
        self.assertEqual(messages(kb), [])
        self.assertTrue(any("孤立" in m for m in messages(kb, "warning")))

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
        self.f.node(base_meta("a", title="标题 <b>A</b>", sources=["s"]),
                    "## 直觉 {intuition}\n\n$E = mc^2$，见 [[b]] [@s]。\n\n## 推导 {math}\n\n$$x^2$$")
        self.f.node(base_meta("b", status="candidate"), "")
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
        for rel_path in ("index.html", "guide.html", "nodes/a.html", "nodes/b.html", "paths/p.html",
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

    def test_home_lists_unverified_separately(self):
        theory.build(self.f.root)
        html = (self.f.root / "theory" / "index.html").read_text(encoding="utf-8")
        self.assertIn("还没有已核验的节点", html)
        self.assertIn("草稿与候选（2 个", html)

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


class DashboardLinkTests(unittest.TestCase):
    def test_paper_board_links_to_theory_map(self):
        html = (ROOT / "radar" / "web" / "dashboard.html").read_text(encoding="utf-8")
        self.assertIn('href="theory/index.html"', html)


if __name__ == "__main__":
    unittest.main()
