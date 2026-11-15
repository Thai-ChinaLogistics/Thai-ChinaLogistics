"""Build a conservative Chinese GEO visibility report from VERIFIED-SCHEMA JSONL.

This tool does not search AI products or independently authenticate evidence.
It refuses invalid records, and never treats missing tests as negative results.

Usage:
    python scripts/report_geo_visibility.py evidence.jsonl --output geo-report.md
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from validate_geo_evidence import PLATFORMS, validate_file

LABELS = {"doubao": "豆包", "kimi": "Kimi", "deepseek": "DeepSeek"}
MEASURES = ("search_hit", "cited", "mentioned", "recommended")


def summarize(path: Path) -> dict:
    errors = validate_file(path)
    if errors:
        raise ValueError("Invalid GEO ledger: " + "; ".join(errors))
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    # Only the newest observation per platform, question and search mode
    # counts. This avoids inflating a rate with repeated runs of one prompt.
    latest = {}
    for row in rows:
        if row["run_status"] != "OBSERVED":
            continue
        key = (row["platform"], row["query_id"], row["search_enabled"])
        if key not in latest or row["checked_at_iso8601"] > latest[key]["checked_at_iso8601"]:
            latest[key] = row
    output = {}
    for platform in sorted(PLATFORMS):
        observed = [r for r in latest.values() if r["platform"] == platform]
        organic = [r for r in observed if r["query_id"] <= 10]
        counts = {}
        for measure in MEASURES:
            group = organic if measure == "recommended" else observed
            eligible = [r for r in group if r.get(measure) is not None]
            counts[measure] = {
                "positive": sum(r[measure] is True for r in eligible),
                "tested": len(eligible),
            }
        output[platform] = {
            "observed_queries": len({r["query_id"] for r in observed}),
            "organic_queries": len({r["query_id"] for r in organic}),
            "results": counts,
            "evidence_links": sorted({r["source_url_or_artifact"] for r in observed}),
        }
    return output


def build_markdown(result: dict) -> str:
    lines = [
        "# 国内 AI GEO 可见度验证报告",
        "",
        "> 本报告仅汇总经字段校验的测试记录，不证明原始材料的真实性，也不等于平台官方收录统计。",
        "> 无实测结果显示「未验证」，不显示误导性的 0%。",
        "",
        "| 平台 | 已实测问题 | 搜索命中 | AI 引用 | 品牌提及 | 无品牌主动推荐 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    def format_count(item):
        return f'{item["positive"]}/{item["tested"]}' if item["tested"] else "未验证"
    for platform in ("doubao", "kimi", "deepseek"):
        x = result[platform]
        cells = [format_count(x["results"][m]) for m in MEASURES]
        lines.append(f'| {LABELS[platform]} | {x["observed_queries"]}/12 | ' + " | ".join(cells) + " |")
    lines += [
        "",
        "说明：主动推荐仅统计不含品牌名称的第 1–10 题；品牌对照题 11–12 不纳入该指标。",
        "这些数字只代表输入记录里的有效测试，不能推断其他用户会收到相同回答。",
        "",
        "## 证据文件",
        "",
    ]
    for platform in ("doubao", "kimi", "deepseek"):
        links = result[platform]["evidence_links"]
        lines.append(f'- {LABELS[platform]}：' + (", ".join(f"`{x}`" for x in links) if links else "尚无真实测试证据"))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = build_markdown(summarize(args.evidence))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
