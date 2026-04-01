# ADR 005: Librería de Extracción de Feeds

* **Fecha:** 12/03/2026
* **Decisores:** Equipo NewsRadar

## Contexto

La aplicación debe monitorizar al menos 100 canales RSS. Es necesario procesar XMLs de diferentes formatos (RSS 2.0, Atom) de forma estandarizada.

## Decisión

Utilizar la librería **feedparser** (RSS parser para Python).

## Motivo

1. **Robustez:** Es la librería estándar de facto en Python para RSS; maneja automáticamente las variaciones entre formatos de feed y codificaciones de caracteres.
2. **Normalización:** Convierte cualquier entrada XML en un diccionario de Python consistente, simplificando el mapeo a los modelos de Pydantic y su posterior guardado en Elasticsearch.

## Consecuencias

* Se integrará dentro del módulo `worker` o `extractor` del backend.
