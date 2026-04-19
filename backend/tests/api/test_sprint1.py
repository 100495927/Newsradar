import os
import pymongo

from shared.utils.email_sender import send_notification_email

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
    # Añadimos directConnection=True y subimos el timeout
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000, directConnection=True)
    try:
        client.admin.command('ping')
        connected = True
    except Exception as e:
        print(f"DEBUG Mongo Error: {e}")
        connected = False
    assert connected is True
