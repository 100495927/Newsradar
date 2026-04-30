from __future__ import annotations

from typing import Iterable


def normalize_text(value: object) -> str:
    # casefold cubre mejor mayusculas/minusculas internacionales que lower().
    if value is None:
        return ""
    return str(value).casefold()


def clean_descriptors(descriptors: Iterable[object] | None) -> list[str]:
    if not descriptors:
        return []

    cleaned: list[str] = []
    seen: set[str] = set()
    for descriptor in descriptors:
        # Mongo puede contener valores heredados o incompletos; se ignoran aqui.
        if descriptor is None:
            continue
        value = str(descriptor).strip()
        key = value.casefold()
        if value and key not in seen:
            cleaned.append(value)
            seen.add(key)
    return cleaned


def find_matched_descriptors(entry: dict, descriptors: Iterable[object] | None) -> list[str]:
    # De momento el requisito se cubre buscando en titulo y resumen del RSS.
    haystack = " ".join(
        [
            normalize_text(entry.get("titulo")),
            normalize_text(entry.get("resumen")),
        ]
    )

    matches: list[str] = []
    for descriptor in clean_descriptors(descriptors):
        if descriptor.casefold() in haystack:
            matches.append(descriptor)
    return matches
