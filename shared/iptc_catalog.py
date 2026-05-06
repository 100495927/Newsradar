from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class IPTCTopLevelCategory:
    id: int
    name: str
    source: str = "IPTC"

    @property
    def code(self) -> str:
        return str(self.id)


IPTC_TOP_LEVEL_CATEGORIES: tuple[IPTCTopLevelCategory, ...] = (
    IPTCTopLevelCategory(1000000, "Artes, cultura, entretenimiento y medios"),
    IPTCTopLevelCategory(3000000, "Catástrofes y accidentes"),
    IPTCTopLevelCategory(13000000, "Ciencia y tecnología"),
    IPTCTopLevelCategory(16000000, "Conflicto, guerra y paz"),
    IPTCTopLevelCategory(15000000, "Deporte"),
    IPTCTopLevelCategory(4000000, "Economía, negocios y finanzas"),
    IPTCTopLevelCategory(5000000, "Educación"),
    IPTCTopLevelCategory(10000000, "Estilo de vida y tiempo libre"),
    IPTCTopLevelCategory(8000000, "Interés humano, animales, insólito"),
    IPTCTopLevelCategory(9000000, "Mano de obra"),
    IPTCTopLevelCategory(6000000, "Medio ambiente"),
    IPTCTopLevelCategory(17000000, "Meteorología"),
    IPTCTopLevelCategory(2000000, "Policía y justicia"),
    IPTCTopLevelCategory(11000000, "Política"),
    IPTCTopLevelCategory(12000000, "Religión y culto"),
    IPTCTopLevelCategory(7000000, "Salud"),
    IPTCTopLevelCategory(14000000, "Sociedad"),
)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(without_accents.lower().split())


_BY_ID = {category.id: category for category in IPTC_TOP_LEVEL_CATEGORIES}
_BY_NAME = {_normalize_text(category.name): category for category in IPTC_TOP_LEVEL_CATEGORIES}
_BY_CODE = {category.code: category for category in IPTC_TOP_LEVEL_CATEGORIES}

_ALIASES = {
    "arte y entretenimiento": 1000000,
    "artes cultura entretenimiento y medios": 1000000,
    "catastrofes y accidentes": 3000000,
    "ciencia y tecnologia": 13000000,
    "tech": 13000000,
    "technology": 13000000,
    "tecnologia": 13000000,
    "conflicto guerra y paz": 16000000,
    "deporte": 15000000,
    "economia": 4000000,
    "economia negocios y finanzas": 4000000,
    "energy": 4000000,
    "energia": 4000000,
    "finanzas": 4000000,
    "finanzas y mercados": 4000000,
    "fin_mrkt": 4000000,
    "mercados": 4000000,
    "educacion": 5000000,
    "estilo de vida y ocio": 10000000,
    "health": 7000000,
    "interes humano animales insolito": 8000000,
    "justicia derecho y orden publico": 2000000,
    "mano de obra": 9000000,
    "medio ambiente": 6000000,
    "meteorologia": 17000000,
    "policia y justicia": 2000000,
    "politica": 11000000,
    "religion": 12000000,
    "religion y culto": 12000000,
    "salud": 7000000,
    "sec_pol": 11000000,
    "seguridad politica": 11000000,
    "sociedad": 14000000,
    "trabajo": 9000000,
}


def get_category_by_id(category_id: int) -> IPTCTopLevelCategory | None:
    return _BY_ID.get(category_id)


def get_category_by_code(code: str) -> IPTCTopLevelCategory | None:
    return _BY_CODE.get(code)


def resolve_category(value: str | int | None) -> IPTCTopLevelCategory | None:
    if value is None:
        return None
    if isinstance(value, int):
        return get_category_by_id(value)

    cleaned = str(value).strip()
    if not cleaned:
        return None
    if cleaned.isdigit():
        return get_category_by_id(int(cleaned))

    normalized = _normalize_text(cleaned)
    category = _BY_NAME.get(normalized)
    if category is not None:
        return category

    alias_id = _ALIASES.get(normalized)
    if alias_id is None:
        return None
    return get_category_by_id(alias_id)


def as_public_dicts() -> list[dict[str, int | str]]:
    return [
        {"id": category.id, "name": category.name, "source": category.source}
        for category in IPTC_TOP_LEVEL_CATEGORIES
    ]
