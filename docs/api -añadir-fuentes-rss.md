# Estado actual de altas RSS

Este documento describe una implementacion antigua y ya no vigente.

## Lo que ya no existe

- el `rss-worker` ya no expone una API propia
- ya no existe el endpoint interno `POST /fuentes`
- ya no existe persistencia runtime en `col_rss_fuentes`

## Flujo correcto a dia de hoy

La gestion de fuentes y canales se hace desde el backend publico:

1. Crear la fuente de informacion en `POST /api/v1/information-sources`
2. Crear el canal RSS asociado en `POST /api/v1/information-sources/{source_id}/rss-channels`
3. El `rss-worker` lee periodicamente `rss_channels` e `information_sources` desde MongoDB
4. Las noticias capturadas se guardan en `rss_entradas`

## Colecciones canonicas

- `information_sources`
- `rss_channels`
- `rss_entradas`

## Referencia recomendada

Para el detalle completo del cambio de modelo y la razon historica de abandonar `rss_fuentes`, usar:

- `docs/migracion-modelo-rss-2026-05-02.md`
