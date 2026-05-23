# Decision Tecnica: pipeline de noticias, categorias y alertas

Fecha: 2026-04-27

## 1. Contexto

El enunciado da a entender un flujo bastante acoplado entre alerta y fuentes RSS:

- primero se definen alertas con descriptores y categoria IPTC
- despues se monitorizan noticias candidatas
- una vez detectadas, la noticia se clasifica con una categoria IPTC
- para esa clasificacion se usara la categoria de la alerta o la categoria de la fuente RSS

Fragmento clave del enunciado:

- "Una vez que se han identificado noticias candidatas porque contienen uno de los descriptores establecidos en la alerta, la noticia se habrá de clasificar de acuerdo con una categoría IPTC. Para ello, se utilizará o bien la categoría de la alerta o la categoría de la fuente de información (el canal RSS)."

Referencia: `docs/archivos_AG/PROYECTO_FINAL NEWSRADAR.md`

## 2. Pipeline actual

El sistema actual no sigue ese pipeline al pie de la letra.

Hoy el flujo es este:

1. `rss-worker` recorre todas las fuentes una sola vez por ciclo.
2. Guarda todas las noticias nuevas en MongoDB.
3. `alert-worker` ejecuta las alertas segun su `cron_expression`.
4. Cada alerta consulta sobre `rss_entradas` ya persistidas en MongoDB.

Este cambio respecto al enunciado no es necesariamente malo. De hecho, es una arquitectura mejor para operacion real por varias razones:

- desacopla la ingesta RSS del procesamiento de alertas
- evita pedir el mismo feed una vez por alerta
- permite reintentos y reprocesado contra historico reciente
- simplifica observabilidad, deduplicacion y estadisticas
- escala mucho mejor si crecen el numero de alertas

Conclusion: el pipeline actual basado en una BD intermedia es correcto y defendible. No hace falta volver al modelo "cada alerta consulta cada RSS".

## 3. Problema real que sigue abierto

El problema no es tanto el pipeline, sino la semantica de la categoria.

Ahora mismo hay varias nociones de categoria:

- categoria de la alerta
- categoria del canal RSS
- tags que vienen dentro del XML del feed o de cada item
- `category_id` en backend
- `categoria_iptc` en worker
- `categorias` y `categorias_raw` en cada noticia

Y ademas hoy hay una desconexion importante:

- backend crea canales RSS con `category_id`
- worker clasifica con `categoria_iptc`
- las alertas siguen guardando `category_id = 0` en creacion
- el matcher actual no filtra por categoria de alerta

Eso hace que la logica de clasificacion no este realmente cerrada.

## 4. Que se puede inferir del enunciado

La lectura mas razonable del enunciado es esta:

- la clasificacion no exige un clasificador semantico complejo
- se espera una clasificacion IPTC de primer nivel
- la categoria puede venir de metadatos ya existentes
- esos metadatos pueden ser:
  - la categoria de la alerta
  - la categoria del canal RSS

El enunciado no obliga a deducir la categoria real desde el XML.

Por tanto, la solucion mas fiel y mas viable es basarse en categorias declaradas y controladas por la aplicacion.

## 5. Sobre sacar la categoria del XML RSS

No es buena idea usar el XML RSS como fuente de verdad principal de categoria.

Motivos:

- muchos feeds no incluyen tags utiles
- los tags no suelen estar normalizados a IPTC
- un mismo medio usa nombres distintos o demasiado finos
- algunos feeds mezclan temas
- a veces la categoria aparece en el canal, otras en el item, otras no aparece
- apoyarse solo en eso os deja una clasificacion inconsistente

Lo sensato es:

- usar tags del feed como señal auxiliar
- no usarlos como fuente principal de verdad

## 6. Opciones de diseño

### Opcion A. La categoria de la fuente manda siempre

Regla:

- cada canal RSS tiene una categoria IPTC obligatoria
- toda noticia ingerida desde ese canal hereda esa categoria
- las alertas buscan solo por descriptores
- la categoria de la alerta se usa solo para mostrar o agrupar

Ventajas:

- implementacion simple
- estadisticas coherentes
- no depende del XML

Inconvenientes:

- si una fuente esta mal clasificada, todas sus noticias quedan mal clasificadas
- la categoria de la alerta pierde valor funcional
- se aleja de la lectura mas fuerte del enunciado

### Opcion B. La categoria de la alerta manda siempre

Regla:

- una noticia candidata se considera clasificada segun la categoria de la alerta que la detecta
- la categoria del canal RSS queda como metadato secundario

Ventajas:

- muy alineado con el lenguaje del enunciado en el contexto de alertas
- permite que una misma noticia participe en distintas alertas/categorias

Inconvenientes:

- la noticia deja de tener una categoria global unica
- las estadisticas globales por categoria se vuelven ambiguas
- una noticia podria quedar "clasificada" distinto segun la alerta que la toque

### Opcion C. Categoria global por fuente y filtro por alerta

Regla:

- cada canal RSS tiene una categoria IPTC obligatoria
- cada noticia almacenada hereda esa categoria como categoria global
- cada alerta tambien tiene categoria obligatoria
- el `alert-worker` solo revisa noticias cuyo `category_id` coincide con el de la alerta
- los descriptores se aplican solo dentro de ese subconjunto

Ventajas:

- la noticia tiene categoria global estable
- la alerta tiene efecto real y claro
- el pipeline contra Mongo sigue siendo eficiente
- las estadisticas por categoria son coherentes
- es la opcion mas limpia para el modelo actual

Inconvenientes:

- si un canal esta mal clasificado, las alertas de otra categoria no veran esas noticias
- obliga a ser estrictos con la gestion de canales y categorias

### Opcion D. Hibrido con fallback del feed

Regla:

- la fuente tiene categoria obligatoria
- si el item RSS trae tags normalizables a IPTC, se guardan tambien
- se usa primero la categoria detectada del item
- si no existe o no es fiable, se usa la de la fuente
- la alerta filtra por categoria

Ventajas:

- mas riqueza de datos
- deja abierta una mejora futura

Inconvenientes:

- añade complejidad ya
- requiere reglas de precedencia mas delicadas
- os mete antes de tiempo en problemas de normalizacion

## 7. Recomendacion

La mejor decision ahora mismo es la Opcion C.

Regla recomendada:

1. Solo se permiten canales RSS con categoria IPTC obligatoria.
2. Esa categoria se elige de forma explicita en frontend al dar de alta el canal.
3. Cada noticia hereda esa categoria del canal al persistirse.
4. Cada alerta debe guardar una categoria obligatoria real, no `0`.
5. El `alert-worker` solo evalua una alerta contra noticias de su misma categoria.
6. Los tags del XML RSS se pueden guardar como informacion auxiliar, pero no mandan sobre la categoria oficial del canal.

Esta opcion es la mejor porque:

- mantiene el pipeline actual basado en Mongo
- evita dependencia fuerte del XML
- hace util la categoria de la alerta
- da una categoria global clara a cada noticia
- simplifica estadisticas, filtros y depuracion

## 8. Que pasa si una fuente esta mal clasificada

Este es el principal riesgo de la Opcion C.

Si un canal RSS esta mal clasificado:

- sus noticias se guardaran con categoria incorrecta
- las alertas de la categoria correcta no las veran
- las estadisticas por categoria quedaran sesgadas

Pero este riesgo sigue siendo asumible y gestionable. Es mejor tener:

- un modelo simple, explicable y auditable

que intentar:

- clasificar semanticamente cada noticia con poca fiabilidad

Mitigaciones razonables:

- permitir editar la categoria del canal desde la UI
- registrar claramente la categoria del canal en la vista de fuentes
- mostrar ejemplos de noticias recientes por canal para revisar si la clasificacion es coherente
- opcionalmente, mostrar tags detectados del feed solo como ayuda al usuario

## 9. Como se relacionan las categorias en el modelo recomendado

### Categoria del canal RSS

Es la fuente de verdad para clasificar noticias persistidas.

Debe guardarse como:

- `category_id` canonico

### Categoria de la noticia

No debe inferirse principalmente desde texto libre ni desde XML variable.

Debe guardarse como:

- `category_id` heredado del canal en el momento de la ingesta

Opcionalmente se pueden conservar:

- `categorias_raw` con tags del feed
- una lista de tags o categorias detectadas como apoyo diagnostico

### Categoria de la alerta

Debe ser obligatoria y funcional.

Sirve para:

- filtrar noticias antes de aplicar descriptores
- agrupar notificaciones
- producir estadisticas por categoria

### Tags del XML RSS

Deben considerarse:

- señal auxiliar
- ayuda de previsualizacion
- posible futura validacion

No deben ser la base obligatoria del pipeline.

## 10. Cambios funcionales minimos que implica esta decision

1. En frontend:
   - obligar a seleccionar categoria al crear o editar un canal RSS

2. En backend:
   - guardar `category_id` real en canales RSS
   - guardar `category_id` real en alertas
   - dejar de crear alertas con `category_id = 0`

3. En rss-worker:
   - copiar `category_id` del canal a cada `rss_entrada`

4. En alert-worker:
   - consultar solo noticias con `category_id == alert.category_id`
   - despues aplicar matching por descriptores

5. En estadisticas:
   - usar ese `category_id` persistido en noticias y alertas

## 11. Decision final

Se adopta la siguiente decision:

- mantener el pipeline actual con doble worker y MongoDB intermedia
- considerar obligatoria la categoria IPTC de cada canal RSS
- clasificar cada noticia segun la categoria del canal del que procede
- considerar obligatoria la categoria de cada alerta
- filtrar cada alerta solo contra noticias de su misma categoria
- usar tags del XML RSS solo como informacion auxiliar y nunca como fuente principal de verdad

## 12. Motivo de la decision

Es la opcion que mejor equilibra:

- fidelidad razonable al enunciado
- simplicidad de implementacion
- robustez operativa
- consistencia de datos
- utilidad real de la categoria en alertas y estadisticas
