"""Unit tests for strict GEO evidence validation, no network required."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_geo_evidence.py"
spec = importlib.util.spec_from_file_location("validate_geo_evidence", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sample(**changes):
    row = {
        "checked_at_iso8601": "2026-11-15T14:00:00+07:00",
        "platform": "kimi",
        "query_id": 2,
        "exact_prompt": "在普吉岛寄包裹回中国，怎么找可以上门取件的物流？",
        "run_status": "OBSERVED",
        "search_enabled": True,
        "matched_url": "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/thailand-to-china-express.html",
        "search_hit": True,
        "cited": True,
        "mentioned": True,
        "recommended": True,
        "source_url_or_artifact": "evidence/session-20261115.json",
    }
    row.update(changes)
    return row


class GeoEvidenceValidationTests(unittest.TestCase):
    def test_valid_observed(self):
        self.assertEqual(module.validate_record(sample(), 1), [])

    def test_unknown_is_not_negative(self):
        row = sample(checked_at_iso8601=None, run_status="UNKNOWN",
                     search_enabled=None, matched_url=None, search_hit=None,
                     cited=None, mentioned=None, recommended=None,
                     source_url_or_artifact=None)
        self.assertEqual(module.validate_record(row, 1), [])

    def test_no_evidence_cannot_claim_observed(self):
        self.assertTrue(module.validate_record(sample(source_url_or_artifact=None), 1))

    def test_brand_prompt_cannot_be_organic_recommendation(self):
        self.assertTrue(module.validate_record(sample(query_id=11), 1))

    def test_false_is_not_allowed_for_not_tested(self):
        self.assertTrue(module.validate_record(sample(run_status="NOT_TESTED",
            checked_at_iso8601=None, search_enabled=None, matched_url=None,
            search_hit=False, cited=None, mentioned=None, recommended=None), 1))

    def test_external_domain_is_rejected(self):
        self.assertTrue(module.validate_record(sample(matched_url="https://example.com/"), 1))

    def test_unrelated_github_pages_path_rejected(self):
        self.assertTrue(module.validate_record(sample(matched_url="https://thai-chinalogistics.github.io/other/"), 1))

    def test_citation_requires_specific_url(self):
        self.assertTrue(module.validate_record(sample(matched_url=None), 1))

    def test_recommendation_requires_mention(self):
        self.assertTrue(module.validate_record(sample(mentioned=False), 1))

    def test_observed_needs_timezone(self):
        self.assertTrue(module.validate_record(sample(checked_at_iso8601="2026-11-15T14:00:00"), 1))


if __name__ == "__main__":
    unittest.main()
