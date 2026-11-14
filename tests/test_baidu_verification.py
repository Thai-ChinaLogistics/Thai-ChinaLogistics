"""Regression tests for owner-supplied Baidu meta tag readiness and verification.

No Baidu account token is hardcoded; never claim ownership based on HTML alone.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.baidu_verification import (
    analyze_html, install_tag, probe_live_site, OFFICIAL_SITE_URL,
)

BASE = ('<!DOCTYPE html><html lang="zh-CN"><head>'
        '<meta charset="utf-8"><title>泰中物流</title>'
        '<link rel="canonical" href="https://thai-chinalogistics.github.io/Thai-ChinaLogistics/">'
        '</head><body><h1>泰中物流</h1></body></html>')
CODE = "code-OwnerGenerated567890"


class DummyResponse:
    def __init__(self, url, data: bytes, status=200):
        self.url, self.data, self.status = url, data, status
    def geturl(self):
        return self.url
    def read(self, n=-1):
        return self.data if n < 0 else self.data[:n]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False


class BaiduOwnershipTests(unittest.TestCase):
    def test_no_token_is_not_configured_never_verified(self):
        state = analyze_html(BASE)
        self.assertEqual(state["state"], "ACCOUNT_TOKEN_REQUIRED")
        self.assertFalse(state["baidu_verified"])
        self.assertNotIn("content", str(state))
        self.assertEqual(state["meta_count"], 0)

    def test_install_exact_owner_supplied_code_only_in_head_and_idempotent(self):
        once = install_tag(BASE, CODE)
        self.assertIn('<meta name="baidu-site-verification" content="' + CODE + '">', once)
        self.assertEqual(once.count("baidu-site-verification"), 1)
        self.assertEqual(once.count("<h1>泰中物流</h1>"), 1)
        self.assertIn('rel="canonical"', once)
        self.assertEqual(install_tag(once, CODE), once)
        self.assertEqual(analyze_html(once)["state"], "TAG_READY_PENDING_PLATFORM_VERIFICATION")

    def test_rejects_injected_or_fake_codes(self):
        for code in (
            "", "SAMPLE", 'x" onmouseover="evil"', "<script>alert(1)</script>",
            "abc&def", "a" * 130, "网站验证", "ab\ncd",
        ):
            with self.subTest(code=code), self.assertRaises(ValueError):
                install_tag(BASE, code)

    def test_refuses_to_overwrite_existing_baidu_ownership(self):
        first = install_tag(BASE, CODE)
        with self.assertRaisesRegex(ValueError, "different"):
            install_tag(first, "code-AnotherOwner987654")

    def test_detects_tags_outside_head_duplicate_malformed_and_ambiguity(self):
        outside = BASE.replace("</body>", '<meta name="baidu-site-verification" content="' + CODE + '"></body>')
        self.assertEqual(analyze_html(outside)["state"], "MALFORMED_TAG_LOCATION")
        inside = install_tag(BASE, CODE)
        repeated = inside.replace("</head>", '<meta name="baidu-site-verification" content="' + CODE + '"></head>')
        self.assertEqual(analyze_html(repeated)["state"], "DUPLICATE_BAIDU_META")

    def test_live_project_200_does_not_prove_baidu_or_domain_root(self):
        html = install_tag(BASE, CODE)
        def urlopen(req, timeout):
            if req.full_url == OFFICIAL_SITE_URL:
                return DummyResponse(req.full_url, html.encode("utf-8"))
            raise HTTPError(req.full_url, 404, "Not Found", {}, None)
        with patch("scripts.baidu_verification.urlopen", side_effect=urlopen):
            report = probe_live_site(expected_code=CODE)
        self.assertEqual(report["project_http_status"], 200)
        self.assertEqual(report["domain_root_http_status"], 404)
        self.assertTrue(report["project_meta_matches"])
        self.assertFalse(report["baidu_platform_verified"])
        self.assertEqual(report["ownership_status"], "PLATFORM_ACCOUNT_VERIFICATION_REQUIRED")
        self.assertNotIn(CODE, str(report))

    def test_absent_code_fails_closed_on_live_html(self):
        def urlopen(req, timeout):
            return DummyResponse(req.full_url, BASE.encode("utf-8"))
        with patch("scripts.baidu_verification.urlopen", side_effect=urlopen):
            report = probe_live_site(expected_code=CODE)
        self.assertFalse(report["project_meta_matches"])
        self.assertEqual(report["ownership_status"], "HTML_TAG_NOT_LIVE")


if __name__ == "__main__":
    unittest.main()
