"""Read-only static HTML and Sitemap audit for a GitHub Pages project site.

Does not check live HTTP access, Google indexing, business facts or AI citation.
No network access or external dependencies. Outputs REVIEW_REQUIRED evidence.
"""
from __future__ import annotations

import argparse
from datetime import date
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

BASE_URL = "https://thai-chinalogistics.github.io/Thai-ChinaLogistics/"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.h1_count = 0
        self.canonicals = []
        self.descriptions = []
        self.robots = []
        self.jsonld_raw = []
        self.in_title = False
        self.in_ld = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "link" and "canonical" in str(d.get("rel", "")).lower().split():
            self.canonicals.append(d.get("href", ""))
        elif tag == "meta":
            if str(d.get("name", "")).lower() == "description":
                self.descriptions.append(d.get("content", ""))
            if str(d.get("name", "")).lower() == "robots":
                self.robots.append(d.get("content", ""))
        elif tag == "script" and d.get("type", "").lower().strip() == "application/ld+json":
            self.in_ld = True
            self.jsonld_raw.append("")

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.in_ld:
            self.jsonld_raw[-1] += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_ld:
            self.in_ld = False


def map_sitemap_url(url: str) -> str | None:
    if not isinstance(url, str) or not url.startswith(BASE_URL):
        return None
    parsed = urlsplit(url)
    base = urlsplit(BASE_URL)
    if (parsed.scheme != "https" or parsed.netloc != base.netloc
            or parsed.query or parsed.fragment or parsed.username or parsed.password):
        return None
    relative = unquote(parsed.path[len(base.path):])
    if not relative:
        return "index.html"
    parts = relative.split("/")
    if (any(p in {"", ".", ".."} or "\\" in p for p in parts)
            or not relative.lower().endswith(".html")):
        return None
    return "/".join(parts)


def inspect_page(html: str, url: str) -> list[str]:
    parser = PageParser()
    parser.feed(html)
    parser.close()
    issues = []
    if not "".join(parser.title_parts).strip():
        issues.append("MISSING_TITLE")
    if not any(isinstance(x, str) and x.strip() for x in parser.descriptions):
        issues.append("MISSING_DESCRIPTION")
    if parser.h1_count != 1:
        issues.append("H1_COUNT_NOT_ONE")
    if parser.canonicals != [url]:
        issues.append("CANONICAL_NOT_EXACTLY_SELF")
    if any("noindex" in str(x).casefold() for x in parser.robots):
        issues.append("SITEMAP_PAGE_NOINDEX")
    for snippet in parser.jsonld_raw:
        try:
            data = json.loads(snippet)
            if not isinstance(data, (dict, list)):
                raise ValueError("JSON-LD root must be object or array")
        except (json.JSONDecodeError, ValueError):
            issues.append("INVALID_JSONLD")
    return sorted(set(issues))


def audit(root: Path) -> dict:
    tree = ET.parse(root / "sitemap.xml")
    sitemap_urls = []
    findings = []
    for elem in tree.findall(f".//{SITEMAP_NS}url"):
        url = (elem.findtext(f"{SITEMAP_NS}loc") or "").strip()
        lastmod = (elem.findtext(f"{SITEMAP_NS}lastmod") or "").strip()
        sitemap_urls.append(url)
        mapped = map_sitemap_url(url)
        if mapped is None:
            findings.append({"url": url, "code": "INVALID_OR_OUT_OF_SCOPE_SITEMAP_URL"})
            continue
        if lastmod:
            try:
                parsed_date = date.fromisoformat(lastmod[:10])
                if parsed_date > date.today():
                    findings.append({"url": url, "code": "FUTURE_LASTMOD"})
            except ValueError:
                findings.append({"url": url, "code": "INVALID_LASTMOD"})
        target = root / mapped
        if not target.is_file():
            findings.append({"url": url, "code": "SITEMAP_PAGE_MISSING_IN_REPO"})
            continue
        try:
            html = target.read_text(encoding="utf-8")
            for code in inspect_page(html, url):
                findings.append({"url": url, "code": code})
        except (UnicodeError, ValueError):
            findings.append({"url": url, "code": "INVALID_HTML_ENCODING"})
    for url in sorted(set(sitemap_urls)):
        if sitemap_urls.count(url) > 1:
            findings.append({"url": url, "code": "DUPLICATE_SITEMAP_LOC"})

    # Reverse-check the published site's top-level HTML inventory. Without
    # this, omitted but indexable pages appear as a false clean Sitemap.
    # Explicit noindex pages must remain omitted (never auto-submit them).
    published_html = sorted(root.glob("*.html"))
    indexable_html = []
    explicitly_noindex = []
    verification_html = []
    listed_local_paths = {
        p for p in (map_sitemap_url(u) for u in sitemap_urls)
        if p is not None
    }
    for path in published_html:
        try:
            source = path.read_text(encoding="utf-8")
            # Google ownership challenge files are NOT searchable content and
            # must never be inserted into a sitemap to satisfy a count.
            if (re.fullmatch(r"google[A-Za-z0-9_-]{8,64}[.]html", path.name)
                    and source.strip() == f"google-site-verification: {path.name}"):
                verification_html.append(path.name)
                continue
            parser = PageParser()
            parser.feed(source)
            parser.close()
        except (UnicodeError, ValueError):
            findings.append({"url": BASE_URL + path.name,
                             "code": "INVALID_HTML_ENCODING"})
            continue
        if any("noindex" in str(x).casefold() for x in parser.robots):
            explicitly_noindex.append(path.name)
            continue
        indexable_html.append(path.name)
        if path.name not in listed_local_paths:
            findings.append({"url": BASE_URL if path.name == "index.html" else BASE_URL + path.name,
                             "code": "INDEXABLE_HTML_MISSING_FROM_SITEMAP"})
    return {
        "schema_version": "1.0",
        "scope": "repository_only_no_live_crawl_or_index_evidence",
        "can_authorize_edits": False,
        "sitemap_url_count": len(sitemap_urls),
        "unique_url_count": len(set(sitemap_urls)),
        "published_top_level_html_count": len(published_html),
        "indexable_top_level_html_count": len(indexable_html),
        "explicit_noindex_html_count": len(explicitly_noindex),
        "explicit_noindex_paths": explicitly_noindex,
        "verified_ownership_challenge_html_count": len(verification_html),
        "verified_ownership_challenge_paths": verification_html,
        "missing_sitemap_indexable_count": sum(
            x["code"] == "INDEXABLE_HTML_MISSING_FROM_SITEMAP"
            for x in findings
        ),
        "finding_count": len(findings),
        "status": "REVIEW_REQUIRED" if findings else "NO_SOURCE_ISSUES_OBSERVED",
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
