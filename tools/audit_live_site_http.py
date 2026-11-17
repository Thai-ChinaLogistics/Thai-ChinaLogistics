"""Independent production HTTP smoke evidence for the Thai-China Logistics site.

Runs from a network-capable CI runner with fixed first-party URLs only.
Never claims Googlebot access, Google indexing, AI citations, or that the
current pull-request files are deployed. Does not mutate external resources.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from audit_sitemap_pages import BASE_URL, PageParser

MAX_BYTES = 2_000_000
TIMEOUT_SECONDS = 12
HOST_ROOT = "https://thai-chinalogistics.github.io"
PROBES = (
    ("homepage", BASE_URL, "html", True),
    ("sitemap", BASE_URL + "sitemap.xml", "xml", True),
    ("express", BASE_URL + "thailand-to-china-express.html", "html", True),
    ("pickup", BASE_URL + "thailand-to-china-pickup.html", "html", True),
    ("pricing", BASE_URL + "thailand-to-china-price.html", "html", True),
    # Informational only. The shared Github Pages host root may legitimately
    # lack a robots.txt. A 404 here is not evidence of robots blocking.
    ("host_root_robots", HOST_ROOT + "/robots.txt", "text", False),
)


def probe(name: str, url: str, kind: str, *, required: bool,
          opener=None) -> dict:
    opener = opener or urlopen
    result = {"name": name, "url": url, "required": required,
              "http_status": None, "result": "UNKNOWN"}
    start = monotonic()
    try:
        request = Request(url, headers={
            "User-Agent": "ThaiChinaLogistics-SEO-Evidence/1.0",
            "Accept": "text/html,application/xml,text/xml,text/plain,*/*",
            "Accept-Encoding": "identity",
        })
        with opener(request, timeout=TIMEOUT_SECONDS) as response:
            result["http_status"] = int(response.status)
            result["final_url"] = response.geturl()
            result["content_type"] = response.headers.get("Content-Type", "")
            result["x_robots_tag"] = response.headers.get("X-Robots-Tag", "")
            body = response.read(MAX_BYTES + 1)
    except HTTPError as exc:
        result["http_status"] = exc.code
        result["result"] = "ORIGIN_HTTP_ERROR"
        return result
    except (URLError, OSError, TimeoutError, ValueError) as exc:
        result["result"] = "NETWORK_ERROR"
        result["error_type"] = type(exc).__name__
        # Network/tool-layer failures are NOT HTTP 404, 500 or an index verdict.
        return result
    finally:
        result["elapsed_ms"] = round((monotonic() - start) * 1000)

    result["content_length_read"] = len(body)
    result["sha256_of_read_body"] = sha256(body).hexdigest()
    if len(body) > MAX_BYTES:
        result["result"] = "BODY_TOO_LARGE"
        return result
    if result["http_status"] != 200:
        result["result"] = "ORIGIN_HTTP_ERROR"
        return result
    if result["final_url"] != url:
        result["result"] = "UNEXPECTED_REDIRECT"
        return result
    if kind == "text":
        result["result"] = "HTTP_200"
        return result
    if "noindex" in result["x_robots_tag"].lower():
        result["result"] = "HEADER_NOINDEX"
        return result
    try:
        if kind == "xml":
            if "xml" not in result["content_type"].lower():
                result["result"] = "UNEXPECTED_CONTENT_TYPE"
                return result
            root = ET.fromstring(body)
            locs = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            result["sitemap_loc_count"] = len(locs)
            result["result"] = "PASS" if root.tag.endswith("}urlset") and locs else "INVALID_SITEMAP"
        else:
            if "html" not in result["content_type"].lower():
                result["result"] = "UNEXPECTED_CONTENT_TYPE"
                return result
            parser = PageParser()
            parser.feed(body.decode("utf-8"))
            parser.close()
            result["title_present"] = bool("".join(parser.title_parts).strip())
            result["canonical_is_self"] = parser.canonicals == [url]
            result["noindex_meta"] = any("noindex" in str(x).lower() for x in parser.robots)
            result["result"] = ("PASS" if result["title_present"] and
                                result["canonical_is_self"] and not result["noindex_meta"]
                                else "HTML_META_REVIEW")
    except (UnicodeError, ValueError, ET.ParseError):
        result["result"] = "BODY_PARSE_ERROR"
    return result


def audit(opener=None) -> dict:
    probes = [probe(name, url, kind, required=required, opener=opener)
              for name, url, kind, required in PROBES]
    mandatory = [x for x in probes if x["required"]]
    return {
        "schema_version": "1.0",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "from": "github_actions_runner_external_https_get",
        "only_checks": "production_url_http_status_source_content_type_canonical",
        "does_not_prove": [
            "googlebot_can_crawl", "google_indexed", "sitemap_processed_by_google",
            "ai_recommended", "pull_request_deployed"
        ],
        "read_only": True,
        "summary": {
            "required": len(mandatory),
            "passed": sum(x["result"] == "PASS" for x in mandatory),
            "network_unknown": sum(x["result"] == "NETWORK_ERROR" for x in mandatory),
            "status": "HTTP_SOURCE_CHECK_PASS" if all(
                x["result"] == "PASS" for x in mandatory
            ) else "REVIEW_REQUIRED",
        },
        "probes": probes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    # Diagnostic data only: transient network errors should not bypass or
    # accidentally block the *separate* source/semantic safety gates.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
