#!/usr/bin/env python3
"""Probe and compare RSS/XML feed structures across multiple sources.

Outputs:
- Raw XML files per source.
- One JSON summary with structural metadata and field coverage.
- One Markdown matrix for quick human review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import feedparser
import requests

DEFAULT_FEEDS: list[dict[str, str]] = [
    {
        "id": "cnmv_notas_prensa",
        "name": "CNMV Notas de Prensa",
        "url": "https://www.cnmv.es/portal/RSS/RSS.asmx/GetDatos?iID=1",
    },
    {
        "id": "cnmv_info_privilegiada",
        "name": "CNMV Informacion Privilegiada",
        "url": "https://www.cnmv.es/portal/informacion-privilegiada/RSS.asmx/GetNoticiasCNMV",
    },
    {
        "id": "una_al_dia",
        "name": "Una al Dia (Hispasec)",
        "url": "https://feeds.feedburner.com/hispasec/zCAd",
    },
    {
        "id": "bbc_world",
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
    },
    {
        "id": "dsca_noticias",
        "name": "Ministerio DSCA Noticias",
        "url": "https://www.dsca.gob.es/es/rss-noticias.xml",
    },
    {
        "id": "lamoncloa_destacadas",
        "name": "La Moncloa Destacadas",
        "url": "https://www.lamoncloa.gob.es/paginas/rss.aspx",
    },
    {
        "id": "rtve_noticias",
        "name": "RTVE Noticias",
        "url": "https://api2.rtve.es/rss/temas_noticias.xml",
    },
]

CORE_ITEM_FIELDS = [
    "title",
    "link",
    "summary",
    "description",
    "content",
    "published",
    "published_parsed",
    "updated",
    "id",
    "guid",
    "author",
    "authors",
    "tags",
]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    default_output = repo_root / "docs" / "rss_probe"

    parser = argparse.ArgumentParser(description="Analyze RSS/XML structures")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output,
        help="Directory for generated probe artifacts",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=25,
        help="HTTP timeout in seconds per feed",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=40,
        help="Maximum number of items to inspect per feed",
    )
    return parser.parse_args()


def extract_xml_namespaces(xml_text: str) -> dict[str, str]:
    namespaces: dict[str, str] = {}
    for prefix, uri in re.findall(r"xmlns(?::([A-Za-z0-9_\-]+))?=\"([^\"]+)\"", xml_text):
        key = prefix or "default"
        namespaces[key] = uri
    return namespaces


def safe_xml_parse(xml_text: str) -> ET.Element | None:
    try:
        return ET.fromstring(xml_text)
    except ET.ParseError:
        return None


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def xml_first_item_pubdate(root: ET.Element | None) -> str | None:
    if root is None:
        return None

    for node in root.iter():
        if local_name(node.tag).lower() == "item":
            for child in list(node):
                if local_name(child.tag).lower() == "pubdate" and child.text:
                    return child.text.strip()
            return None
    return None


def probe_one_feed(feed_cfg: dict[str, str], timeout: int, max_items: int, raw_dir: Path) -> dict[str, Any]:
    started_at = datetime.now(UTC).isoformat()
    out: dict[str, Any] = {
        "id": feed_cfg["id"],
        "name": feed_cfg["name"],
        "url": feed_cfg["url"],
        "started_at": started_at,
    }

    try:
        response = requests.get(feed_cfg["url"], timeout=timeout, allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException as exc:
        out["status"] = "error"
        out["error"] = f"http_error: {exc}"
        return out

    response.encoding = response.encoding or "utf-8"
    xml_text = response.text
    xml_bytes = xml_text.encode(response.encoding, errors="ignore")

    raw_path = raw_dir / f"{feed_cfg['id']}.xml"
    raw_path.write_text(xml_text, encoding="utf-8")

    parsed = feedparser.parse(xml_bytes)
    entries = list(parsed.entries[:max_items])

    item_field_presence = {field: 0 for field in CORE_ITEM_FIELDS}
    entry_key_counter: Counter[str] = Counter()

    for entry in entries:
        entry_keys = set(entry.keys())
        entry_key_counter.update(entry_keys)
        for field in CORE_ITEM_FIELDS:
            value = entry.get(field)
            if value is not None and value != "":
                item_field_presence[field] += 1

    root = safe_xml_parse(xml_text)
    namespaces = extract_xml_namespaces(xml_text)

    out["status"] = "ok"
    out["http"] = {
        "status_code": response.status_code,
        "content_type": response.headers.get("Content-Type"),
        "final_url": response.url,
    }
    out["xml"] = {
        "root_tag": local_name(root.tag) if root is not None else None,
        "namespaces": namespaces,
        "first_item_pubDate": xml_first_item_pubdate(root),
        "raw_path": str(raw_path),
    }
    feed_channel = parsed.get("feed", {})
    channel_keys: list[str] = []
    if isinstance(feed_channel, dict):
        channel_keys = sorted(str(k) for k in feed_channel.keys())

    out["feedparser"] = {
        "version": parsed.get("version"),
        "bozo": bool(parsed.get("bozo")),
        "bozo_exception": str(parsed.get("bozo_exception")) if parsed.get("bozo") else None,
        "channel_keys": channel_keys,
        "item_count_sampled": len(entries),
        "item_field_presence": item_field_presence,
        "item_key_frequency": dict(sorted(entry_key_counter.items())),
    }
    out["ended_at"] = datetime.now(UTC).isoformat()
    return out


def build_markdown_report(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# RSS Probe Report")
    lines.append("")
    lines.append(f"Generated at: {summary['generated_at']}")
    lines.append("")

    lines.append("## Feed Status")
    lines.append("")
    lines.append("| Feed | Status | Version | Items | Namespaces |")
    lines.append("|---|---|---|---:|---:|")

    ok_entries = [r for r in summary["results"] if r.get("status") == "ok"]

    for result in summary["results"]:
        if result.get("status") != "ok":
            lines.append(f"| {result['id']} | error | - | 0 | 0 |")
            continue

        version = result["feedparser"].get("version") or "unknown"
        item_count = result["feedparser"]["item_count_sampled"]
        namespace_count = len(result["xml"]["namespaces"])
        lines.append(f"| {result['id']} | ok | {version} | {item_count} | {namespace_count} |")

    lines.append("")
    lines.append("## Core Field Coverage")
    lines.append("")
    lines.append("Coverage = ratio of sampled items that include the field.")
    lines.append("")

    lines.append("| Feed | title | link | summary | content | published | authors | tags |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    for result in ok_entries:
        count = max(1, result["feedparser"]["item_count_sampled"])
        fp = result["feedparser"]["item_field_presence"]

        def pct(field: str) -> str:
            return f"{(fp.get(field, 0) / count) * 100:.0f}%"

        lines.append(
            "| "
            + " | ".join(
                [
                    result["id"],
                    pct("title"),
                    pct("link"),
                    pct("summary"),
                    pct("content"),
                    pct("published"),
                    pct("authors"),
                    pct("tags"),
                ]
            )
            + " |"
        )

    lines.append("")
    lines.append("## Quick Structural Notes")
    lines.append("")
    for result in ok_entries:
        first_pubdate = result["xml"].get("first_item_pubDate") or "n/a"
        ns = ", ".join(sorted(result["xml"]["namespaces"].keys())) or "none"
        lines.append(f"- {result['id']}: namespaces=[{ns}], first pubDate='{first_pubdate}'")

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()

    output_dir: Path = args.output_dir
    raw_dir = output_dir / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    results = [
        probe_one_feed(feed, timeout=args.timeout, max_items=args.max_items, raw_dir=raw_dir)
        for feed in DEFAULT_FEEDS
    ]

    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "feed_count": len(DEFAULT_FEEDS),
        "ok_count": sum(1 for r in results if r.get("status") == "ok"),
        "error_count": sum(1 for r in results if r.get("status") != "ok"),
        "results": results,
    }

    json_path = output_dir / "rss_probe_summary.json"
    md_path = output_dir / "rss_probe_matrix.md"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_report(summary), encoding="utf-8")

    print(f"[rss_probe] output_dir={output_dir}")
    print(f"[rss_probe] summary_json={json_path}")
    print(f"[rss_probe] matrix_md={md_path}")
    print(f"[rss_probe] ok={summary['ok_count']} error={summary['error_count']}")

    return 0 if summary["ok_count"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
