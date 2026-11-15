"""Validate AI GEO evidence JSONL without contacting any external service.

Usage: python scripts/validate_geo_evidence.py path/to/evidence.jsonl
Exits nonzero on unverifiable or contradictory observed claims.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

PLATFORMS = {"doubao", "kimi", "deepseek"}
STATUSES = {"NOT_TESTED", "UNKNOWN", "BLOCKED", "OBSERVED"}
FIELDS = {
    "checked_at_iso8601", "platform", "query_id", "exact_prompt",
    "run_status", "search_enabled", "matched_url", "search_hit",
    "cited", "mentioned", "recommended", "source_url_or_artifact",
}
TARGET_HOST = "thai-chinalogistics.github.io"
TARGET_PREFIX = "/Thai-ChinaLogistics/"


def validate_record(row: dict, line_number: int) -> list[str]:
    errors = []
    prefix = f"line {line_number}"
    if not isinstance(row, dict):
        return [f"{prefix}: expected JSON object"]
    missing = FIELDS - row.keys()
    if missing:
        errors.append(f"{prefix}: missing fields: {', '.join(sorted(missing))}")
        return errors
    if row["platform"] not in PLATFORMS:
        errors.append(f"{prefix}: invalid platform")
    if row["run_status"] not in STATUSES:
        errors.append(f"{prefix}: invalid run_status")
    if not isinstance(row["query_id"], int) or isinstance(row["query_id"], bool) or not 1 <= row["query_id"] <= 12:
        errors.append(f"{prefix}: query_id must be an integer 1..12")
    if not isinstance(row["exact_prompt"], str) or not row["exact_prompt"].strip():
        errors.append(f"{prefix}: exact_prompt must be nonempty")
    timestamp = row["checked_at_iso8601"]
    if row["run_status"] == "OBSERVED":
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError("timezone missing")
        except (ValueError, TypeError, AttributeError):
            errors.append(f"{prefix}: OBSERVED requires timezone-aware checked_at_iso8601")
    elif timestamp not in (None, ""):
        errors.append(f"{prefix}: non-observed status must not claim a test timestamp")
    for field in ("search_enabled", "search_hit", "cited", "mentioned", "recommended"):
        value = row[field]
        if value is not None and type(value) is not bool:
            errors.append(f"{prefix}: {field} must be boolean or null")
        if row["run_status"] != "OBSERVED" and value is not None:
            errors.append(f"{prefix}: {field} must be null until OBSERVED")
    link = row["matched_url"]
    matched = False
    if link is not None:
        if not isinstance(link, str):
            errors.append(f"{prefix}: matched_url must be URL or null")
        else:
            u = urlparse(link)
            matched = u.scheme == "https" and u.hostname == TARGET_HOST and (u.path == TARGET_PREFIX[:-1] or u.path.startswith(TARGET_PREFIX))
            if not matched:
                errors.append(f"{prefix}: matched_url must be owned HTTPS project-path URL")
    if row["run_status"] != "OBSERVED" and link is not None:
        errors.append(f"{prefix}: matched_url must be null until OBSERVED")
    if row["run_status"] == "OBSERVED":
        evidence = row["source_url_or_artifact"]
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(f"{prefix}: OBSERVED requires traceable evidence")
        if row["recommended"] is True and row["query_id"] > 10:
            errors.append(f"{prefix}: brand-prompt control cannot count as organic recommendation")
        if row["recommended"] is True and row["mentioned"] is not True:
            errors.append(f"{prefix}: recommended=true requires mentioned=true")
        if row["cited"] is True and link is None:
            errors.append(f"{prefix}: cited=true requires exact matched_url")
        if row["search_hit"] is True and link is None:
            errors.append(f"{prefix}: search_hit=true requires exact matched_url")
    return errors


def validate_file(path: Path) -> list[str]:
    errors = []
    if not path.is_file():
        return [f"missing file: {path}"]
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {n}: malformed JSON: {exc.msg}")
            continue
        errors.extend(validate_record(row, n))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    errors = validate_file(args.evidence)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"FAIL: {len(errors)} evidence validation error(s)", file=sys.stderr)
        return 1
    print("PASS: GEO evidence schema and claim gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
