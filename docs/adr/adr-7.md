# ADR 007: Contrato de datos RSS unificado (Mongo ObjectId + hashes logicos)

- Fecha: 02/04/2026
- Decisores: Equipo NewsRadar

## Contexto

Existian divergencias entre el modelo RSS en Python y la inicializacion de Mongo:

- nombres de colecciones diferentes,
- nombres de campos distintos,
- discrepancias en el tipo de identificador para relaciones entre fuente y entrada.

Ademas, el proyecto requiere deduplicacion estable de noticias y soporte para indexacion en Elasticsearch.

## Decision

1. Mantener campos funcionales RSS en espanol para minimizar friccion con el codigo existente.
2. Usar `_id` nativo `ObjectId` de Mongo como identificador tecnico.
3. Conservar hashes personalizados como identificadores logicos:
   - `hash_fuente` en fuentes.
   - `hash_deduplicado` en entradas.
4. Unificar colecciones RSS en Mongo como:
   - `rss_fuentes`
   - `rss_entradas`
   - `rss_entradas_raw`
5. Definir en Elasticsearch indices RSS alineados con estos campos para busqueda y agregaciones.
6. Establecer MongoDB como fuente de verdad y Elasticsearch como indice secundario/materializado para consulta.
7. Inicializar Elasticsearch mediante un contenedor one-shot `elasticsearch-setup` en Compose.

## Motivo

- `ObjectId` simplifica referencias y operaciones nativas en Mongo.
- hashes propios garantizan deduplicacion e idempotencia funcional.
- conservar espanol reduce coste de migracion en la capa RSS actual.
- la imagen oficial de Elasticsearch no ofrece un mecanismo nativo equivalente a `/docker-entrypoint-initdb.d` de Mongo para crear indices/mappings al primer arranque.
- el contenedor `elasticsearch-setup` mantiene la inicializacion desacoplada, repetible e idempotente.

## Consecuencias

- El flujo de persistencia debe insertar/recuperar primero la fuente para obtener `ObjectId` antes de insertar entradas.
- Se deben mantener validadores e indices sincronizados entre capa Python e init de Mongo.
- El conector Mongo -> Elasticsearch usara `hash_deduplicado` como `_id` de documento para evitar duplicados en ES.
- Si Elasticsearch se pierde o se recrea, se reindexa desde MongoDB sin perdida de estado funcional.
- La creacion de indices de Elasticsearch depende del job `elasticsearch-setup` en cada entorno nuevo o tras un reset.

## Alternativas consideradas

1. Migrar todo a nombres en ingles.
   - Ventaja: mayor estandarizacion.
   - Inconveniente: impacto alto y cambios amplios en codigo existente.

2. Usar solo hashes como `_id` en Mongo.
   - Ventaja: simplicidad en deduplicacion.
   - Inconveniente: peor encaje con relaciones y practicas habituales de Mongo.
