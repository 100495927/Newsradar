"""
Test de envío real de email via SMTP.

Ejecutar dentro del contenedor backend (donde las variables SMTP están disponibles):
    docker exec newsradar-backend python -m pytest backend/tests/test_email_send.py -v -s

O desde el host si las variables SMTP están en el entorno local:
    pytest backend/tests/test_email_send.py -v -s
"""
from __future__ import annotations

import os
import smtplib

import pytest

from shared.utils import send_notification_email_with_error

TARGET_EMAIL = "100495680@alumnos.uc3m.es"


def _smtp_configured() -> bool:
    return all([
        os.getenv("SMTP_SERVER"),
        os.getenv("SMTP_USER"),
        os.getenv("SMTP_PASSWORD"),
    ])


# ---------------------------------------------------------------------------
# Tests de diagnóstico SMTP
# ---------------------------------------------------------------------------

def test_smtp_env_vars_present():
    """Verifica que las variables de entorno SMTP están configuradas."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    mail_from = os.getenv("MAIL_FROM")

    print(f"\n  SMTP_SERVER  : {smtp_server}")
    print(f"  SMTP_PORT    : {smtp_port}")
    print(f"  SMTP_USER    : {smtp_user}")
    print(f"  SMTP_PASSWORD: {'***' + smtp_password[-4:] if smtp_password and len(smtp_password) > 4 else '(no configurada)'}")
    print(f"  MAIL_FROM    : {mail_from}")

    assert smtp_server, "SMTP_SERVER no está configurada"
    assert smtp_user, "SMTP_USER no está configurada"
    assert smtp_password, "SMTP_PASSWORD no está configurada"


@pytest.mark.skipif(not _smtp_configured(), reason="Variables SMTP no configuradas")
def test_smtp_connection():
    """Verifica que se puede abrir conexión SMTP con las credenciales configuradas."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    print(f"\n  Conectando a {smtp_server}:{smtp_port} como {smtp_user}...")

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
        print("  Conexión y autenticación SMTP correctas.")
    except smtplib.SMTPAuthenticationError as exc:
        pytest.fail(
            f"Fallo de autenticación SMTP: {exc}\n"
            "  -> Para Gmail debes usar una 'Contraseña de aplicación' (App Password) de 16 caracteres,\n"
            "     no la contraseña normal de la cuenta. Obtenerla en:\n"
            "     https://myaccount.google.com/apppasswords"
        )
    except Exception as exc:
        pytest.fail(f"Error al conectar con el servidor SMTP: {exc}")


@pytest.mark.skipif(not _smtp_configured(), reason="Variables SMTP no configuradas")
def test_send_verification_email_to_target():
    """Envía un email real de verificación a la dirección de destino."""
    verify_link = "http://localhost:5173/verify/test-token-de-prueba-12345"
    subject = "NewsRadar – Test: Verifica tu cuenta"
    body = (
        "Hola,\n\n"
        "Este es un email de prueba generado por el test de integración de NewsRadar.\n\n"
        "Si ves este mensaje, el sistema de envío de emails funciona correctamente.\n\n"
        "Enlace de verificación de prueba (no funcional):\n\n"
        f"{verify_link}\n\n"
        "— El equipo de NewsRadar"
    )

    print(f"\n  Enviando email de prueba a: {TARGET_EMAIL}")

    sent, error = send_notification_email_with_error(TARGET_EMAIL, subject, body)

    if not sent:
        pytest.fail(
            f"El email no se pudo enviar.\n"
            f"  Error: {error}\n\n"
            f"  Causas comunes con Gmail:\n"
            f"  1. La SMTP_PASSWORD es la contraseña normal — Gmail exige App Password.\n"
            f"     Crear una en: https://myaccount.google.com/apppasswords\n"
            f"  2. La cuenta tiene bloqueado el acceso SMTP (verificar en Gmail > Seguridad).\n"
            f"  3. El contenedor no tiene salida a internet en el puerto 587."
        )

    print(f"  Email enviado correctamente a {TARGET_EMAIL}.")
