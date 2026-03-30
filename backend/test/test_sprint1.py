import os
import pytest
import pymongo
from src.utils.email_sender import send_notification_email

# TC-02: Verificar variables de entorno
def test_env_vars_presence():
    assert os.getenv("SMTP_SERVER") is not None
    assert os.getenv("SMTP_USER") is not None

# TC-01: Validar formato de email (Simulado)
def test_email_format_validation():
    # Por ahora, como no tenemos validación real, verificamos que el sender no explote con un email mal formado
    result = send_notification_email("", "", "")
    assert result is False

# TC-04: Conexión a MongoDB
def test_mongodb_connection():
    uri = os.getenv("MONGODB_URI")
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command('ping')
        connected = True
    except Exception:
        connected = False
    assert connected is True