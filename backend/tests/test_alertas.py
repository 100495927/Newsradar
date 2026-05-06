import pytest
from datetime import datetime, timezone
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from shared.utils import next_run_after, next_run_on_or_after

# Importamos tu app real desde app.py
from app.app import app
from app.alertas import routes as alert_routes
from app.auth.user import UserInDB
from app.alertas.models import AlertCreate

# Creamos el cliente de pruebas con tu aplicación
client = TestClient(app)


class FakeCollection:
    def __init__(self, docs: list[dict] | None = None):
        self.docs = list(docs or [])

    def count_documents(self, query: dict) -> int:
        return sum(
            1
            for doc in self.docs
            if all(doc.get(key) == value for key, value in query.items())
        )

    def insert_one(self, doc: dict):
        self.docs.append(dict(doc))


def _dummy_user() -> UserInDB:
    return UserInDB(
        id=7,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        organization="NewsRadar",
        role_ids=[1],
        password_hash="hashed",
        role="manager",
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        email_verified_at=datetime.now(timezone.utc),
        is_verified=True,
    )

# --- TESTS DE INTEGRACIÓN (API REST) ---

def test_health_endpoint():
    """Prueba que el endpoint de health responde correctamente."""
    # Fíjate que usamos el prefijo /api/v1
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()

def test_crear_alerta_requiere_autenticacion():
    """Prueba que la creación de una alerta sin token de autenticación falla."""
    payload = {
        "name": "Alerta de prueba",
        "descriptors": ["tecnologia", "IA"],
        "cron_expression": "0 12 * * *"
    }
    
    # Intentamos hacer POST a una ruta protegida
    response = client.post("/api/v1/users/1/alerts", json=payload)
    
    # FastAPI/dependencies.py debe bloquearnos por no llevar un JWT válido
    assert response.status_code in [401, 403]

# --- TESTS UNITARIOS (Aislados) ---

def test_modelo_alerta_invalido():
    """Prueba que Pydantic rechaza alertas que no cumplen los requisitos."""
    # El campo 'name' tiene min_length=1. Si pasamos vacío, debe lanzar error.
    with pytest.raises(ValidationError):
        AlertCreate(name="", cron_expression="0 12 * * *")


def test_crear_alerta_persiste_scope_rss_en_mongo(monkeypatch):
    alerts_col = FakeCollection([])
    monkeypatch.setattr(alert_routes, "alerts_col", alerts_col)
    monkeypatch.setattr(alert_routes, "next_mongo_id", lambda _key: 33)
    scheduled_next_run = datetime(2026, 5, 2, 13, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(alert_routes, "next_run_after", lambda *_args, **_kwargs: scheduled_next_run)
    monkeypatch.setattr(alert_routes, "ensure_user_can_access", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(alert_routes, "ensure_user_exists", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        alert_routes,
        "_validate_alert_scope_or_400",
        lambda category_id, rss_channel_ids, information_source_ids: (
            rss_channel_ids,
            information_source_ids,
        ),
    )

    payload = AlertCreate(
        name="Alerta energia",
        descriptors=["energia"],
        categories=[{"code": "4000000", "label": "Economía, negocios y finanzas"}],
        rss_channels_ids=["101"],
        cron_expression="*/15 * * * *",
    )

    alert = alert_routes.create_user_alert(
        user_id=7,
        payload=payload,
        current_user=_dummy_user(),
    )

    assert alert.model_dump() == {
        "id": 33,
        "user_id": 7,
        "name": "Alerta energia",
        "descriptors": ["energia"],
        "categories": [{"code": "4000000", "label": "Economía, negocios y finanzas"}],
        "rss_channels_ids": ["101"],
        "information_sources_ids": [],
        "cron_expression": "*/15 * * * *",
    }
    assert alerts_col.docs[0]["category_id"] == 4000000
    assert alerts_col.docs[0]["rss_channel_ids"] == [101]
    assert alerts_col.docs[0]["information_sources_ids"] == []
    assert alerts_col.docs[0]["enabled"] is True
    assert alerts_col.docs[0]["next_run_at"] == scheduled_next_run


def test_crear_alerta_persiste_varios_rss_channels(monkeypatch):
    alerts_col = FakeCollection([])
    monkeypatch.setattr(alert_routes, "alerts_col", alerts_col)
    monkeypatch.setattr(alert_routes, "next_mongo_id", lambda _key: 34)
    monkeypatch.setattr(
        alert_routes,
        "next_run_after",
        lambda *_args, **_kwargs: datetime(2026, 5, 2, 12, 15, tzinfo=timezone.utc),
    )
    monkeypatch.setattr(alert_routes, "ensure_user_can_access", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(alert_routes, "ensure_user_exists", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        alert_routes,
        "_validate_alert_scope_or_400",
        lambda category_id, rss_channel_ids, information_source_ids: (
            rss_channel_ids,
            information_source_ids,
        ),
    )

    payload = AlertCreate(
        name="Alerta multi-canal",
        descriptors=["energia"],
        categories=[{"code": "4000000", "label": "Economía, negocios y finanzas"}],
        rss_channels_ids=["101", "202", "303"],
        cron_expression="*/15 * * * *",
    )

    alert = alert_routes.create_user_alert(
        user_id=7,
        payload=payload,
        current_user=_dummy_user(),
    )

    assert alert.rss_channels_ids == ["101", "202", "303"]
    assert alerts_col.docs[0]["rss_channel_ids"] == [101, 202, 303]


def test_crear_alerta_rechaza_varias_categorias(monkeypatch):
    monkeypatch.setattr(alert_routes, "alerts_col", FakeCollection([]))
    monkeypatch.setattr(alert_routes, "ensure_user_can_access", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(alert_routes, "ensure_user_exists", lambda *_args, **_kwargs: None)

    payload = AlertCreate(
        name="Alerta multicategoria",
        descriptors=["energia"],
        categories=[
            {"code": "4000000", "label": "Economía, negocios y finanzas"},
            {"code": "15000000", "label": "Deporte"},
        ],
        cron_expression="0 * * * *",
    )

    with pytest.raises(HTTPException) as exc_info:
        alert_routes.create_user_alert(
            user_id=7,
            payload=payload,
            current_user=_dummy_user(),
        )

    assert "exactamente una categor" in str(exc_info.value).lower()


def test_next_run_after_avoids_running_new_alert_in_a_past_minute() -> None:
    reference = datetime(2026, 5, 2, 12, 0, 35, tzinfo=timezone.utc)

    assert next_run_on_or_after("0 * * * *", reference) == datetime(
        2026, 5, 2, 12, 0, tzinfo=timezone.utc
    )
    assert next_run_after("0 * * * *", reference) == datetime(
        2026, 5, 2, 13, 0, tzinfo=timezone.utc
    )
