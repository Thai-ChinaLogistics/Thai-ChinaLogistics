"""Offline, read-only audit of public Thai-China Logistics entity and claim consistency.

Emits evidence-backed REVIEW_REQUIRED findings; never edits business statements.
It cannot prove a service is actually offered, a transit promise is accurate,
or a search/AI crawler visited a page. Requires Python 3.11+ stdlib only.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

ORIGIN = "https://thai-chinalogistics.github.io"
PROJECT_PATH = "/Thai-ChinaLogistics/"
PROMISES = (
    ("AIR_TRANSIT_UNVERIFIED", "48小时到达中国"),
    ("LAND_TRANSIT_UNVERIFIED", "7-15天稳定送达"),
)


class VisibleTextParser(HTMLParser):
    """Parse readable text, excluding code/script/style and hidden templates."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template", "noscript"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "template", "noscript"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def visible_text(raw_html: str) -> str:
    p = VisibleTextParser()
    p.feed(raw_html)
    return re.sub(r"\s+", " ", " ".join(p.parts)).strip()


def _finding(code: str, source: str, evidence: str, next_step: str) -> dict:
    return {"status": "REVIEW_REQUIRED", "code": code, "source": source,
            "evidence_excerpt": evidence[:220], "next_step": next_step}


def _local_official_path(value: str) -> Path | None:
    if not isinstance(value, str):
        return None
    url = urlsplit(value)
    if url.scheme != "https" or url.netloc != urlsplit(ORIGIN).netloc or url.query or url.fragment:
        return None
    if not url.path.startswith(PROJECT_PATH):
        return None
    tail = unquote(url.path[len(PROJECT_PATH):])
    parts = tail.split("/") if tail else []
    if any(x in {".", "..", ""} for x in parts if x) or "\\" in tail:
        return None
    if not tail:
        return Path("index.html")
    if not tail.endswith(".html"):
        return None
    return Path(tail)


def audit(root: Path) -> dict:
    profile = json.loads((root / "ai-entity.json").read_text(encoding="utf-8"))
    llms = (root / "llms.txt").read_text(encoding="utf-8")
    home = visible_text((root / "index.html").read_text(encoding="utf-8"))
    about = visible_text((root / "about.html").read_text(encoding="utf-8"))
    findings = []

    contact = profile.get("contact") or {}
    for label, value in (("telephone", contact.get("telephone")),
                         ("whatsapp", contact.get("whatsapp"))):
        if not isinstance(value, str) or not value or value not in llms:
            findings.append(_finding("CONTACT_NOT_ALIGNED", "ai-entity.json / llms.txt",
                        f"contact.{label}={value!r} not matched in llms.txt",
                        "核实官方联系方式后统一公开资料，禁止猜测。"))
    if profile.get("canonicalUrl") != ORIGIN + PROJECT_PATH:
        findings.append(_finding("CANONICAL_ENTITY_MISMATCH", "ai-entity.json",
                    str(profile.get("canonicalUrl")), "复核实体主页 URL 与站点规范地址。"))
    name = profile.get("canonicalName")
    if not isinstance(name, str) or name not in llms or name not in about:
        findings.append(_finding("BRAND_ENTITY_MISMATCH", "ai-entity.json / llms.txt / about.html",
                    repr(name), "统一已确认的品牌名称。"))

    for field, url in sorted((profile.get("officialPages") or {}).items()):
        path = _local_official_path(url)
        if path is None or not (root / path).is_file():
            findings.append(_finding("OFFICIAL_PAGE_INVALID_OR_MISSING", "ai-entity.json",
                        f"officialPages.{field}={url}", "确认站点仓真实公开服务页与 canonical。"))

    services = [x.lower().strip() for x in profile.get("services", []) if isinstance(x, str)]
    if "sea freight" in services and re.search(r"海运服务\s*(?:暂未|尚未|未)\s*开放", home):
        findings.append(_finding("SEA_SERVICE_STATUS_CONFLICT", "index.html / ai-entity.json",
                    "homepage: 海运服务暂未开放; ai-entity.json: services contains sea freight",
                    "由业务负责人核实实际开通状态，再统一首页、AI 实体资料和运输服务页；不得自动改成可用。"))

    # PRD enhancements inject text after DOMContentLoaded. A source-only HTML
    # inspection misses these customer-visible statements entirely.
    enhancement_path = root / "prd-enhancements.js"
    if enhancement_path.is_file():
        injected = enhancement_path.read_text(encoding="utf-8")
        unqualified = [
            marker for marker in ("空运、陆运、海运", "海运/门到门")
            if marker in injected
        ]
        if unqualified:
            findings.append(_finding(
                "DYNAMIC_SEA_ROUTE_CLAIM_REVIEW",
                "prd-enhancements.js",
                ", ".join(unqualified),
                "核对动态注入的海运信息与已确认的实际服务状态，未确认前避免默认写成可用线路。",
            ))

    for code, literal in PROMISES:
        if literal in home:
            findings.append(_finding(code, "index.html", literal,
                    "确认该时效的起止定义、限制条件及业务证据；不能把展示语默认为履约保证。"))

    return {
        "schema_version": "1.0",
        "scope": "offline_source_review_not_independent_service_verification",
        "can_authorize_business_edits": False,
        "finding_count": len(findings),
        "status": "REVIEW_REQUIRED" if findings else "NO_SOURCE_CONFLICT_OBSERVED",
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.site_root)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    # This audit is advisory; reviewed business statements are not auto-edited.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
