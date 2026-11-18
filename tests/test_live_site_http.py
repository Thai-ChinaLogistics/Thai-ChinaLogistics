"""Synthetic local tests: origin HTTP status must not be confused with tools/GSC."""
import importlib.util
from pathlib import Path
import tempfile
import sys
import unittest
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location("audit_live_site_http", ROOT / "tools" / "audit_live_site_http.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class FakeResponse:
    def __init__(self, url, body, content_type, *, status=200, x_robots=""):
        self.url, self.body, self.status = url, body, status
        self.headers = {"Content-Type": content_type, "X-Robots-Tag": x_robots}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def geturl(self):
        return self.url
    def read(self, amount):
        return self.body[:amount]


def html(url):
    return ('<html><head><title>Thai-China Logistics</title>'
            '<link rel="canonical" href="' + url + '"></head><body>'
            '<h1>Shipping services</h1></body></html>').encode()


def xml():
    return ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            '<url><loc>' + mod.BASE_URL + '</loc></url></urlset>').encode()


def normal_opener(request, *, timeout):
    url = request.full_url
    if url.endswith("/robots.txt"):
        raise HTTPError(url, 404, "Not Found", {}, None)
    if url.endswith("/sitemap.xml"):
        return FakeResponse(url, xml(), "application/xml")
    return FakeResponse(url, html(url), "text/html; charset=utf-8")


class LiveHttpAuditTests(unittest.TestCase):
    def test_real_http_200_can_be_recorded_as_source_pass(self):
        result = mod.probe("express", mod.BASE_URL + "thailand-to-china-express.html",
                           "html", required=True, opener=normal_opener)
        self.assertEqual(result["http_status"], 200)
        self.assertTrue(result["canonical_is_self"])
        self.assertEqual(result["result"], "PASS")

    def test_sitemap_has_parsed_loc_count(self):
        result = mod.probe("sitemap", mod.BASE_URL + "sitemap.xml",
                           "xml", required=True, opener=normal_opener)
        self.assertEqual(result["sitemap_loc_count"], 1)
        self.assertEqual(result["result"], "PASS")

    def test_http_404_is_explicit_origin_status(self):
        def failure(request, *, timeout):
            raise HTTPError(request.full_url, 404, "Not Found", {}, None)
        result = mod.probe("express", mod.BASE_URL + "thailand-to-china-express.html",
                           "html", required=True, opener=failure)
        self.assertEqual(result["http_status"], 404)
        self.assertEqual(result["result"], "ORIGIN_HTTP_ERROR")

    def test_dns_failure_does_not_invent_http_status(self):
        def failure(request, *, timeout):
            raise URLError("dns failure")
        result = mod.probe("express", mod.BASE_URL + "thailand-to-china-express.html",
                           "html", required=True, opener=failure)
        self.assertIsNone(result["http_status"])
        self.assertEqual(result["result"], "NETWORK_ERROR")

    def test_robot_root_absence_is_optional_not_robots_blocked(self):
        report = mod.audit(opener=normal_opener)
        self.assertEqual(report["summary"]["required"], 5)
        self.assertEqual(report["summary"]["passed"], 5)
        self.assertEqual(report["summary"]["status"], "HTTP_SOURCE_CHECK_PASS")
        robots = next(x for x in report["probes"] if x["name"] == "host_root_robots")
        self.assertEqual(robots["http_status"], 404)
        self.assertFalse(robots["required"])

    def test_exact_live_bytes_match_checked_out_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, relative in mod.SOURCE_PATHS.items():
                url = next(p[1] for p in mod.PROBES if p[0] == name)
                body = xml() if name == "sitemap" else html(url)
                (root / relative).write_bytes(body)
            result = mod.compare_live_to_checkout(mod.audit(opener=normal_opener), root)
            self.assertEqual(result["status"], "ALL_DEPLOYED_SOURCE_MATCH")
            self.assertEqual(result["exact_matches"], 5)
            self.assertEqual(result["needs_review"], 0)

    def test_http_200_with_old_page_content_is_not_deployment_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, relative in mod.SOURCE_PATHS.items():
                url = next(p[1] for p in mod.PROBES if p[0] == name)
                body = xml() if name == "sitemap" else html(url)
                (root / relative).write_bytes(body)
            (root / "thailand-to-china-express.html").write_bytes(b"new edited content")
            result = mod.compare_live_to_checkout(mod.audit(opener=normal_opener), root)
            self.assertEqual(result["status"], "REVIEW_REQUIRED")
            self.assertEqual(result["exact_matches"], 4)
            self.assertEqual(next(x for x in result["checks"]
                                  if x["name"] == "express")["status"],
                             "SOURCE_DIFFERS_FROM_DEPLOYED")

    def test_source_comparison_does_not_infer_google_indexing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = mod.compare_live_to_checkout(mod.audit(opener=normal_opener), Path(tmp))
            self.assertIn("google_indexed", result["not_proof_of"])
            self.assertEqual(result["needs_review"], 5)

    def test_x_robots_noindex_is_review(self):
        def response(request, *, timeout):
            return FakeResponse(request.full_url, html(request.full_url), "text/html",
                                x_robots="noindex")
        result = mod.probe("express", mod.BASE_URL + "thailand-to-china-express.html",
                           "html", required=True, opener=response)
        self.assertEqual(result["result"], "HEADER_NOINDEX")

    def test_unexpected_redirect_does_not_claim_pass(self):
        def response(request, *, timeout):
            return FakeResponse("https://other.example.com/", html(request.full_url), "text/html")
        result = mod.probe("express", mod.BASE_URL + "thailand-to-china-express.html",
                           "html", required=True, opener=response)
        self.assertEqual(result["result"], "UNEXPECTED_REDIRECT")


if __name__ == "__main__":
    unittest.main()
