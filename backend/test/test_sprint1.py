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
    # Buscamos la URI, si no existe usamos la de root por defecto para el test
    uri = os.getenv("MONGODB_URI", "mongodb://newsradar_root:change_me_root_pwd@mongodb:27017/admin?authSource=admin")
    
    # IMPORTANTE: Añadimos direct_connection=True para evitar líos de réplicas en Docker
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000, directConnection=True)
    
    try:
        # Intentamos el ping en la base de datos que viene en la URI o en 'admin'
        client.admin.command('ping')
        connected = True
    except Exception as e:
        print(f"\nDEBUG Error Mongo: {e}")
        connected = False
    finally:
        client.close()
        
    assert connected is True
