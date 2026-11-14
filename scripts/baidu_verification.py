"""Baidu Search Resource Platform ownership proof safety helper.

Only an exact owner-supplied Baidu HTML meta code can be inserted. It is
public site metadata, not a credential for an API and not ownership proof until
the real Baidu webmaster console independently reports successful verification.

CLI:
  python scripts/baidu_verification.py --root .
  python scripts/baidu_verification.py --code '<issued-by-baidu>' --apply
  python scripts/baidu_verification.py --code '<issued-by-baidu>' --check-live
"""
from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OFFICIAL_SITE_URL = "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/"
DOMAIN_ROOT_URL = "https://thai-chinalogistics.github.io/"
VALID_CODE = re.compile(r"[A-Za-z0-9_-]{8,96}\Z")
HEAD = re.compile(r"<head\b[^>]*>", re.IGNORECASE)


class BaiduTagParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.found = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "head":
            self.in_head = True
        if tag == "meta":
            attributes = {str(k).lower(): v for k, v in attrs}
            if str(attributes.get("name") or "").lower() == "baidu-site-verification":
                self.found.append((attributes.get("content"), self.in_head))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag.lower() == "head":
            self.in_head = False


def _scan(html: str) -> BaiduTagParser:
    parser = BaiduTagParser()
    parser.feed(html)
    return parser


def _is_valid_code(code) -> bool:
    return isinstance(code, str) and VALID_CODE.fullmatch(code) is not None


def analyze_html(html: str) -> dict:
    """A live tag is only an HTML state; NEVER a platform verification result."""
    tags = _scan(html).found
    if len(tags) > 1:
        status = "DUPLICATE_BAIDU_META"
    elif tags and not tags[0][1]:
        status = "MALFORMED_TAG_LOCATION"
    elif tags and not _is_valid_code(tags[0][0]):
        status = "MALFORMED_VERIFICATION_CODE"
    elif tags:
        status = "TAG_READY_PENDING_PLATFORM_VERIFICATION"
    else:
        status = "ACCOUNT_TOKEN_REQUIRED"
    return {
        "state": status,
        "meta_count": len(tags),
        "tag_in_head": bool(tags and tags[0][1]),
        "baidu_verified": False,
        "site_url": OFFICIAL_SITE_URL,
        "console_verification_required": True,
    }


def install_tag(html: str, code: str) -> str:
    """Idempotently insert only a validated, account-issued code in <head>."""
    if not _is_valid_code(code):
        raise ValueError("invalid or placeholder Baidu owner verification code")
    tags = _scan(html).found
    status = analyze_html(html)["state"]
    if tags:
        if status == "TAG_READY_PENDING_PLATFORM_VERIFICATION" and tags[0][0] == code:
            return html
        if status == "TAG_READY_PENDING_PLATFORM_VERIFICATION":
            raise ValueError("different existing Baidu owner code; manual review required")
        raise ValueError("existing Baidu ownership tag is malformed or duplicated")
    head = list(HEAD.finditer(html))
    if len(head) != 1:
        raise ValueError("expected exactly one <head> element")
    tag = f'<meta name="baidu-site-verification" content="{code}">'
    match = head[0]
    out = html[:match.end()] + "\n" + tag + html[match.end():]
    if analyze_html(out)["state"] != "TAG_READY_PENDING_PLATFORM_VERIFICATION":
        raise ValueError("inserted code could not be verified within document head")
    return out


def _http_get_small(url: str) -> tuple[int | None, str | None]:
    try:
        req = Request(url, headers={"User-Agent": "ThaiChinaLogistics-OwnerPreflight/1.0"})
        with urlopen(req, timeout=10) as response:
            if response.geturl() != url:
                return getattr(response, "status", None), None
            raw = response.read(32768)
            return getattr(response, "status", None), raw.decode("utf-8", errors="replace")
    except HTTPError as exc:
        return exc.code, None
    except (URLError, OSError, TimeoutError):
        return None, None


def probe_live_site(*, expected_code: str | None) -> dict:
    """Only HTTP/meta existence; Baidu platform status remains UNKNOWN."""
    if expected_code is not None and not _is_valid_code(expected_code):
        raise ValueError("invalid owner code")
    root_status, _ = _http_get_small(DOMAIN_ROOT_URL)
    page_status, body = _http_get_small(OFFICIAL_SITE_URL)
    matched = False
    if page_status == 200 and isinstance(body, str):
        tags = _scan(body).found
        matched = len(tags) == 1 and tags[0] == (expected_code, True) and expected_code is not None
    return {
        "domain_root_http_status": root_status,
        "project_http_status": page_status,
        "project_meta_matches": matched,
        "baidu_platform_verified": False,
        "ownership_status": ("PLATFORM_ACCOUNT_VERIFICATION_REQUIRED" if matched
                             else "HTML_TAG_NOT_LIVE"),
        "domain_root_http_200": root_status == 200,
        "file_verification_ownership_proven": False,
        "site_url": OFFICIAL_SITE_URL,
        "domain_root_url": DOMAIN_ROOT_URL,
        "verification_method_note": "Domain-root files may not be deployable from a GitHub Pages project subpath; test HTML-tag method in official Baidu account.",
        "no_indexing_or_ai_citation_claim": True,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Owner-issued Baidu HTML proof readiness (no automatic verification)")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--code", help="Exact owner-issued value from Baidu Search Resource Platform")
    p.add_argument("--apply", action="store_true", help="Modify index.html only when exact owner code supplied")
    p.add_argument("--check-live", action="store_true", help="Check published tag and domain-root HTTP; never claim ownership verified")
    p.add_argument("--report", type=Path)
    args = p.parse_args(argv)
    if args.apply and args.check_live:
        p.error("choose --apply or --check-live, not both")
    if args.check_live:
        result = probe_live_site(expected_code=args.code)
    else:
        index = args.root / "index.html"
        html = index.read_text(encoding="utf-8")
        if args.apply:
            if not args.code:
                p.error("--apply requires exact --code issued in Baidu webmaster console")
            modified = install_tag(html, args.code)
            if modified != html:
                index.write_text(modified, encoding="utf-8")
            html = modified
        result = analyze_html(html)
        if result["state"].startswith(("DUPLICATE_", "MALFORMED_")):
            print("FAIL: ambiguous or malformed Baidu verification tag")
            return 1
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Baidu readiness: %s; official account verification remains required" %
          (result.get("state") or result.get("ownership_status")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
