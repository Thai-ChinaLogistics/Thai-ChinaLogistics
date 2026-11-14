"""Scope-bound IndexNow notifier for changed public Thai-China Logistics HTML.

A 200/202 response is notification receipt ONLY, never index/ranking evidence.
Runs only after a live hosted key file is verified, and never on PR branches.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ORIGIN = "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/"
HOST = "thai-chinalogistics.github.io"
INDEXNOW_API = "https://api.indexnow.org/indexnow"
MAX_URLS_PER_RUN = 25


def prepare_changed_urls(changed_files: list[str], root: Path) -> list[str]:
    """Only changed/additional root-level public HTML pages on our owned path."""
    urls = set()
    for source in changed_files:
        path = source.strip()
        if not path or "/" in path or "\\" in path:
            continue
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*\.html", path):
            continue
        if path in {"admin.html"} or path.startswith("google"):
            continue
        f = root / path
        if not f.is_file():
            continue  # Deleted pages need a separately validated deletion flow.
        html = f.read_text(encoding="utf-8")
        if re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', html, re.I):
            continue
        urls.add(ORIGIN if path == "index.html" else ORIGIN + path)
    return sorted(urls)


def discover_key_file(root: Path) -> tuple[Path, str] | None:
    matches = [p for p in root.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}\.txt", p.name)]
    if len(matches) != 1:
        return None
    p = matches[0]
    key = p.stem
    if p.read_text(encoding="utf-8").strip() != key:
        return None
    return p, key


def _check_hosted_key(url: str, key: str, *, transport) -> bool:
    try:
        request = Request(url, headers={"User-Agent": "ThaiChinaLogistics-IndexNow/1.0"})
        with transport(request, timeout=8) as response:
            return (
                response.geturl() == url
                and getattr(response, "status", 0) == 200
                and response.read(256).strip() == key.encode("utf-8")
            )
    except (HTTPError, URLError, OSError, TimeoutError):
        return False


def run_submission(root: Path, changed_files: list[str], *, transport=None) -> dict:
    transport = transport or urlopen
    urls = prepare_changed_urls(changed_files, root)
    report = {
        "protocol": "IndexNow",
        "transport": "api.indexnow.org",
        "status": "NO_CHANGED_PUBLIC_PAGES",
        "candidate_count": len(urls),
        "submitted_count": 0,
        "http_status": None,
        "indexing_verified": False,
        "ai_recommendation_verified": False,
        "urls": urls,
    }
    if not urls:
        return report
    if len(urls) > MAX_URLS_PER_RUN:
        report["status"] = "BLOCKED_URL_LIMIT"
        return report
    found = discover_key_file(root)
    if not found:
        report["status"] = "KEY_FILE_NOT_CONFIGURED"
        return report
    key_file, key = found
    key_location = ORIGIN + key_file.name
    if not _check_hosted_key(key_location, key, transport=transport):
        report["status"] = "KEY_NOT_PUBLIC"
        return report

    payload = {
        "host": HOST, "key": key, "keyLocation": key_location, "urlList": urls
    }
    request = Request(
        INDEXNOW_API,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "ThaiChinaLogistics-IndexNow/1.0"},
        method="POST",
    )
    try:
        with transport(request, timeout=12) as response:
            response.read(1024)
            status = getattr(response, "status", 0)
        report["http_status"] = status
        report["status"] = (
            "RECEIVED_NOT_INDEXED" if status == 200 else
            "RECEIVED_PENDING_VERIFICATION" if status == 202 else
            "HTTP_UNEXPECTED"
        )
        if status in (200, 202):
            report["submitted_count"] = len(urls)
    except HTTPError as e:
        report["http_status"] = e.code
        report["status"] = "HTTP_ERROR"
    except (URLError, OSError, TimeoutError) as e:
        report["status"] = "NETWORK_ERROR"
        report["error_type"] = type(e).__name__
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Notify IndexNow of verified updated public pages.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--changed-files", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source = args.changed_files.read_text(encoding="utf-8").splitlines()
    report = run_submission(args.root.resolve(), source)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("IndexNow: status=%s candidates=%s submitted=%s http=%s (not indexing)" %
          (report["status"], report["candidate_count"], report["submitted_count"], report["http_status"]))
    return 0  # Submission failure is recorded; do not break content-safety CI.


if __name__ == "__main__":
    raise SystemExit(main())
