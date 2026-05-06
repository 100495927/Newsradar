from __future__ import annotations

from shared.iptc_catalog import resolve_category


def canonicalize_iptc_category(value: str) -> str | None:
    category = resolve_category(value)
    return None if category is None else category.name


def detect_categories_from_tags(raw_tags: list[str]) -> list[str]:
    canonical: list[str] = []
    for raw in raw_tags:
        value = canonicalize_iptc_category(raw)
        if value and value not in canonical:
            canonical.append(value)
    return canonical
