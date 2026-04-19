from __future__ import annotations

import unicodedata

IPTC_TOP_LEVEL_CATEGORIES = (
    "Artes, cultura, entretenimiento y medios",
    "Catástrofes y accidentes",
    "Economía, negocios y finanzas",
    "Educación",
    "Medio ambiente",
    "Salud",
    "Trabajo",
    "Estilo de vida y ocio",
    "Política",
    "Religión",
    "Ciencia y tecnología",
    "Sociedad",
    "Deporte",
    "Conflicto, guerra y paz",
    "Justicia, derecho y orden público",
)

_IPTC_BY_NORMALIZED = {}
for _categoria in IPTC_TOP_LEVEL_CATEGORIES:
    _IPTC_BY_NORMALIZED[" ".join(_categoria.lower().split())] = _categoria


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(without_accents.lower().split())


_CATEGORY_ALIASES = {
    "arte y entretenimiento": "Artes, cultura, entretenimiento y medios",
    "artes cultura entretenimiento y medios": "Artes, cultura, entretenimiento y medios",
    "catastrofes y accidentes": "Catástrofes y accidentes",
    "economia": "Economía, negocios y finanzas",
    "economia negocios y finanzas": "Economía, negocios y finanzas",
    "finanzas": "Economía, negocios y finanzas",
    "finanzas y mercados": "Economía, negocios y finanzas",
    "mercados": "Economía, negocios y finanzas",
    "energia": "Economía, negocios y finanzas",
    "educacion": "Educación",
    "medio ambiente": "Medio ambiente",
    "salud": "Salud",
    "trabajo": "Trabajo",
    "estilo de vida y ocio": "Estilo de vida y ocio",
    "politica": "Política",
    "seguridad politica": "Política",
    "religion": "Religión",
    "ciencia y tecnologia": "Ciencia y tecnología",
    "tecnologia": "Ciencia y tecnología",
    "tech": "Ciencia y tecnología",
    "sociedad": "Sociedad",
    "deporte": "Deporte",
    "conflicto guerra y paz": "Conflicto, guerra y paz",
    "justicia derecho y orden publico": "Justicia, derecho y orden público",
    "presidente": "Política",
    "actividad": "Política",
    "ciberseguridad": "Ciencia y tecnología",
    "phishing": "Ciencia y tecnología",
    "vulnerabilidades": "Ciencia y tecnología",
    "parches": "Ciencia y tecnología",
    "ransomware": "Ciencia y tecnología",
    "linux": "Ciencia y tecnología",
    "backdoor": "Ciencia y tecnología",
    "microsoft": "Ciencia y tecnología",
    "remoto": "Ciencia y tecnología",
    "teams": "Ciencia y tecnología",
}


def is_iptc_category(value: str) -> bool:
    return _normalize_text(value) in _IPTC_BY_NORMALIZED


def canonicalize_iptc_category(value: str) -> str | None:
    normalized = _normalize_text(value)
    if normalized in _IPTC_BY_NORMALIZED:
        return _IPTC_BY_NORMALIZED[normalized]
    return _CATEGORY_ALIASES.get(normalized)


def normalize_feed_categories(
    raw_categories: list[str] | None,
    fallback_category: str | None = None,
) -> tuple[list[str] | None, list[str] | None]:
    canonical: list[str] = []
    original: list[str] = []

    for raw in raw_categories or []:
        if not raw:
            continue
        cleaned = raw.strip()
        if not cleaned:
            continue
        if cleaned not in original:
            original.append(cleaned)
        canonical_value = canonicalize_iptc_category(cleaned)
        if canonical_value and canonical_value not in canonical:
            canonical.append(canonical_value)

    fallback = canonicalize_iptc_category(fallback_category) if fallback_category else None
    if fallback and fallback not in canonical:
        canonical.append(fallback)

    return (canonical or None, original or None)


__all__ = [
    "IPTC_TOP_LEVEL_CATEGORIES",
    "canonicalize_iptc_category",
    "is_iptc_category",
    "normalize_feed_categories",
]
