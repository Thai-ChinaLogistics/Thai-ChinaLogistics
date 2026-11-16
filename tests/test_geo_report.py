"""Tests for GEO reporting: no fabricated negatives, proper denominators."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from report_geo_visibility import build_markdown, summarize


def record(platform="kimi", query_id=2, **kwargs):
    x = {
        "checked_at_iso8601": "2026-11-15T10:00:00+00:00",
        "platform": platform,
        "query_id": query_id,
        "exact_prompt": "泰国寄中国上门取件如何选择？",
        "run_status": "OBSERVED",
        "search_enabled": True,
        "matched_url": "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/thailand-to-china-express.html",
        "search_hit": True,
        "cited": True,
        "mentioned": True,
        "recommended": True,
        "source_url_or_artifact": "fixture/synthetic-test.json",
    }
    x.update(kwargs)
    return x


class GeoReportTests(unittest.TestCase):
    def summarize_rows(self, rows):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ledger.jsonl"
            path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
            return summarize(path)

    def test_empty_ledger_is_not_zero_percent(self):
        report = build_markdown(self.summarize_rows([]))
        self.assertIn("未验证", report)
        self.assertNotIn("0%", report)

    def test_genuine_observation_counts(self):
        out = self.summarize_rows([record()])
        self.assertEqual(out["kimi"]["results"]["recommended"], {"positive": 1, "tested": 1})

    def test_brand_query_excluded_from_organic_recommendations(self):
        out = self.summarize_rows([record(query_id=11, recommended=False)])
        self.assertEqual(out["kimi"]["results"]["recommended"]["tested"], 0)
        self.assertEqual(out["kimi"]["results"]["cited"]["tested"], 1)

    def test_unknown_status_is_not_negative(self):
        x = record(run_status="UNKNOWN", checked_at_iso8601=None, search_enabled=None,
                   matched_url=None, search_hit=None, cited=None, mentioned=None,
                   recommended=None, source_url_or_artifact=None)
        out = self.summarize_rows([x])
        self.assertEqual(out["kimi"]["results"]["recommended"]["tested"], 0)

    def test_duplicate_question_uses_latest(self):
        old = record(recommended=False, checked_at_iso8601="2026-11-14T10:00:00+00:00")
        new = record(recommended=True, checked_at_iso8601="2026-11-15T10:00:00+00:00")
        out = self.summarize_rows([old, new])
        self.assertEqual(out["kimi"]["results"]["recommended"], {"positive": 1, "tested": 1})

    def test_timezone_offsets_use_actual_instant(self):
        older = record(
            recommended=False,
            checked_at_iso8601="2026-11-16T23:30:00+07:00",
        )
        newer = record(
            recommended=True,
            checked_at_iso8601="2026-11-16T17:00:00+00:00",
        )
        out = self.summarize_rows([older, newer])
        self.assertEqual(out["kimi"]["results"]["recommended"],
                         {"positive": 1, "tested": 1})

    def test_missing_evidence_rejected(self):
        with self.assertRaises(ValueError):
            self.summarize_rows([record(source_url_or_artifact=None)])


if __name__ == "__main__":
    unittest.main()
