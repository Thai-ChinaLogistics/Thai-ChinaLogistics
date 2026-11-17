"""Regression tests for read-only cross-source SEO/GEO business-fact audit."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "audit_geo_service_claims.py"
spec = importlib.util.spec_from_file_location("audit_geo_service_claims", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class GeoServiceClaimAuditTests(unittest.TestCase):
    def make_site(self, root, home="泰国寄中国，空运陆运咨询。"):
        base = Path(root)
        (base / "index.html").write_text("<html><body>" + home + "</body></html>", encoding="utf-8")
        (base / "about.html").write_text("<h1>Thai-China Logistics</h1>", encoding="utf-8")
        (base / "service.html").write_text("<h1>Shipping</h1>", encoding="utf-8")
        (base / "llms.txt").write_text(
            "# Thai-China Logistics\n+66 83 976 9828\nhttps://wa.me/66839769828\n", encoding="utf-8"
        )
        profile = {
            "canonicalName": "Thai-China Logistics",
            "canonicalUrl": "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/",
            "contact": {"telephone": "+66 83 976 9828",
                        "whatsapp": "https://wa.me/66839769828"},
            "services": ["air freight", "land freight"],
            "officialPages": {
                "home": "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/",
                "service": "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/service.html"
            }
        }
        (base / "ai-entity.json").write_text(json.dumps(profile), encoding="utf-8")
        return profile

    def test_consistent_minimal_profile_has_no_source_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            self.make_site(d)
            report = mod.audit(Path(d))
            self.assertEqual(report["finding_count"], 0)
            self.assertFalse(report["can_authorize_business_edits"])

    def test_sea_freight_advertised_while_homepage_unavailable_flags_review(self):
        with tempfile.TemporaryDirectory() as d:
            profile = self.make_site(d, "目前海运服务暂未开放，以空运陆运为主。")
            profile["services"].append("sea freight")
            (Path(d) / "ai-entity.json").write_text(json.dumps(profile), encoding="utf-8")
            report = mod.audit(Path(d))
            self.assertIn("SEA_SERVICE_STATUS_CONFLICT", [x["code"] for x in report["findings"]])
            self.assertEqual(report["status"], "REVIEW_REQUIRED")

    def test_exact_transport_time_claims_are_review_not_published_proofs(self):
        with tempfile.TemporaryDirectory() as d:
            self.make_site(d, "<p>48小时到达中国</p><p>7-15天稳定送达</p>")
            codes = [x["code"] for x in mod.audit(Path(d))["findings"]]
            self.assertIn("AIR_TRANSIT_UNVERIFIED", codes)
            self.assertIn("LAND_TRANSIT_UNVERIFIED", codes)

    def test_code_only_claim_is_not_treated_as_visible(self):
        with tempfile.TemporaryDirectory() as d:
            self.make_site(d, "<script>const message = '48小时到达中国';</script>普通服务咨询")
            codes = [x["code"] for x in mod.audit(Path(d))["findings"]]
            self.assertNotIn("AIR_TRANSIT_UNVERIFIED", codes)

    def test_incorrect_official_url_and_contact_are_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.make_site(d)
            p["officialPages"]["service"] = "https://example.com/not-ours.html"
            p["contact"]["whatsapp"] = "https://wa.me/0000000000"
            (Path(d) / "ai-entity.json").write_text(json.dumps(p), encoding="utf-8")
            codes = [x["code"] for x in mod.audit(Path(d))["findings"]]
            self.assertIn("OFFICIAL_PAGE_INVALID_OR_MISSING", codes)
            self.assertIn("CONTACT_NOT_ALIGNED", codes)

    def test_encoded_path_escape_is_rejected(self):
        self.assertIsNone(mod._local_official_path(
            "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/dir/%2e%2e/outside.html"
        ))


if __name__ == "__main__":
    unittest.main()
