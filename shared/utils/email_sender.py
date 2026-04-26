from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_notification_email_with_error(
    to_email: str,
    subject: str,
    body: str,
) -> tuple[bool, str | None]:
    """Envia un correo y devuelve exito + detalle de error si falla."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("MAIL_FROM") or smtp_user

    if not to_email:
        return False, "El usuario destinatario no tiene email configurado"

    if not all([smtp_server, smtp_user, smtp_password, from_email]):
        return False, "Faltan variables SMTP obligatorias en el entorno"

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True, None
    except Exception as exc:  # pragma: no cover - depende del SMTP real
        return False, str(exc)


def send_notification_email(to_email: str, subject: str, body: str) -> bool:
    """Compatibilidad retrocompatible: solo informa si el envio tuvo exito."""
    sent, _ = send_notification_email_with_error(to_email, subject, body)
    return sent
