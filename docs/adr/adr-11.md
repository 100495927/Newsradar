# ADR 011: Categorías efectivas y validación de alertas

**Fecha:** 29-04-2026  
**Decisores:** Equipo NewsRadar  

## Contexto
El enunciado describe la alerta en singular como perteneciente a una categoría IPTC, pero el API de referencia usa `categories` como lista y además permite seleccionar fuentes o canales RSS concretos para cada alerta.

Esto abre una ambigüedad: si una alerta tiene varias categorías o si sus fuentes seleccionadas no encajan con esas categorías, no está claro cómo clasificar la noticia ni cómo validar la alerta.

## Decisión
- La categoría efectiva de una noticia será la categoría IPTC de su canal RSS.
- Por ahora cada alerta tendrá funcionalmente una sola categoría.
- El campo `categories` se mantiene como lista por compatibilidad con el API y para permitir una futura extensión a varias categorías sin romper el contrato.
- Si una alerta selecciona fuentes o canales concretos, todos ellos deben ser compatibles con la única categoría de la alerta.
- Si no lo son, la creación o actualización de la alerta se rechazará con `400 Bad Request`.

## Motivo
- Mantiene una categoría global única y estable para cada noticia.
- Evita reclasificar una misma noticia en varias categorías por culpa de una alerta.
- Hace coherentes las estadísticas por categoría.
- Da un criterio claro de validación cuando el usuario restringe fuentes concretas.
- Conserva margen para ampliar a varias categorías más adelante sin cambiar la forma pública del modelo.

## Consecuencias
- Una noticia no pasa a ser de todas las categorías de la alerta; sigue siendo de la categoría de su fuente.
- La validación de compatibilidad entre alerta y fuentes seleccionadas es una restricción funcional, no una restricción expresable solo con el schema OpenAPI.
- Si más adelante se habilitan varias categorías por alerta, la semántica recomendada será de filtro OR, no de multiclasificación de noticias.
