# ADR 006: Motor de Búsqueda y Almacenamiento Indexado

* **Fecha:** 12-03-2026
* **Decisores:** Equipo NewsRadar

## Contexto
El requisito de NewsRadar de generar nubes de palabras y realizar "matches" de alertas sobre miles de noticias requiere una capacidad de búsqueda semántica y agregación que una base de datos convencional no ofrece de forma nativa.

## Decisión
Implementar **Elasticsearch** (vía Docker).

## Motivo
1. **Full-Text Search:** Permite buscar palabras clave dentro del contenido de las noticias con una latencia mínima.
2. **Agregaciones:** Facilita la generación de las "Word Clouds" mediante su motor de agregación de términos.
3. **Escalabilidad:** Está diseñado para manejar grandes volúmenes de documentos de texto, lo cual es ideal para el histórico de noticias.

## Consecuencias
* Aumenta el consumo de RAM en el entorno Docker (Elasticsearch es exigente en recursos).
* Se debe implementar un "indexer" en el backend para enviar las noticias extraídas a los índices de Elastic.
