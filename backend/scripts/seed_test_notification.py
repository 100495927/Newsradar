"""Script para inyectar una alerta y notificacion de prueba en la cuenta gmail@gmail.com."""
from datetime import datetime, timezone
import sys
sys.path.insert(0, "/app")

from backend.app.store import alerts_col, notifications_col, next_mongo_id

now = datetime.now(timezone.utc)
uid = 8  # gmail@gmail.com

alert_id = next_mongo_id("alerts")
alerts_col.insert_one({
    "id": alert_id,
    "user_id": uid,
    "name": "Inteligencia Artificial",
    "descriptors": ["inteligencia artificial", "IA", "machine learning"],
    "categories": [{"code": "13000000", "label": "Ciencia y tecnología"}],
    "category_id": 13000000,
    "rss_channel_ids": [],
    "cron_expression": "*/15 * * * *",
    "enabled": True,
    "notification_channels": ["app", "email"],
    "created_at": now,
    "updated_at": now,
})
print(f"Alerta creada: id={alert_id}")

notif_id = next_mongo_id("notifications")
notifications_col.insert_one({
    "id": notif_id,
    "alert_id": alert_id,
    "user_id": uid,
    "timestamp": now,
    "subject": "Actualizacion de Inteligencia Artificial",
    "metrics": [
        {"name": "noticias_encontradas", "value": 8},
        {"name": "noticias_nuevas", "value": 5},
    ],
    "matches": [
        {
            "title": "OpenAI lanza nuevo modelo de IA generativa",
            "link": "https://elpais.com/tecnologia/openai-nuevo-modelo",
            "source": "El Pais",
            "published_at": now,
            "summary": "La empresa presenta su ultimo avance en inteligencia artificial.",
            "matched_descriptors": ["inteligencia artificial", "IA"],
            "category_id": None,
        },
        {
            "title": "Machine learning aplicado a la medicina",
            "link": "https://rtve.es/noticias/ml-medicina",
            "source": "RTVE",
            "published_at": now,
            "summary": "Investigadores usan ML para detectar enfermedades raras.",
            "matched_descriptors": ["machine learning"],
            "category_id": None,
        },
    ],
    "delivery_channels": ["app", "email"],
    "email_status": "sent",
    "email_sent_at": now,
    "email_error": None,
    "read_at": None,
    "created_at": now,
    "updated_at": now,
})
print(f"Notificacion creada: id={notif_id} para alerta {alert_id} (usuario gmail@gmail.com)")
