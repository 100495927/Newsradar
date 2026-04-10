# ADR 009: Gestión de Notificaciones vía SMTP (App Password)

**Fecha:** 07-04-2026   
**Decisores:** Equipo NewsRadar  

## Contexto
El sistema de alertas de NewsRadar requiere enviar correos electrónicos a los usuarios. El uso de credenciales directas (usuario/contraseña) de cuentas personales de Gmail representa un riesgo crítico de seguridad y suele ser bloqueado por los mecanismos de protección de Google (OAuth2/Less Secure Apps).

## Decisión
Utilizar el sistema de **App Passwords** (Contraseñas de aplicación) de Google y centralizar la configuración mediante variables de entorno cifradas.

## Motivo
* **Seguridad (Aislamiento):** Las "App Passwords" generan un código único de 16 caracteres que solo sirve para el protocolo SMTP, manteniendo la contraseña maestra de la cuenta a salvo.
* **Compatibilidad:** Permite seguir utilizando la librería estándar `smtplib` de Python sin la complejidad de implementar flujos completos de OAuth2 en esta fase del proyecto.
* **Control de Acceso:** El acceso se puede revocar de forma inmediata desde el panel de seguridad de la cuenta de Google sin afectar a otros servicios o miembros del equipo.

## Consecuencias
* **Configuración Local:** Cada desarrollador debe configurar su `.env` con el código proporcionado. 
* **Prevención de Fugas:** El pipeline de CI (GitHub Actions) valida estrictamente que el archivo `.env` original no se suba al repositorio para evitar la exposición de estas credenciales.
