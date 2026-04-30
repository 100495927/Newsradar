from __future__ import annotations

import unicodedata
from typing import List

import httpx
from fastapi import APIRouter, Depends, Query

from ..auth.user import UserInDB
from ..dependencies import get_current_user
from .dictionary import fallback_lookup

router = APIRouter(tags=["synonyms"])

CONCEPTNET_URL = "https://api.conceptnet.io/query"


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text.lower().strip())
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _fetch_conceptnet(word: str) -> list[str]:
    node = f"/c/es/{_normalize(word).replace(' ', '_')}"
    results: list[str] = []

    for rel in ("/r/Synonym", "/r/RelatedTo"):
        try:
            resp = httpx.get(
                CONCEPTNET_URL,
                params={"node": node, "rel": rel, "limit": 15},
                timeout=5.0,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for edge in data.get("edges", []):
                for side in ("start", "end"):
                    term = edge.get(side, {})
                    if term.get("language") == "es" and term.get("term") != node:
                        label = term.get("label", "")
                        if label and label not in results:
                            results.append(label)
        except Exception:
            continue

        if len(results) >= 3:
            break

    return results[:10]


@router.get("/synonyms", response_model=List[str])
def get_synonyms(
    word: str = Query(..., min_length=1, max_length=100),
    _: UserInDB = Depends(get_current_user),
) -> List[str]:
    """Return synonym/related-word suggestions for a given Spanish word."""
    suggestions = _fetch_conceptnet(word)
    if not suggestions:
        suggestions = fallback_lookup(word)
    # Ensure between 3 and 10 results
    return suggestions[:10]
