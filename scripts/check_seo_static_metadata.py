"""Regression: static SEO metadata must match existing Chinese default copy.

Only checks pre-existing translations; never approves service claims.
"""
from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

STRICT_PAGES = (
    Path("china-to-thailand.html"),
    Path("luggage-to-china.html"),
    Path("daigou-shipping.html"),
)
DESCRIPTION_ONLY_PAGES = (
    Path("air-freight-to-china.html"),
    Path("buddhist-amulets-to-china.html"),
    Path("chiang-mai-to-china.html"),
    Path("chiang-rai-to-china.html"),
    Path("electronics-to-china.html"),
    Path("hat-yai-to-china.html"),
    Path("koh-samui-to-china.html"),
    Path("land-freight-to-china.html"),
    Path("moving-to-china.html"),
    Path("pattaya-to-china.html"),
    Path("thai-products-to-china.html"),
)
PAGES = STRICT_PAGES + DESCRIPTION_ONLY_PAGES


class HeadMetadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.in_title = False
        self.description = None
        self.html_lang = None
        self.default_lang = None

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "html":
            self.html_lang = fields.get("lang")
            self.default_lang = fields.get("data-lang")
        if tag == "title":
            self.in_title = True
        if tag == "meta" and fields.get("name", "").lower() == "description":
            self.description = fields.get("content")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self):
        return "".join(self.title_parts).strip()


def validate(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    parser = HeadMetadata()
    parser.feed(html)
    marker = "window.TCL_SEO_PAGE_META="
    if marker not in html:
        return [f"{path}: localized page metadata configuration missing"]
    try:
        payload, _ = json.JSONDecoder().raw_decode(html.split(marker, 1)[1].lstrip())
        zh = payload["zh"]
    except (ValueError, KeyError, TypeError) as exc:
        return [f"{path}: cannot parse default-language metadata: {exc}"]
    errors = []
    if parser.html_lang != zh.get("lang") or parser.default_lang != "zh":
        errors.append(f"{path}: HTML language disagrees with default Chinese metadata")
    # The original pilot aligned both fields. Remaining pages retain their existing titles.
    if path in STRICT_PAGES and parser.title != zh.get("title"):
        errors.append(f"{path}: static title differs from existing zh localized title")
    if parser.description != zh.get("description"):
        errors.append(f"{path}: static description differs from existing zh localized description")
    if not 10 <= len(parser.title) <= 65:
        errors.append(f"{path}: title length outside 10-65")
    if not 50 <= len(parser.description or "") <= 180:
        errors.append(f"{path}: description length outside 50-180")
    return errors


if __name__ == "__main__":
    errors = [error for path in PAGES for error in validate(path)]
    if errors:
        raise SystemExit("SEO static metadata regression failed:\n" + "\n".join(errors))
    print(f"PASS: {len(PAGES)} scoped pages use existing zh descriptions; 3 pilot titles verified")
