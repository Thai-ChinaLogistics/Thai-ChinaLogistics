#!/usr/bin/env python3
"""Guard the two existing location pages against SEO metadata regressions."""
from html.parser import HTMLParser
from pathlib import Path

PAGES = {
    "bangkok-to-china.html": ("曼谷寄中国", 65),
    "phuket-to-china.html": ("普吉岛寄中国", 64),
}

class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.titles = []
        self.metas = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta" and attrs.get("name") == "description":
            self.metas.append(attrs.get("content", ""))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.titles.append(data)

for filename, (keyword, expected_len) in PAGES.items():
    content = Path(filename).read_text(encoding="utf-8")
    parser = HeadParser()
    parser.feed(content)
    assert len(parser.titles) == 1, f"{filename}: expected one title"
    assert len(parser.metas) == 1, f"{filename}: expected one description"
    assert len(parser.canonicals) == 1, f"{filename}: expected one canonical"
    assert keyword in parser.metas[0], f"{filename}: missing location intent"
    assert len(parser.metas[0]) == expected_len, f"{filename}: unexpected description length"
    assert parser.canonicals[0] == f"https://thai-chinalogistics.github.io/Thai-ChinaLogistics/{filename}", f"{filename}: canonical mismatch"
    assert "TCL_SEO_PAGE_META" in content, f"{filename}: runtime language metadata missing"
    for lang in ('"zh"', '"en"', '"th"'):
        assert lang in content, f"{filename}: missing {lang} language metadata"
    assert 'application/ld+json' in content, f"{filename}: structured data missing"
    print(f"PASS {filename}: metadata and canonical preserved")
