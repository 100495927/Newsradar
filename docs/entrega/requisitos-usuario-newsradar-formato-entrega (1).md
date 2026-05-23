# Requisitos de usuario NewsRadar

## Criterio de identificación

La identificación de los requisitos sigue el formato `UG-nnn`:

- `U`: indica que se trata de un requisito de usuario.
- `G`: indica que es un requisito general.
- `nnn`: numeración consecutiva del requisito.

## Escalas utilizadas

### Prioridad
- Alta
- Medio
- Bajo

### Fuente
- Cliente
- Analistas

### Necesidad
- Alta
- Medio
- Bajo

### Claridad
- Alta
- Medio
- Bajo

### Verificabilidad
- Alta
- Medio
- Bajo

### Estabilidad
- Alta
- Medio
- Bajo

## Requisitos

### UG-001
Identificador: UG-001  
Nombre: Crear alertas de monitorización

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe permitir crear alertas para monitorizar noticias sobre un tema concreto.

### UG-002
Identificador: UG-002  
Nombre: Limitar el número de alertas

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe permitir a un gestor de NewsRadar dar de alta como máximo 20 alertas.

### UG-003
Identificador: UG-003  
Nombre: Definir atributos básicos de una alerta

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Cada alerta debe incluir al menos un nombre, una palabra clave principal y una categoría IPTC Media Topics de primer nivel.

### UG-004
Identificador: UG-004  
Nombre: Recomendar expansión semántica de alertas

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Medio

Descripción:

El sistema debe recomendar extensiones del descriptor principal de una alerta mediante sinónimos o términos relacionados.

### UG-005
Identificador: UG-005  
Nombre: Generar entre 3 y 10 términos relacionados

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La expansión de una alerta debe generar entre 3 y 10 palabras adicionales.

### UG-006
Identificador: UG-006  
Nombre: Aceptar recomendaciones de descriptores

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El usuario debe poder aceptar las recomendaciones sugeridas para completar los descriptores de la alerta.

### UG-007
Identificador: UG-007  
Nombre: Seleccionar fuentes asociadas a una alerta

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El usuario debe poder seleccionar las fuentes o canales RSS concretos asociados a una alerta.

### UG-008
Identificador: UG-008  
Nombre: Aplicar selección por defecto de fuentes

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Si el usuario no selecciona fuentes concretas, el sistema debe tomar por defecto todos los canales RSS de la misma categoría.

### UG-009
Identificador: UG-009  
Nombre: Monitorizar alertas de forma continua

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Alta

Descripción:

El sistema debe monitorizar de forma continua las alertas mediante una expresión de cron o un mecanismo equivalente programado.

### UG-010
Identificador: UG-010  
Nombre: Detectar noticias candidatas por coincidencia

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Cuando el sistema detecte una noticia que contenga alguno de los descriptores definidos en una alerta, debe almacenarla y enviarla al proceso de clasificación.

### UG-011
Identificador: UG-011  
Nombre: Almacenar noticias detectadas

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe almacenar las noticias candidatas detectadas durante la monitorización.

### UG-012
Identificador: UG-012  
Nombre: Clasificar noticias por categoría IPTC

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe clasificar cada noticia candidata de acuerdo con una categoría IPTC.

### UG-013
Identificador: UG-013  
Nombre: Usar categoría de alerta o fuente para clasificar

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Medio  
Verificabilidad: Alta  
Estabilidad: Medio

Descripción:

La clasificación de una noticia debe realizarse usando la categoría de la alerta o la categoría de la fuente de información.

### UG-014
Identificador: UG-014  
Nombre: Restringir categorías al primer nivel IPTC

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema solo debe permitir categorías pertenecientes al primer nivel de IPTC Media Topics.

### UG-015
Identificador: UG-015  
Nombre: Generar notificaciones por coincidencia

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe generar una notificación cuando aparezca una noticia que contenga palabras incluidas en una alerta.

### UG-016
Identificador: UG-016  
Nombre: Enviar notificaciones por buzón y correo

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe poder enviar notificaciones al buzón interno de la aplicación y al correo electrónico del usuario.

### UG-017
Identificador: UG-017  
Nombre: Configurar canal de notificaciones

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La alerta debe poder configurarse para definir si las notificaciones se envían al buzón de la aplicación, al correo electrónico o a ambos.

### UG-018
Identificador: UG-018  
Nombre: Definir asunto de la notificación

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El título de la notificación debe indicar la alerta y el momento de actualización, con el formato equivalente a `Actualización de <alerta> en <día/hora>`.

### UG-019
Identificador: UG-019  
Nombre: Incluir datos básicos de la noticia en la notificación

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El contenido de la notificación debe incluir, al menos, origen de la noticia, fecha y hora, título y resumen disponible en el RSS.

### UG-020
Identificador: UG-020  
Nombre: Incluir estadísticas de procesamiento en la notificación

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Medio  
Verificabilidad: Medio  
Estabilidad: Medio

Descripción:

El sistema debe informar en las notificaciones de los resultados y estadísticas del procesamiento.

### UG-021
Identificador: UG-021  
Nombre: Gestionar fuentes de información

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe incluir un mecanismo para añadir fuentes de información y canales RSS.

### UG-022
Identificador: UG-022  
Nombre: Asociar fuente a medio y categoría

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Cada fuente o canal RSS debe asociarse a un medio de comunicación y a una categoría IPTC.

### UG-023
Identificador: UG-023  
Nombre: Disponer de un catálogo inicial de 100 canales RSS

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Medio

Descripción:

El sistema debe contar inicialmente con al menos 100 canales RSS pertenecientes a 10 medios diferentes.

### UG-024
Identificador: UG-024  
Nombre: Cubrir categorías IPTC con canales RSS

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Medio

Descripción:

El catálogo inicial debe cubrir al menos con un canal RSS todas las categorías de primer nivel de IPTC Media Topics.

### UG-025
Identificador: UG-025  
Nombre: Gestionar usuarios de la plataforma

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe gestionar usuarios de la plataforma.

### UG-026
Identificador: UG-026  
Nombre: Soportar roles de usuario

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe soportar al menos dos roles: gestor de NewsRadar y lector.

### UG-027
Identificador: UG-027  
Nombre: Permitir al gestor administrar alertas y fuentes

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El rol gestor de NewsRadar debe poder gestionar alertas y añadir fuentes de información.

### UG-028
Identificador: UG-028  
Nombre: Restringir la gestión de alertas al lector

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El rol lector debe poder acceder a la plataforma en modo lectura, sin capacidad para gestionar alertas.

### UG-029
Identificador: UG-029  
Nombre: Definir datos identificativos del usuario

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Cada usuario debe identificarse mediante un correo electrónico válido, nombre, apellidos y organización.

### UG-030
Identificador: UG-030  
Nombre: Permitir el registro de nuevos usuarios

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe permitir el alta de nuevos usuarios.

### UG-031
Identificador: UG-031  
Nombre: Enviar verificación de cuenta al registrarse

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Cuando se registre un nuevo usuario, el sistema debe enviar un correo de verificación de cuenta.

### UG-032
Identificador: UG-032  
Nombre: Caducar la verificación en 24 horas

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El enlace o mecanismo de verificación de cuenta debe caducar a las 24 horas.

### UG-033
Identificador: UG-033  
Nombre: Disponer de administrador inicial

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe disponer de un usuario administrador inicial con capacidad para asignar roles a nuevos usuarios.

### UG-034
Identificador: UG-034  
Nombre: Permitir inicio de sesión

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe ofrecer funcionalidad de login.

### UG-035
Identificador: UG-035  
Nombre: Permitir recuperación de contraseña

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe permitir recuperar la contraseña del usuario.

### UG-036
Identificador: UG-036  
Nombre: Permitir edición de perfil

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe permitir editar los datos personales del usuario.

### UG-037
Identificador: UG-037  
Nombre: Disponer de interfaz gráfica de usuario

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Toda la información capturada y analizada debe poder visualizarse y gestionarse mediante una interfaz gráfica.

### UG-038
Identificador: UG-038  
Nombre: Incluir panel de mando

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe ofrecer un panel de mando para visualización y gestión de la información.

### UG-039
Identificador: UG-039  
Nombre: Mostrar nubes de palabras por categoría

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Medio

Descripción:

El panel de mando debe mostrar los temas más candentes mediante nubes de palabras por categoría.

### UG-040
Identificador: UG-040  
Nombre: Mostrar estadísticas globales de extracción

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El panel de mando debe mostrar estadísticas globales de extracción de información.

### UG-041
Identificador: UG-041  
Nombre: Mostrar métricas mínimas en el panel

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Las estadísticas globales deben incluir, como mínimo, número de fuentes, número de noticias, número de noticias por categoría, número de alertas y número de alertas por categoría.

### UG-042
Identificador: UG-042  
Nombre: Gestionar alertas desde la interfaz

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La interfaz debe permitir crear y gestionar alertas.

### UG-043
Identificador: UG-043  
Nombre: Gestionar fuentes desde la interfaz

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La interfaz debe permitir crear y gestionar fuentes de información y canales RSS.

### UG-044
Identificador: UG-044  
Nombre: Consultar buzón interno de notificaciones

Prioridad: Medio  
Fuente: Cliente  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La interfaz debe permitir consultar el buzón interno de notificaciones.

### UG-045
Identificador: UG-045  
Nombre: Soportar interfaz bilingüe

Prioridad: Bajo  
Fuente: Cliente  
Necesidad: Bajo  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Medio

Descripción:

Opcionalmente, el sistema debe permitir visualizar la interfaz en dos idiomas: español e inglés.

### UG-046
Identificador: UG-046  
Nombre: Limitar el cambio de idioma a la interfaz

Prioridad: Bajo  
Fuente: Cliente  
Necesidad: Bajo  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El cambio de idioma debe afectar a la interfaz de usuario, no necesariamente al contenido de las noticias.

### UG-047
Identificador: UG-047  
Nombre: Exponer la información mediante API REST

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Toda la información gestionada por el sistema debe exponerse mediante un API REST.

### UG-048
Identificador: UG-048  
Nombre: Documentar el API con OpenAPI

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El API REST debe estar documentada con OpenAPI.

### UG-049
Identificador: UG-049  
Nombre: Mantener compatibilidad con el API del anexo

Prioridad: Alta  
Fuente: Cliente  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Medio

Descripción:

El sistema desarrollado debe ofrecer el mismo API REST definido en el anexo del enunciado para la gestión de información.

### UG-050
Identificador: UG-050  
Nombre: Disponer de arquitectura mínima del sistema

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe contar, como mínimo, con un sistema gestor de datos para almacenamiento de información, un sistema gestor de datos para almacenamiento de entidades del sistema, una capa de lógica de negocio, una capa de visualización y un API REST.

### UG-051
Identificador: UG-051  
Nombre: Justificar la tecnología seleccionada

Prioridad: Medio  
Fuente: Analistas  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Alta

Descripción:

Aunque no existe restricción de lenguaje, plataforma o tecnología, las tecnologías elegidas deben justificarse cuando proceda.

### UG-052
Identificador: UG-052  
Nombre: Automatizar las pruebas

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El proyecto debe automatizar las pruebas del sistema mediante integración continua.

### UG-053
Identificador: UG-053  
Nombre: Cubrir pruebas unitarias y funcionales

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La automatización de pruebas debe cubrir al menos pruebas unitarias y pruebas funcionales.

### UG-054
Identificador: UG-054  
Nombre: Permitir pruebas de rendimiento opcionales

Prioridad: Bajo  
Fuente: Analistas  
Necesidad: Bajo  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Medio

Descripción:

Las pruebas de rendimiento son opcionales dentro del proyecto.

### UG-055
Identificador: UG-055  
Nombre: Gestionar el desarrollo en una plataforma tipo GitHub

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El proceso de desarrollo debe planificarse y gestionarse en una plataforma tipo GitHub usando una metodología tipo Scrum.

### UG-056
Identificador: UG-056  
Nombre: Organizar el trabajo con sprints e issues

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La gestión del proyecto debe contemplar sprints, issues, etiquetas, ramas y la configuración asociada.

### UG-057
Identificador: UG-057  
Nombre: Facilitar revisiones periódicas del proyecto

Prioridad: Medio  
Fuente: Analistas  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Alta

Descripción:

El profesor debe formar parte del proyecto y este debe poder revisarse de forma periódica con una cadencia máxima de una a dos semanas.

### UG-058
Identificador: UG-058  
Nombre: Configurar una estrategia de ramas

Prioridad: Medio  
Fuente: Analistas  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Alta

Descripción:

El control de versiones debe configurarse con una estrategia de ramas apropiada.

### UG-059
Identificador: UG-059  
Nombre: Automatizar la configuración del entorno

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El proyecto debe proveer mecanismos para automatizar la configuración de las herramientas tecnológicas utilizadas.

### UG-060
Identificador: UG-060  
Nombre: Desplegar automáticamente en una nueva máquina

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El sistema debe poder construirse y desplegarse automáticamente en una máquina nueva.

### UG-061
Identificador: UG-061  
Nombre: Utilizar un pipeline de construcción

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El proyecto debe utilizar un pipeline para la construcción del sistema.

### UG-062
Identificador: UG-062  
Nombre: Proporcionar métricas de calidad del código

Prioridad: Medio  
Fuente: Analistas  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Alta

Descripción:

El proyecto debe proporcionar métricas de calidad del código fuente.

### UG-063
Identificador: UG-063  
Nombre: Mantener una estructura mínima del repositorio

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El repositorio debe contener al menos código fuente completo, documentación versionada, ADRs, especificación final de requisitos, diagramas de arquitectura, scripts de construcción, scripts de pruebas, scripts de ejecución, scripts de despliegue, scripts de documentación, configuración de dependencias, configuración de entorno, datos de prueba o inicialización y planificación del proceso de desarrollo.

### UG-064
Identificador: UG-064  
Nombre: Automatizar construcción, pruebas y distribución

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El proyecto debe incluir mecanismos automatizados para la construcción del software, la ejecución de pruebas, la integración continua, la generación de informe de cobertura, la generación de documentación técnica, la verificación de calidad del código y el empaquetado y distribución.

### UG-065
Identificador: UG-065  
Nombre: Gestionar todo el proyecto en un único repositorio

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

Todo el proyecto debe estar completamente gestionado y documentado dentro de un único repositorio versionado.

### UG-066
Identificador: UG-066  
Nombre: Evitar documentación fuera del repositorio

Prioridad: Medio  
Fuente: Analistas  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

No debe existir documentación externa fuera del repositorio para la entrega evaluable.

### UG-067
Identificador: UG-067  
Nombre: Permitir evaluación reproducible con un único comando

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

El repositorio debe permitir que un evaluador pueda clonar el proyecto, ejecutar un único comando o pipeline, construir el sistema, ejecutar las pruebas, generar la documentación, desplegar la aplicación en un entorno limpio y ejecutar la aplicación sin intervención manual adicional.

### UG-068
Identificador: UG-068  
Nombre: Versionar la documentación junto al código

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La documentación debe estar versionada junto al código.

### UG-069
Identificador: UG-069  
Nombre: Generar documentación automáticamente cuando sea posible

Prioridad: Medio  
Fuente: Analistas  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Alta

Descripción:

La documentación debe generarse automáticamente cuando sea posible.

### UG-070
Identificador: UG-070  
Nombre: Mantener trazabilidad entre requisitos y arquitectura

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Alta

Descripción:

La documentación debe mantener trazabilidad con requisitos y arquitectura.

### UG-071
Identificador: UG-071  
Nombre: Mantener trazabilidad con los prompts utilizados

Prioridad: Medio  
Fuente: Analistas  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Medio

Descripción:

La documentación debe mantener trazabilidad con los prompts utilizados.

### UG-072
Identificador: UG-072  
Nombre: Incluir referencias cruzadas en la documentación

Prioridad: Medio  
Fuente: Analistas  
Necesidad: Medio  
Claridad: Alta  
Verificabilidad: Medio  
Estabilidad: Alta

Descripción:

La documentación debe incluir referencias cruzadas entre requisitos, ADRs, componentes implementados y pruebas asociadas.

### UG-073
Identificador: UG-073  
Nombre: Automatizar la verificación funcional mediante API

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Alta

Descripción:

La verificación funcional del sistema debe automatizarse a través del API REST definido en el anexo, con datos preparados para ello.

### UG-074
Identificador: UG-074  
Nombre: Superar inspecciones manuales adicionales

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Alta  
Verificabilidad: Alta  
Estabilidad: Medio

Descripción:

Además de la verificación automática, el sistema debe superar inspecciones manuales sobre funcionalidades de clasificación, usuarios, notificaciones e interfaz.

### UG-075
Identificador: UG-075  
Nombre: Facilitar cambios rápidos en competición

Prioridad: Alta  
Fuente: Analistas  
Necesidad: Alta  
Claridad: Medio  
Verificabilidad: Medio  
Estabilidad: Medio

Descripción:

El sistema debe estar preparado para incorporar cambios, recuperar versiones previas o desactivar funcionalidades en el entorno de producción en tiempos reducidos.

## Observaciones

- Se ha usado `UG` en todos los identificadores, tal como indicaste.
- Los valores de prioridad, necesidad y estabilidad se han asignado de forma razonada a partir del enunciado.
- Los requisitos opcionales del enunciado, como el soporte bilingüe, se han reflejado con prioridad y necesidad bajas.
