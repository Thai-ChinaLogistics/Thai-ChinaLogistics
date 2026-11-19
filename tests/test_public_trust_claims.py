"""Regression tests for truthful, verifiable SEO/GEO business claims.

Runs offline. Does not certify shipping operations, customer reviews or Google indexing.
"""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicTrustClaimsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.entity = json.loads((ROOT / "ai-entity.json").read_text(encoding="utf-8"))

    def test_review_fabrication_and_unverified_rating_are_not_published(self):
        for marker in (
            "4.99", "reviews: [[", "window.createRatingSummaryCard",
            "window.createReviewCard", "window.refreshReviewMeta",
            "buildBalancedTwoWayReviews", "testimonialTrack",
        ):
            self.assertNotIn(marker, self.home)
        self.assertIn("当前暂不公开未经核验的客户评分和评价", self.home)
        self.assertEqual(self.home.count("reviews: []"), 3)

    def test_fixed_transit_promises_removed_across_three_languages(self):
        for marker in (
            "48小时", "48 Hours", "48 ชม.",
            "7-15", "20-30",
            "空运、陆运和海运都可咨询",
        ):
            self.assertNotIn(marker, self.home)

    def test_sea_freight_is_unavailable_not_an_active_service(self):
        self.assertNotIn("sea freight", self.entity["services"])
        self.assertIn("sea freight", self.entity["unavailableServices"])
        self.assertIn("海运服务暂未开放", self.home)

    def test_homepage_seo_and_contact_structure_preserved(self):
        self.assertEqual(len(re.findall(r'<meta[^>]+name="viewport"', self.home)), 1)
        self.assertIn('<link rel="canonical" href="https://thai-chinalogistics.github.io/Thai-ChinaLogistics/">', self.home)
        self.assertIn('id="faq"', self.home)
        self.assertIn('onsubmit="submitInquiry(event)"', self.home)
        self.assertIn('id="reviews"', self.home)
        self.assertIn('"@type": "Organization"', self.home)


if __name__ == "__main__":
    unittest.main()
