"""Guard user-observed query phrases on the pre-existing canonical pages.

Search-suggestion screenshots do not constitute verified query volume,
Google indexing, AI citation or customer leads. This is source-only QA.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/"


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0
        self.canonicals = []
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {"script", "style", "template", "noscript"}:
            self.skip += 1
        if tag == "h1":
            self.h1_count += 1
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href"))

    def handle_endtag(self, tag):
        if tag in {"script", "style", "template", "noscript"} and self.skip:
            self.skip -= 1

    def handle_data(self, text):
        if not self.skip:
            self.parts.append(text)


def page(relative):
    parser = VisibleHTML()
    parser.feed((ROOT / relative).read_text(encoding="utf-8"))
    return parser


class UserSuggestionPageTests(unittest.TestCase):
    def test_priority_queries_have_a_real_existing_landing_answer(self):
        matched = {
            "thailand-to-china-express.html": "从泰国寄东西回中国",
            "bangkok-to-china.html": "曼谷邮寄回国",
            "thailand-to-china-price.html": "泰国寄到中国的运费",
            "luggage-to-china.html": "泰国邮寄行李回国",
            "moving-to-china.html": "泰国寄中国大件物流",
        }
        for relative, phrase in matched.items():
            with self.subTest(relative=relative):
                p = page(relative)
                text = re.sub(r"\s+", " ", " ".join(p.parts))
                self.assertIn(phrase, text)
                self.assertEqual(p.canonicals, [BASE + relative])
                self.assertEqual(p.h1_count, 1)

    def test_bangkok_page_links_to_price_and_pickup_not_new_duplicate_pages(self):
        source = (ROOT / "bangkok-to-china.html").read_text(encoding="utf-8")
        self.assertIn('href="thailand-to-china-price.html"', source)
        self.assertIn('href="thailand-to-china-pickup.html"', source)

    def test_sitemap_lastmod_only_reflects_real_edits(self):
        root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        entries = {
            node.findtext(f"{ns}loc"): node.findtext(f"{ns}lastmod")
            for node in root.findall(f"{ns}url")
        }
        self.assertEqual(len(entries), 28)
        for relative in (
            "thailand-to-china-express.html", "bangkok-to-china.html",
            "thailand-to-china-price.html", "luggage-to-china.html",
            "moving-to-china.html"
        ):
            self.assertEqual(entries[BASE + relative], "2026-11-18")

    def test_competitor_brand_terms_not_in_our_updated_titles(self):
        for relative in (
            "thailand-to-china-express.html", "bangkok-to-china.html",
            "thailand-to-china-price.html", "luggage-to-china.html",
            "moving-to-china.html"
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            title = re.search(r"<title>(.*?)</title>", source, re.DOTALL)
            self.assertIsNotNone(title)
            for term in ("中通", "kex", "最便宜", "第一名"):
                self.assertNotIn(term.casefold(), title.group(1).casefold())


if __name__ == "__main__":
    unittest.main()
