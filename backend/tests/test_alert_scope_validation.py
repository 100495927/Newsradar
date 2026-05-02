from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.alertas import routes as alert_routes


class FakeCursor(list):
    pass


class FakeCollection:
    def __init__(self, docs: list[dict] | None = None):
        self.docs = docs or []

    def find(self, query: dict | None = None, projection: dict | None = None):
        return FakeCursor([doc for doc in self.docs if _matches(doc, query or {})])


def test_validate_alert_scope_accepts_consistent_sources_and_channels(monkeypatch) -> None:
    monkeypatch.setattr(
        alert_routes,
        "rss_channels_col",
        FakeCollection(
            [
                {
                    "id": 101,
                    "category_id": 11000000,
                    "information_source_id": 1,
                }
            ]
        ),
    )
    monkeypatch.setattr(
        alert_routes,
        "information_sources_col",
        FakeCollection([{"id": 1}]),
    )

    channels, sources = alert_routes._validate_alert_scope_or_400(
        11000000,
        [101],
        [1],
    )

    assert channels == [101]
    assert sources == [1]


def test_validate_alert_scope_rejects_channel_outside_selected_sources(monkeypatch) -> None:
    monkeypatch.setattr(
        alert_routes,
        "rss_channels_col",
        FakeCollection(
            [
                {
                    "id": 101,
                    "category_id": 11000000,
                    "information_source_id": 2,
                }
            ]
        ),
    )
    monkeypatch.setattr(
        alert_routes,
        "information_sources_col",
        FakeCollection([{"id": 1}, {"id": 2}]),
    )

    with pytest.raises(HTTPException) as exc_info:
        alert_routes._validate_alert_scope_or_400(
            11000000,
            [101],
            [1],
        )

    assert exc_info.value.status_code == 400
    assert "no pertenecen a las fuentes" in str(exc_info.value.detail)


def _matches(doc: dict, query: dict) -> bool:
    for key, expected in query.items():
        actual = doc.get(key)
        if isinstance(expected, dict):
            if "$in" in expected and actual not in expected["$in"]:
                return False
            if "$exists" in expected:
                exists = actual is not None
                if exists != expected["$exists"]:
                    return False
            continue
        if actual != expected:
            return False
    return True
