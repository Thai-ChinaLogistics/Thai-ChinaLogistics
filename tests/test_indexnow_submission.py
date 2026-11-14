import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.submit_indexnow import prepare_changed_urls, run_submission

ORIGIN = "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/"
KEY = "a" * 32


class FakeResponse:
    def __init__(self, url, data=b"", status=200):
        self.url = url
        self.data = data
        self.status = status

    def geturl(self):
        return self.url

    def read(self, limit=-1):
        return self.data if limit == -1 else self.data[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class IndexNowTests(unittest.TestCase):
    def make_site(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / (KEY + ".txt")).write_text(KEY, encoding="utf-8")
        for name in ("index.html", "luggage-to-china.html", "admin.html", "googleverify.html"):
            (root / name).write_text("<html><body>public</body></html>", encoding="utf-8")
        return tmp, root

    def test_only_updated_same_path_public_pages_are_submitted(self):
        tmp, root = self.make_site()
        try:
            pages = prepare_changed_urls(
                ["index.html", "luggage-to-china.html", "admin.html",
                 "googleverify.html", "../about.html", "https://evil.example/x.html",
                 "nested/bad.html", "luggage-to-china.html", "robots.txt"],
                root,
            )
            self.assertEqual(pages, [ORIGIN, ORIGIN + "luggage-to-china.html"])
        finally:
            tmp.cleanup()

    def test_key_must_be_live_before_submitting_and_no_fabricated_accepted_status(self):
        tmp, root = self.make_site()
        try:
            with patch("scripts.submit_indexnow.urlopen", side_effect=HTTPError("key", 404, "not found", {}, None)):
                report = run_submission(root, ["index.html"])
            self.assertEqual(report["status"], "KEY_NOT_PUBLIC")
            self.assertEqual(report["submitted_count"], 0)
            self.assertEqual(report["urls"], [ORIGIN])
        finally:
            tmp.cleanup()

    def test_real_receipt_is_not_an_indexing_claim(self):
        tmp, root = self.make_site()
        requests = []
        try:
            def fake_urlopen(request, timeout):
                requests.append(request)
                if request.full_url == ORIGIN + KEY + ".txt":
                    return FakeResponse(request.full_url, KEY.encode())
                payload = json.loads(request.data.decode())
                self.assertEqual(payload["host"], "thai-chinalogistics.github.io")
                self.assertEqual(payload["urlList"], [ORIGIN + "luggage-to-china.html"])
                self.assertEqual(payload["keyLocation"], ORIGIN + KEY + ".txt")
                return FakeResponse(request.full_url, b"", 202)
            with patch("scripts.submit_indexnow.urlopen", side_effect=fake_urlopen):
                report = run_submission(root, ["luggage-to-china.html"])
            self.assertEqual(report["status"], "RECEIVED_PENDING_VERIFICATION")
            self.assertEqual(report["submitted_count"], 1)
            self.assertFalse(report["indexing_verified"])
            self.assertNotIn(KEY, json.dumps(report))
            self.assertEqual(len(requests), 2)
        finally:
            tmp.cleanup()

    def test_empty_changed_pages_do_not_contact_network(self):
        tmp, root = self.make_site()
        try:
            with patch("scripts.submit_indexnow.urlopen", side_effect=AssertionError("network call")):
                report = run_submission(root, ["robots.txt", "admin.html"])
            self.assertEqual(report["status"], "NO_CHANGED_PUBLIC_PAGES")
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
