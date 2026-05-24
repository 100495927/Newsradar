# Migracion del modelo RSS a `information_sources` + `rss_channels`

Fecha: 2026-05-02

## 1. Resumen ejecutivo

Se ha consolidado un modelo MongoDB normalizado para RSS con tres colecciones canonicas:

- `information_sources`
- `rss_channels`
- `rss_entradas`

El contrato de la API no cambia:

- la fuente de informacion se crea en `/api/v1/information-sources`
- los canales RSS se crean en `/api/v1/information-sources/{source_id}/rss-channels`

Lo que cambia es la interpretacion interna y el almacenamiento real.

## 2. Que significa que `rss_fuentes` estaba "disfrazada"

La expresion "disfrazada" se refiere a que el nombre `rss_fuentes` sugeria una coleccion de fuentes de informacion, pero su shape y su uso real eran los de un catalogo de feeds concretos, es decir, de canales RSS.

Los sintomas eran estos:

- guardaba una `url` de feed, no la URL corporativa o principal del medio
- guardaba `category_id` por documento, algo propio de un canal y no de una fuente logica
- el worker la recorria como lista operativa de feeds a capturar
- una misma cabecera editorial como `El Pais` podia aparecer varias veces, una por cada feed

En la practica, un documento de `rss_fuentes` representaba algo equivalente a:

- "feed de portada de El Pais"
- "feed de politica de ABC"
- "feed internacional de BBC"

Eso no es una `information source` del contrato. Eso es un `rss channel`.

## 3. Como se estaba gestionando `information sources` en la API

La API externa ya estaba pensada en dos niveles:

1. `information source`
2. `rss channel` perteneciente a esa fuente

Ejemplo contractual:

- crear la fuente `El Pais`
- obtener su `id`
- crear despues un canal RSS bajo `/information-sources/{id}/rss-channels`

El problema historico fue que durante una fase intermedia el backend mantuvo las rutas del contrato, pero las persistio sobre una coleccion `rss_fuentes` que no modelaba de forma limpia esa separacion conceptual.

Eso generaba estas confusiones:

- la ruta parecia hablar de una fuente logica, pero internamente podia terminar creando un feed concreto
- el worker leia `rss_fuentes` como lista de canales operativos
- el backend y el worker no siempre compartian la misma fuente de verdad

## 4. Modelo de datos adoptado

### `information_sources`

Representa el medio o fuente logica.

Campos operativos:

- `id`
- `name`
- `url`
- `active`
- `created_at`
- `updated_at`
- `deleted_at`

Ejemplo:

```json
{
  "id": 1,
  "name": "El Pais",
  "url": "https://elpais.com",
  "active": true
}
```

### `rss_channels`

Representa un feed RSS concreto dependiente de una fuente.

Campos operativos:

- `id`
- `information_source_id`
- `url`
- `category_id`
- `active`
- `created_at`
- `updated_at`
- `deleted_at`

Ejemplo:

```json
{
  "id": 101,
  "information_source_id": 1,
  "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/america/portada",
  "category_id": 11000000,
  "active": true
}
```

### `rss_entradas`

Representa una noticia ingerida.

Campos clave:

- `information_source_id`
- `rss_channel_id`
- `source_name`
- `source_url`
- `channel_url`
- `titulo`
- `resumen`
- `link`
- `category_id`
- `fecha_publicacion`
- `fecha_ingestion`
- `hash_deduplicado`

No guarda ya referencia a `rss_fuentes._id` ni un `id_fuente` legacy.

## 5. Por que no se ha embebido

No se embeben canales dentro de `information_sources` porque los canales:

- se crean y borran por separado
- se filtran por categoria
- participan en alertas como recurso seleccionable
- son la unidad operativa que consume el worker RSS

La relacion correcta aqui es 1:N:

- una fuente de informacion tiene muchos canales RSS

## 6. Cambios funcionales aplicados

### Backend

- Las rutas de `information-sources` y `rss-channels` persisten en `information_sources` y `rss_channels`.
- Borrar una fuente hace soft-delete de sus canales.
- Borrar una categoria devuelve `409` si hay canales RSS activos asociados.
- Las alertas validan que los `rss_channels_ids` y `information_sources_ids` sean coherentes con la categoria y entre si.

### RSS worker

- Ya no lee `rss_fuentes`.
- Lee canales activos desde `rss_channels` y resuelve su fuente desde `information_sources`.
- Inserta entradas en `rss_entradas` con `information_source_id` y `rss_channel_id`.

### Alert worker

- Sigue funcionando.
- Filtra siempre por `category_id`.
- Si la alerta trae `rss_channel_ids`, restringe ademas por `rss_channel_id`.
- Si no trae `rss_channel_ids`, el alcance efectivo son todos los canales de la categoria de la alerta.
- Si la alerta trae `information_sources_ids`, intersecta tambien por `information_source_id`.

## 7. Estado de las pruebas

Se han revisado los tests para alinearlos con los nombres y relaciones nuevas:

- tests del worker sobre `rss_entradas` y alertas actualizados a `information_source_id` y `rss_channel_id`
- smoke test renombrado conceptualmente de "fuentes" a "canales"
- test unitario nuevo para `ColeccionRssChannels.lista_canales_activos()`
- test RSS del backend reforzado para comprobar la relacion `source -> channel`

Limitacion del entorno de desarrollo actual:

- la prueba de integracion `backend/tests/test_rss.py::test_rss_workflow` sigue necesitando un Mongo accesible como host `mongodb`

## 8. Conclusiones

La lectura correcta a partir de ahora es esta:

- `information_sources` = entidad editorial o medio
- `rss_channels` = feed RSS concreto de esa fuente
- `rss_entradas` = noticia capturada desde un canal

Si aparece documentacion antigua diciendo que la coleccion canonica RSS es `rss_fuentes`, debe considerarse historica y no vigente para el runtime actual.
