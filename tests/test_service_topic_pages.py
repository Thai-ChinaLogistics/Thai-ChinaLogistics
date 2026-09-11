from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/"


PAGES = {
    "thailand-domestic-moving.html": [
        "泰国国内搬家",
        "普吉搬家到曼谷",
        "曼谷搬家到普吉",
        "曼谷搬家到清迈",
        "清迈搬家到曼谷",
        "清迈搬家到普吉",
        "普吉搬家到清迈",
    ],
    "thailand-plants-to-china.html": ["泰国植物", "中国", "苗木", "盆栽", "鲜花"],
    "thailand-pets-to-china.html": ["泰国宠物", "中国", "猫", "狗"],
    "china-pets-to-thailand.html": ["中国宠物", "泰国", "猫", "狗"],
    "bird-nest-thailand-to-china.html": ["泰国燕窝", "中国", "燕窝"],
}


class ServiceTopicPagesTests(unittest.TestCase):
    def test_required_topic_pages_exist_and_have_core_seo(self):
        for filename, phrases in PAGES.items():
            with self.subTest(filename=filename):
                path = ROOT / filename
                self.assertTrue(path.exists(), f"missing page: {filename}")
                source = path.read_text(encoding="utf-8")
                self.assertRegex(source, r"(?is)<title>.+?</title>")
                self.assertRegex(source, r'(?is)<meta\s+name=["\']description["\'][^>]+content=["\'].+?["\']')
                self.assertRegex(source, r"(?is)<h1[^>]*>.*?</h1>")
                canonical = f'{SITE}{filename}'
                self.assertIn(f'<link rel="canonical" href="{canonical}">', source)
                for phrase in phrases:
                    self.assertIn(phrase, source)

    def test_new_topic_pages_are_in_sitemap(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for filename in PAGES:
            with self.subTest(filename=filename):
                self.assertIn(f"<loc>{SITE}{filename}</loc>", sitemap)

    def test_domestic_moving_routes_are_kept_on_one_topic_page(self):
        source = (ROOT / "thailand-domestic-moving.html").read_text(encoding="utf-8")
        route_phrases = [
            "普吉搬家到曼谷",
            "曼谷搬家到普吉",
            "曼谷搬家到清迈",
            "清迈搬家到曼谷",
            "清迈搬家到普吉",
            "普吉搬家到清迈",
        ]
        for phrase in route_phrases:
            self.assertIn(phrase, source)

        # Avoid a one-page-per-route architecture that would create keyword cannibalization.
        for forbidden in [
            "phuket-to-bangkok-moving.html",
            "bangkok-to-phuket-moving.html",
            "bangkok-to-chiang-mai-moving.html",
            "chiang-mai-to-bangkok-moving.html",
        ]:
            self.assertFalse((ROOT / forbidden).exists(), f"do not split route into {forbidden}")


if __name__ == "__main__":
    unittest.main()
