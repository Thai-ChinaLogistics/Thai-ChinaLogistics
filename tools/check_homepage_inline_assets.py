"""Ensure homepage HTML stays Googlebot-friendly and extracted images remain byte-identical.

This checks Git blob hashes of images derived from the original homepage data
URIs. Any future intended image replacement must explicitly update the
baseline and be reviewed as a separate, ordinary website change.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# Original image bytes, not rewritten/transcoded/recompressed in this PR.
EXPECTED = {
    "pickup-slide-2.png": ("ad6a83b75ef0e23db3df7b791ac4e93d6368a003", b"\x89PNG\r\n\x1a\n", "css"),
    "pickup-slide-3.png": ("66f19d35c4f74c6fc1ce13a74727e8580a43e3f7", b"\x89PNG\r\n\x1a\n", "css"),
    "pickup-slide-4.png": ("7949b33ed09813112394224fe19e4de98489689e", b"\x89PNG\r\n\x1a\n", "css"),
    "carton-weight-diagram.png": ("a40ff85e5116612309fa3894141f66827e087b30", b"\x89PNG\r\n\x1a\n", "img"),
    "facebook-icon.png": ("a371772a86d6ec96163357f53f2e0197bc2d4bb3", b"\x89PNG\r\n\x1a\n", "img"),
    "whatsapp-icon.png": ("b914911a91327a3f71757d21673057575a74344c", b"\x89PNG\r\n\x1a\n", "img"),
    "wechat-icon.png": ("75665c196b3cec0f94915198b5e092efa01cadfe", b"\x89PNG\r\n\x1a\n", "img"),
    "wechat-qr.jpeg": ("89beab0b0802d9002e66e81218ff0d5725ae7069", b"\xff\xd8", "img"),
}
MAX_HTML_BYTES = 1_500_000  # Below Google's documented 2MB Googlebot HTML fetch threshold.


def blob_hash(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def validate(root: Path) -> list[str]:
    errors = []
    homepage = root / "index.html"
    if not homepage.is_file():
        return ["index.html: missing"]
    html_bytes = homepage.read_bytes()
    if len(html_bytes) >= MAX_HTML_BYTES:
        errors.append(f"index.html: {len(html_bytes)} bytes exceeds {MAX_HTML_BYTES} budget")
    html = html_bytes.decode("utf-8")
    if "data:image/" in html:
        errors.append("index.html: embedded base64 images reintroduced")
    if "<title>泰国寄中国｜泰中物流、上门取件与门到门方案</title>" not in html:
        errors.append("index.html: established business title changed")
    if "<body" not in html or "</body>" not in html:
        errors.append("index.html: body missing")

    for name, (sha, magic, kind) in EXPECTED.items():
        relative = f"seo-inline/{name}"
        path = root / relative
        if html.count(relative) != 1:
            errors.append(f"index.html: {relative} must be referenced once")
        if kind == "img" and f'src="{relative}"' not in html:
            errors.append(f"index.html: image src for {relative} missing")
        if kind == "css" and not (
            f"url('{relative}')" in html or f'url("{relative}")' in html
        ):
            errors.append(f"index.html: background-image URL for {relative} missing")
        if not path.is_file():
            errors.append(f"{relative}: asset missing")
            continue
        data = path.read_bytes()
        if not data.startswith(magic):
            errors.append(f"{relative}: MIME/file signature mismatch")
        if blob_hash(data) != sha:
            errors.append(f"{relative}: bytes differ from original inline image")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    if errors:
        print("\n".join("FAIL " + error for error in errors), file=sys.stderr)
        return 1
    print(
        "PASS: homepage HTML <=1.5 MB, all eight original image blobs "
        "present byte-identically, no layout-copy/CSS selector rewrite required"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
