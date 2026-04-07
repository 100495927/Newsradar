# ADR 010: Comunicación entre RSS-Worker y Backend API mediante TCP Sockets

**Fecha:** 07-04-2026  
**Decisores:** Equipo NewsRadar  

## Contexto
El flujo de datos original dependía exclusivamente de que el `backend` consultara MongoDB o Elasticsearch para saber si el `rss-worker` había terminado de procesar nuevas noticias. Para implementar funcionalidades de tiempo real (como notificaciones instantáneas o streaming de logs de extracción), necesitamos un mecanismo de comunicación directa entre ambos servicios que no dependa de la latencia de "polling" a la base de datos.

## Decisión
Implementar un canal de comunicación bidireccional basado en **TCP Sockets** para el intercambio de eventos y estados entre el contenedor del Worker y la API principal.

## Motivo
* **Baja Latencia:** El intercambio de mensajes vía sockets es prácticamente instantáneo comparado con las consultas periódicas a la base de datos.
* **Eficiencia de Recursos:** Evita el consumo innecesario de CPU y red que genera el "polling" constante (preguntar cada pocos segundos si hay datos nuevos).
* **Escalabilidad:** Permite que el Backend notifique al Worker para forzar una extracción inmediata si un usuario añade una fuente nueva desde el frontend.
* **Simplicidad en Python:** El uso de la librería nativa `socket` o `asyncio.streams` permite una implementación ligera sin necesidad de añadir un broker de mensajería pesado (como RabbitMQ o Redis) en este Sprint.

## Consecuencias
* **Configuración de Docker:** Se debe asegurar que el contenedor del Backend exponga el puerto específico del socket y que ambos servicios compartan la misma red (`newsradar_net`).
* **Manejo de Errores:** Se debe implementar una lógica de reintento de conexión (reconnect) en el Worker en caso de que el Backend se reinicie.
* **Seguridad:** El puerto del socket debe estar cerrado al exterior y solo ser accesible internamente dentro de la red de Docker.
