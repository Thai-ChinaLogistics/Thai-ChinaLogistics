"""Fail visible internal workflow markers on public static SEO pages.

Only body text is checked; JS, CSS, templates, head metadata and HTML comments
are not customer-visible text. No content is rewritten by this checker.
"""
from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path

INTERNAL_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")
PUBLIC_HTML_EXCLUDES = {"admin.html"}


class VisibleInternalTokens(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_body = False
        self.skip_depth = 0
        self.found: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        elif tag in {"script", "style", "template", "noscript"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False
        elif tag in {"script", "style", "template", "noscript"}:
            self.skip_depth = max(0, self.skip_depth - 1)

    def handle_data(self, data):
        if not self.in_body or self.skip_depth:
            return
        self.found.extend(INTERNAL_TOKEN.findall(data))


def check_html_text(content: str) -> list[str]:
    parser = VisibleInternalTokens()
    parser.feed(content)
    return sorted(set(parser.found))


def check_public_pages(root: Path) -> dict[str, list[str]]:
    failures = {}
    for path in sorted(root.glob("*.html")):
        if path.name in PUBLIC_HTML_EXCLUDES or path.name.startswith("google"):
            continue
        tokens = check_html_text(path.read_text(encoding="utf-8"))
        if tokens:
            failures[path.name] = tokens
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    failures = check_public_pages(args.root)
    if failures:
        for path, markers in failures.items():
            print(f"FAIL {path}: {', '.join(markers)}")
        raise SystemExit(1)
    print("PASS: public HTML body text contains no all-caps internal workflow identifiers")


if __name__ == "__main__":
    main()
