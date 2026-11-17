"""No-network tests for sitemap and static page evidence audit."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "audit_sitemap_pages.py"
spec = importlib.util.spec_from_file_location("audit_sitemap_pages", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BASE = "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/"
GOOD = ('<html><head><title>Shipping</title>'
        '<meta name="description" content="Logistics services">'
        '<link rel="canonical" href="' + BASE + '"></head>'
        '<body><h1>泰中物流</h1>'
        '<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage"}</script>'
        '</body></html>')


class SitemapAuditTests(unittest.TestCase):
    def fixture(self, directory, xml=None, home=GOOD):
        root = Path(directory)
        if xml is None:
            xml = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                   '<url><loc>' + BASE + '</loc><lastmod>2026-11-17</lastmod></url>'
                   '</urlset>')
        (root / "sitemap.xml").write_text(xml, encoding="utf-8")
        (root / "index.html").write_text(home, encoding="utf-8")
        return root

    def test_valid_sitemap_and_html(self):
        with tempfile.TemporaryDirectory() as d:
            result = mod.audit(self.fixture(d))
            self.assertEqual(result["sitemap_url_count"], 1)
            self.assertEqual(result["finding_count"], 0)
            self.assertFalse(result["can_authorize_edits"])

    def test_schema_and_canonical_are_checked(self):
        bad = GOOD.replace(BASE + '"></head>', BASE + 'wrong.html"></head>')
        bad = bad.replace('{"@context":"https://schema.org","@type":"WebPage"}', '{oops}')
        errors = mod.inspect_page(bad, BASE)
        self.assertIn("CANONICAL_NOT_EXACTLY_SELF", errors)
        self.assertIn("INVALID_JSONLD", errors)

    def test_missing_page_and_duplicate_sitemap_loc(self):
        with tempfile.TemporaryDirectory() as d:
            url = BASE + 'unknown.html'
            xml = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                   '<url><loc>' + url + '</loc></url>'
                   '<url><loc>' + url + '</loc></url>'
                   '</urlset>')
            result = mod.audit(self.fixture(d, xml=xml))
            codes = [e["code"] for e in result["findings"]]
            self.assertIn("SITEMAP_PAGE_MISSING_IN_REPO", codes)
            self.assertIn("DUPLICATE_SITEMAP_LOC", codes)

    def test_blocks_outside_project_and_traversal_urls(self):
        self.assertIsNone(mod.map_sitemap_url("https://example.com/"))
        self.assertIsNone(mod.map_sitemap_url(BASE + "sub/%2e%2e/private.html"))
        self.assertIsNone(mod.map_sitemap_url(BASE + "page.html?revision=1"))
        self.assertEqual(mod.map_sitemap_url(BASE), "index.html")

    def test_noindex_and_extra_h1_are_reported(self):
        x = GOOD.replace('<body><h1>', '<meta name="robots" content="noindex"><body><h1>')
        x = x.replace('</h1>', '</h1><h1>Second</h1>')
        result = mod.inspect_page(x, BASE)
        self.assertIn("SITEMAP_PAGE_NOINDEX", result)
        self.assertIn("H1_COUNT_NOT_ONE", result)


if __name__ == "__main__":
    unittest.main()
