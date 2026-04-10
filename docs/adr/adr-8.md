# ADR 008: Visualización y Análisis de Datos con Kibana

**Fecha:** 07-04-2026    
**Decisores:** Equipo NewsRadar  

## Contexto
El proyecto requiere una forma eficiente de monitorizar la salud de los índices de Elasticsearch y validar que los datos extraídos de los feeds RSS se están indexando correctamente. Desarrollar interfaces personalizadas en el Frontend para tareas de administración y depuración en fases tempranas del Sprint restaría tiempo al desarrollo de las funcionalidades principales.

## Decisión
Implementar **Kibana** como herramienta de BI (Business Intelligence) y panel de gestión para el clúster de Elasticsearch mediante un contenedor Docker oficial.

## Motivo
* **Integración Nativa:** Al ser parte del Elastic Stack, la compatibilidad con Elasticsearch 9.3.2 es total y no requiere configuración de drivers adicionales.
* **Dashboarding:** Permite crear visualizaciones rápidas (gráficos de barras por fuente, nubes de palabras preliminares) para asegurar que las agregaciones de noticias son coherentes antes de implementarlas en el backend.
* **Depuración de Índices:** Facilita al equipo de desarrollo la inspección de documentos (noticias) en tiempo real y la ejecución de consultas en la consola de "Dev Tools".

## Consecuencias
* **Recursos:** Se añade un servicio adicional al `docker-compose.yml`, lo que incrementa el consumo de memoria RAM en el entorno local (aprox. 1GB adicional).
* **Entorno de CI:** El servicio se incluye en el flujo de integración continua para asegurar la orquestación, pero no se utiliza activamente en los tests automatizados para ahorrar tiempo de ejecución.
