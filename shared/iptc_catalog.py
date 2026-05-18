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
        return str(self.id).zfill(8)


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


def get_category_by_id(category_id: int) -> IPTCTopLevelCategory | None:
    return _BY_ID.get(category_id)


def get_category_by_code(code: str) -> IPTCTopLevelCategory | None:
    cleaned = str(code).strip()
    if not cleaned or not cleaned.isdigit():
        return None
    return _BY_CODE.get(cleaned.zfill(8))


def resolve_category(value: str | int | None) -> IPTCTopLevelCategory | None:
    if value is None:
        return None
    if isinstance(value, int):
        return get_category_by_id(value)

    cleaned = str(value).strip()
    if not cleaned:
        return None
    if cleaned.isdigit():
        return get_category_by_code(cleaned)

    normalized = _normalize_text(cleaned)
    return _BY_NAME.get(normalized)


def as_public_dicts() -> list[dict[str, int | str]]:
    return [
        {"id": category.id, "name": category.name, "source": category.source}
        for category in IPTC_TOP_LEVEL_CATEGORIES
    ]
