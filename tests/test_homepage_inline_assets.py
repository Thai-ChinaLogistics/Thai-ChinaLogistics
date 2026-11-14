"""Regression for live homepage byte budget and extracted original image data."""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_homepage_inline_assets import EXPECTED, validate

ROOT = Path(__file__).resolve().parents[1]


class HomepageInlineAssetsTests(unittest.TestCase):
    def test_current_site_assets_integrity_and_crawl_budget(self):
        self.assertEqual(validate(ROOT), [])

    def test_missing_or_corrupted_image_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "seo-inline").mkdir()
            shutil.copy2(ROOT / "index.html", root / "index.html")
            for name in EXPECTED:
                shutil.copy2(ROOT / "seo-inline" / name, root / "seo-inline" / name)
            missing = root / "seo-inline" / "facebook-icon.png"
            missing.unlink()
            self.assertTrue(any("facebook-icon.png: asset missing" in x for x in validate(root)))
            shutil.copy2(ROOT / "seo-inline" / "facebook-icon.png", missing)
            bad = root / "seo-inline" / "wechat-icon.png"
            bad.write_bytes(b"\x89PNG\r\n\x1a\nbroken")
            self.assertTrue(any("wechat-icon.png: bytes differ" in x for x in validate(root)))

    def test_reembedded_image_fails_crawl_budget_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "seo-inline").mkdir()
            shutil.copy2(ROOT / "index.html", root / "index.html")
            for name in EXPECTED:
                shutil.copy2(ROOT / "seo-inline" / name, root / "seo-inline" / name)
            page = root / "index.html"
            text = page.read_text(encoding="utf-8")
            page.write_text(text.replace(
                'src="seo-inline/facebook-icon.png"',
                'src="data:image/png;base64,wrong"'), encoding="utf-8")
            self.assertTrue(any("embedded base64" in x for x in validate(root)))


if __name__ == "__main__":
    unittest.main()
