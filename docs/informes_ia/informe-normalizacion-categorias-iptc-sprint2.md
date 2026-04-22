# Informe de normalizacion de categorias IPTC

## Objetivo

Corregir la gestion de categorias de noticias RSS para que el campo operativo del sistema exponga solo categorias estandar IPTC, sin perder la traza de las etiquetas originales publicadas por cada medio.

## Problema detectado

Antes de este cambio, el worker RSS guardaba en `rss_entradas.categorias` las etiquetas crudas del feed (`<category>` o `tags`) sin ninguna validacion ni normalizacion. Eso producia dos problemas:

1. Se mezclaban categorias editoriales de cada medio con categorias estandar del sistema.
2. El nombre `source="IPTC"` en backend podia inducir a pensar que las noticias ya estaban clasificadas con IPTC, cuando en realidad no era asi en la ingesta RSS.

Ejemplos reales observados en los feeds del repositorio:

- `Presidente`
- `Actividad`
- `General`
- `ciberseguridad`
- `Phishing`
- `vulnerabilidades`

Estas etiquetas no son categorias IPTC top-level validas tal cual.

## Criterio de correccion aplicado

Se ha aplicado una normalizacion conservadora, con trazabilidad:

- `categorias`: pasa a almacenar solo categorias IPTC canonicas.
- `categorias_raw`: almacena las etiquetas originales del RSS sin modificar.

La normalizacion sigue esta logica:

1. Si una etiqueta del feed ya coincide con una categoria IPTC admitida, se conserva como categoria canonica.
2. Si una etiqueta del feed coincide con un alias o un termino conocido que puede mapearse con seguridad, se transforma a una categoria IPTC top-level.
3. Si el feed no trae una categoria usable, o trae etiquetas editoriales genericas como `General`, se usa la categoria IPTC configurada para la fuente RSS como fallback.

## Motivo de esta estrategia

Se ha elegido este enfoque porque es el mas seguro operativamente:

- Evita exponer etiquetas no estandar como si fueran IPTC.
- Mantiene los datos originales para auditoria y supervision.
- Permite mejorar el mapeo en el futuro sin perder informacion historica.
- Reduce el riesgo de dejar noticias sin clasificar cuando un feed no publica tags validos.

## Cambios realizados

### 1. Modulo de normalizacion IPTC

Se ha creado `rss-worker/rss/iptc.py`.

Responsabilidades del modulo:

- Definir el conjunto de categorias IPTC top-level aceptadas.
- Normalizar texto ignorando mayusculas, tildes y espacios extra.
- Resolver equivalencias conservadoras como:
- `Phishing` -> `Ciencia y tecnologia`
- `ciberseguridad` -> `Ciencia y tecnologia`
- `Presidente` -> `Politica`
- `Actividad` -> `Politica`
- Aplicar fallback por fuente RSS cuando las etiquetas del feed no sirven.

### 2. Fuentes RSS con categoria IPTC configurada

Se ha ampliado `RSSFuente` para aceptar `categoria_iptc`.

Esto permite que cada feed tenga una clasificacion canonica de respaldo, por ejemplo:

- feeds de `mundo` -> `Politica`
- feed de `marca/primera_division` -> `Deporte`
- feed de `moncloa` -> `Politica`

### 3. Entradas RSS con doble capa de categorias

Se ha ampliado `RSSEntrada` para guardar:

- `categorias`: categorias IPTC normalizadas
- `categorias_raw`: categorias originales del feed

### 4. Parser RSS adaptado

`RSSParser.generar()` ya no persiste directamente los `tags` del feed.

Ahora:

- lee las etiquetas originales
- las normaliza con IPTC
- aplica fallback por fuente cuando hace falta
- construye la entrada con categorias canonicas y categorias crudas

### 5. Esquema Mongo actualizado

Se han actualizado los esquemas para admitir los nuevos campos:

- `rss_fuentes.categoria_iptc`
- `rss_entradas.categorias_raw`

Archivos tocados:

- `shared/mongo/colecciones/ColeccionRssFuentes.py`
- `shared/mongo/colecciones/ColeccionRssEntradas.py`
- `scripts/mongo/init-mongo.js`

## Impacto esperado

Despues de este cambio:

- el campo `categorias` de las noticias almacenadas deja de mezclar etiquetas libres con IPTC
- las consultas y agregaciones por categoria pueden usar `categorias` con mucha mas confianza
- la supervision manual puede comparar `categorias` frente a `categorias_raw`

## Limitaciones conocidas

Este cambio no convierte magicamente cualquier etiqueta editorial en IPTC perfecto.

Limitaciones actuales:

1. El mapeo de aliases es conservador y manual.
2. Algunas etiquetas ambiguas como `General` no se interpretan semantica y automaticamente; usan el fallback de la fuente.
3. La calidad final depende de que la categoria IPTC configurada para cada feed sea razonable.

## Como supervisar el resultado

Se recomienda revisar en Mongo documentos recientes de `rss_entradas` comprobando:

- `categorias` solo contiene etiquetas IPTC esperadas
- `categorias_raw` sigue reflejando lo que venia del medio
- en feeds sin tags utiles, `categorias` toma la categoria configurada en la fuente

Casos de supervision utiles:

- Moncloa: deberia producir `Politica` aunque el feed publique `Presidente` y `Actividad`.
- Hispasec: etiquetas como `Phishing` o `ransomware` deberian acabar en `Ciencia y tecnologia`.
- feeds sin `tags`: deberian clasificarse por el fallback de la fuente.

## Como corregir si un feed queda mal clasificado

Hay dos niveles de correccion:

1. Ajustar el fallback `categoria_iptc` de la fuente en `rss-worker/rss/links_estandar.py`.
2. Anadir o corregir equivalencias en `rss-worker/rss/iptc.py`.

Regla recomendada:

- si el error afecta a todo el feed, corregir el fallback de la fuente
- si el error afecta a una etiqueta concreta repetida en varios items, corregir el alias o el mapeo

## Verificacion realizada

Se han anadido pruebas unitarias para:

- coincidencia exacta con categoria IPTC
- alias conocidos como `Phishing`
- fallback por fuente cuando la etiqueta original no es estandar
- conservacion simultanea de `categorias` y `categorias_raw`

Archivo de pruebas:

- `rss-worker/tests/rss/test_iptc.py`

## Siguiente recomendacion

Si se quiere una integracion completa con el backend de gestion de fuentes y canales, el siguiente paso natural seria unificar la categoria IPTC del worker con la `category_id` de `rss_channels`, para que el fallback de la ingesta salga de la configuracion funcional del sistema y no solo de `links_estandar.py`.
