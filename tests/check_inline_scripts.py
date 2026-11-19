"""Syntax-check embedded scripts after editing the large legacy homepage.

This is a JavaScript parse check, not a browser E2E or production verification.
"""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

class ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture = False
        self.module = False
        self.current = []
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag != "script":
            return
        info = dict(attrs)
        typ = info.get("type", "")
        self.capture = (not info.get("src") and typ not in ("application/ld+json", "application/json"))
        self.module = typ == "module"
        self.current = []

    def handle_data(self, data):
        if self.capture:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.capture:
            content = "".join(self.current)
            if content.strip():
                self.items.append((content, self.module))
            self.capture = False
            self.current = []


def main():
    parser = ScriptCollector()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as temp:
        for i, (body, module) in enumerate(parser.items):
            filename = Path(temp) / f"homepage-inline-{i}.{'mjs' if module else 'js'}"
            filename.write_text(body, encoding="utf-8")
            subprocess.run(["node", "--check", str(filename)], check=True)
    print(f"PASS: parsed {len(parser.items)} embedded homepage scripts")


if __name__ == "__main__":
    main()
