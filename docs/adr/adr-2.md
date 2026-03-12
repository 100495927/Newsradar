# ADR 002: Sistema de Persistencia de Datos

* **Fecha:** 12/03/2026
* **Decisores:** Equipo NewsRadar (6 miembros)

## Contexto
Los datos de las noticias (RSS) no tienen un esquema rígido y pueden variar entre medios. Además, el sistema debe ser capaz de almacenar grandes volúmenes de artículos de forma eficiente.

## Decisión
Adoptar **MongoDB** como base de datos principal, gestionada mediante un contenedor Docker oficial.

## Motivo
1. **Flexibilidad de Esquema:** Al ser NoSQL basada en documentos (BSON), permite almacenar artículos con diferentes metadatos sin migraciones de base de datos complejas.
2. **Escalabilidad:** Maneja eficientemente las escrituras masivas producidas por el script de extracción de noticias.
3. **Simplicidad de Integración:** Se integra nativamente con objetos JSON/Pydantic usados en el backend.

## Consecuencias
* El equipo debe utilizar el driver asíncrono para no bloquear el bucle de eventos de la API.
* Es necesario configurar volúmenes persistentes en Docker para no perder los datos al reiniciar contenedores.
