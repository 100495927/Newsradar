import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_notification_email(to_email: str, subject: str, body: str) -> bool:
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("MAIL_FROM")

    if not all([smtp_server, smtp_user, smtp_password]):
        print("[ERROR] Faltan variables de entorno.")
        return False

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"[ÉXITO] Email enviado a {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Detalle: {e}")
        return False

if __name__ == "__main__":
    # Prueba manual
    send_notification_email("mimilupe08@gmail.com", "Prueba NewsRadar", "Funciona!")