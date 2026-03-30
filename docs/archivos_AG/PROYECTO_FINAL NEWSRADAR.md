Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

# Sistema de monitorización de noticias en medios

# de comunicación y fuentes oficiales:

# NEWSRADAR

## 1 Sobre este documento

```
Persona de
Contacto
```
```
Su profesor en el grupo reducido
```
```
Versión 1.
Estado
(Borrador,
Definitivo)
```
```
Borrador
```
```
Fecha de
actualización:
```
```
martes, 3 de marzo de 2026
```
```
Nº de páginas 16 (incluye portada)
Palabras clave: Proyecto final, newsradar
```
## 2 Tipología

```
Tipo Grupal
```
```
Fecha de entrega y defensa 25 de mayo de 2026, 10:
```
```
Calificación Sistema verificado y validado
(funcionalmente correcto): aprobado
Verificación final del Sistema antes del
combate 10%
Clasificación en la competición 80%
Rol de cada miembro del equipo y
Evaluación 360º entre el equipo y el líder
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
de equipo. Este último criterio permite
establecer el desempeño individual y
discernir la evaluación individual. 10%.
```
```
Peso 100%
```
```
Aclaración Dada la naturaleza de la asignatura, la
descripción del proyecto podrá variar
incluyendo cambios (adición,
actualización o borrado) de
funcionalidades durante todo el tiempo de
ejecución y como mucho hasta 2 semanas
antes de terminar el cuatrimestre.
```
```
Recursos Fichero newsradar_api.zip
```
## 3 Descripción

Todos los días y desde hace mucho tiempo los medios de comunicación publican
un resumen de la información de sus noticias de forma sindicada a través del

### formato RSS (“Really Simple Syndication o Rich Site Summary”). Este formato

permite crear canales de contenidos que a su vez contienen “ítems” de noticias.
Todo ello metadatado apropiadamente. La información publicada bajo este
formato sirve para varios propósitos como puede ser la agregación de noticias o
el contraste de estas.

Bajo este contexto, se busca desarrollar un sistema software que sea capaz de
escuchar canales RSS de distintos medios de comunicación o fuentes oficiales y
en diferentes categorías organizando la información y proveyendo un panel de
mando de monitorización de lo que se está publicando. En concreto, se fijan los
siguientes objetivos:

```
Objetivo 1. Gestión de alertas: monitorización de temas o categorías. El
primer objetivo del sistema es ser capaz de definir alertas sobre un
descriptor (“palabra clave”). El sistema deberá recomendar extensiones a
este descriptor en forma de sinónimos o descriptores similares o
relacionados. El usuario será el encargado de aceptar las
recomendaciones, de seleccionar las fuentes de información o canales RSS
concretos (por omisión serán todos los que pertenezcan a la misma
categoría) y de etiquetar la alerta en una categoría siguiendo el primer
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
nivel de IPTC Media Topics^1. A partir de ese momento, el sistema
comenzará a monitorizar esa alerta (y todos sus descriptores) mediante
```
### un proceso continuo descrito por una expresión de cron. Cuando el sistema

```
detecte alguna noticia que contenga esa palabra se almacenará y pasará
a la fase de clasificación de información.
Objetivo 2. Clasificación de información. Una vez que se han
identificado noticias candidatas porque contienen uno de los descriptores
establecidos en la alerta, la noticia se habrá de clasificar de acuerdo con
una categoría IPTC. Para ello, se utilizará o bien la categoría de la alerta
o la categoría de la fuente de información (el canal RSS).
Objetivo 3. Gestión de notificaciones. Después de clasificar la
información se deberá enviar una notificación con los resultados al usuario
indicando de forma apropiada en el título del correo la alerta y las
estadísticas de procesamiento.
Objetivo 4. Gestión de fuentes de información y canales RSS. El sistema
deberá incluir un mecanismo para añadir fuentes de información: canales
RSS pertenecientes a un medio de comunicación y a una categoría IPTC.
Objetivo 5. Gestión de usuarios. El sistema permitirá dos tipos de
usuarios: 1) gestor de newsradar, tiene la capacidad de gestionar alertas
y añadir fuentes de información y 2) lector, tiene acceso a toda la
plataforma salvando la gestión de alertas.
Objetivo 6. Panel de mando y visualización. Toda la información
capturada y analizada se deberá poder visualizar y gestionar desde un
interfaz gráfico de usuario. Este panel de mando contendrá las siguientes
capacidades:^
a. Visualización de temas más candentes mediante nubes de palabras
por categoría.
b. Visualización de estadísticas globales de extracción de información:
nº de fuentes, nº de noticias, nº de noticias por categoría, nº de
alertas y nº de alertas por categoría
c. Creación y gestión de alertas.
d. Creación y gestión de fuentes de información: canales RSS
e. Gestión del perfil de usuario con capacidad de registro, login,
edición de datos personales y recuperación de contraseña.
```
(^1) https://www.iptc.org/std/NewsCodes/treeview/mediatopic/mediatopic-es.html


Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

### 3.1 Otra información relevante

```
§ Gestión de alertas. Con el objetivo de monitorizar noticias sobre temas
en particular, se podrán definir alertas.
o Un gestor de newsradar puede dar de alta de una alerta (hasta un
máximo de 20).
o Esta alerta estará formada por un nombre, una palabra clave que
se podrá expandir generando entre 3 y 10 palabras extras
(sinónimos, u otras palabras relacionadas).
o Una alerta pertenecerá a una categoría. Las categorías serán las
del estándar IPTC Media Topics.
o La alerta se podrá configurar para que envíe notificaciones al buzón
de la aplicación o al correo electrónico del usuario por la aparición
de noticias que contengan las palabras definidas en dicha alerta.
§ Gestión de fuentes de información y canales RSS.
o Un gestor de newsradar puede dar de alta fuentes de información
pertenecientes a un medio de comunicación.
o El sistema deberá contar con un mínimo inicial de 100 canales RSS
pertenecientes a 10 medios diferentes y cubriendo al menos con 1
canal RSS las categorías de primer nivel de IPTC Media Topics.
§ Gestión de notificaciones. Una notificación se genera cuando aparece
una noticia que contiene palabras incluidas en una alerta. Para ello,
se enviará un mensaje al buzón del usuario en la aplicación y a su
correo electrónico. El título indicará: “Actualización de <alerta> en
<día/hora>” mientras que el contenido mostrará un mensaje
información sobre origen de la noticia, ficha y hora, título de la noticia
y resumen que aparezca en el RSS.
§ Gestión de usuarios. Al menos se requieren dos tipos de roles de
usuarios:
o 1 - Gestor de newsradar que se encarga de configurar los diferentes
aspectos de la plataforma y
o 2 - Lector que utiliza la plataforma en modo lectura con la
configuración se haya realizado.
o Un usuario se identifica por un correo electrónico válido, nombre,
apellidos y organización.
o Al darse de alta un nuevo usuario, el sistema enviará un correo de
verificación que tendrá una caducidad de 24 horas.
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
o Debe existir un usuario administrador inicial que sea capaz de
asignar roles a nuevos usuarios.
§ Panel de mando y visualización.
o Opcionalmente, el panel de mando deberá mostrar la información
en dos idiomas seleccionables: ES (Español) y EN (Inglés).
§ API de servicios. Toda la información gestionada por el sistema deberá
ofrecerse mediante un API REST documentada con OpenAPI. Ver
anexo I.
```
### 3.2 Fuentes de información

A continuación, y a modo de ejemplo, se incluyen los enlaces a los canales RSS
de diferentes medios de comunicación y fuentes oficiales tanto tradicionales como
digitales.

- https://www.rtve.es/rss/
- https://elpais.com/info/rss/
- https://www.abc.es/rss/
- https://www.elconfidencial.com/rss/
- https://www.marca.com/rss.html
- https://www.esdiario.com/rss.html
- https://www.antena3.com/rss/
- https://www.dsca.gob.es/es/consumo/canales-rss
- https://portal.mineco.gob.es/es-es/ministerio/Paginas/Info_RSS.aspx
- https://www.lamoncloa.gob.es/paginas/varios/rss.aspx

## 4 Entorno tecnológico

En cuanto al entorno tecnológico no existe restricción sobre lenguaje de
programación, plataforma o tecnología a utilizar. Sin embargo, sí se establecen
los siguientes elementos arquitecturales con los que el sistema debe contar:

```
§ Un sistema gestor de datos para el almacenamiento de la información.
§ Un sistema gestor de datos para el almacenamiento de las entidades
del sistema.
§ Una capa de lógica de negocio.
§ Una capa de visualización.
§ Un API REST.
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
Entre las tecnologías candidatas se recomiendan:
§ ElasticSearch, MongoDB, SQLite u otro sistema a elección del equipo
de forma justificada para los sistemas de gestión de datos.
§ Apache Superset o Kibana para la visualización de datos.
§ Angular.js, React.js o similar para la visualización de datos (si se
quiere realizar manualmente integrando con una biblioteca tipo
D3.js).
§ Docker para la configuración del software a utilizar.
§ Otras herramientas según las necesidades de DevOps.
§ Hacer un uso intensivo de tecnologías de IA generativa.
```
(^5) Proceso de desarrollo
Tratándose de una asignatura con foco en los conceptos de DevOps es
conveniente resaltar los siguientes puntos que son fundamentales y que se irán
abordando a lo largo del curso en las distintas sesiones semanales:
§ Se debe automatizar cualquier tipo de prueba (integración continua)
cubriendo al menos pruebas unitarias y funcionales del sistema.
Opcionalmente, se podrán hacer pruebas de rendimiento. Para ello, se
recomienda utilizar bibliotecas basadas en Junit (dependiendo del
lenguaje), Mockito, etc. así como Apache JMeter o Locust para pruebas
de rendimiento.
§ Se debe planificar y gestionar todo el proceso de desarrollo en una
plataforma tipo Github mediante una metodología tipo Scrum
estableciendo sprints, issues, etc. con la configuración asociada
(etiquetas, ramas, etc.). El profesor deberá formar parte de este
proyecto y se revisará de forma periódica siendo el período definido por
el equipo (1-2 semanas a lo sumo).
§ De la misma forma, se deben configurar las ramas del control de
versiones apropiadamente.
§ Se deben proveer mecanismos para la automatización de la
configuración de las distintas herramientas tecnológicas que se
utilicen.
§ Se debe ser capaz de construir y desplegar el sistema en una nueva
máquina de forma automática.
§ Se debe utilizar un pipeline para la construcción del sistema.


Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
§ Se deben proporcionar métricas de calidad de código fuente. Por
ejemplo, con algún plugin de entorno de desarrollo o bien con una
herramienta tipo SonarQube.
```
(^6) Propuesta de estructura del repositorio y automatización
El repositorio deberá contener como mínimo:
§ Código fuente completo.
§ Documentación en formato versionado (Mark Down o similar).
§ ADRs almacenados en carpeta específica (por ejemplo, /docs/adr).
§ Especificación final de requisitos.
§ Diagramas de arquitectura.
§ Scripts de construcción.
§ Scripts de pruebas.
§ Scripts de ejecución.
§ Scripts de despliegue.
§ Scripts de documentación.
§ Configuración de dependencias.
§ Configuración de entorno.
§ Datos de prueba o inicialización.
§ Planificación del proceso de desarrollo.
Por lo tanto, ll proyecto deberá incluir mecanismos automatizados para:
§ Construcción del software.
§ Ejecución de pruebas.
§ Integración continua (CI).
§ Generación de informe de cobertura.
§ Generación de documentación técnica.
§ Verificación de calidad del código.
§ Empaquetado y distribución (CD).

## 7 Política con IA generativa

Este proyecto así como la evaluación de este en la competición final se enmarcan
en la OPCIÓN 1. El uso de IA Generativa está permitido en esta asignatura en


Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

todas las actividades evaluables. No obstante, el equipo docente se reserva la
configuración la configuración de la IA generativa en la competición final para
asegurar una competición justa.

## 8 Entregables

Se entregará un único fichero comprimido <NOMBRE_GRUPO>.tgz que
contenga todo el repositorio en una tarea de Aula Global.

En el caso de exceder el tamaño del fichero se deberá subir un fichero de texto
conteniendo el enlace a un archivo en Google Drive.

Todo el proyecto deberá estar completamente gestionado y documentado dentro
de un único repositorio versionado. No se aceptarán entregas externas ni
documentación fuera del repositorio. El repositorio deberá permitir que un
evaluador pueda:

```
§ Clonar el proyecto (se asume que el fichero comprimido es un clonado
del repositorio).
§ Ejecutar un único comando o pipeline.
§ Construir el sistema.
§ Ejecutar las pruebas.
§ Generar la documentación.
§ Desplegar la aplicación en un entorno limpio.
§ Ejecutar la aplicación.
Sin intervención manual adicional.
La documentación deberá:
§ Estar versionada junto al código.
§ Generarse automáticamente cuando sea posible.
§ Mantener trazabilidad con requisitos y arquitectura.
§ Mantener la trazabilidad con los prompts utilizados.
§ Incluir referencias cruzadas entre:
o Requisitos
o ADRs
o Componentes implementados
o Pruebas asociadas
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

## 9 El día del examen: la competición

Sólo se podrá entrar en competición si se pasan los scripts de pruebas y la
inspección manual. La competición consistirá en realizar modificaciones en la
aplicación evaluándose el tiempo tardado por los equipos en incorporar dichas
modificaciones. Se incluyen algunos ejemplos de estas modificación.

```
Modificación Comentario / Evaluación
```
```
Añadir una
funcionalidad
```
```
Se solicitará la adición de una nueva función en la
aplicación.
La competición medirá el tiempo tardado en
completar dicha nueva funcionalidad en el entorno de
producción.^
```
```
Recuperar versión
previa
```
```
Se solicitará reinstalar una versión previa de la
aplicación.^
```
```
Borrar/Desactivar una
funcionalidad
```
```
Se solicitará la desactivación de una nueva función en
la aplicación.
La competición medirá el tiempo tardado en
completar dicha nueva funcionalidad en el entorno de
producción.
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

## ANEXO I: API de servicios REST y verificación funcional

A continuación se incluye una aplicación FastAPI con las instrucciones
correspondientes para ejecutarla. El sistema desarrollado deberá ofrecer este
mismo API REST para la gestión de información.

Independientemente de la implementación, la verificación de funcionamiento
del sistema se automatizará a través de este API con datos preparados para tal
fin.

```
Figura 1 Vista parcial del API REST.
```
```
Figura 2 Generación del API REST a partir del fichero YAML en el Editor de Swagger.
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
Además, se realizarán las siguientes inspecciones de forma manual:
```
```
ID Área Funcional Función de Usuario /
Escenario de Prueba
```
```
¿Funciona?
```
```
1 Clasificación de
información
```
```
Sólo se podrán crear categorías
pertenecientes a IPTC Media
topics de primer nivel^
```
```
Sí / No
```
```
2 Gestión de
usuarios
```
```
Se envía un correo de
verificación de la cuenta
creada.^
```
```
Sí / No
```
```
3 Gestión de
usuarios
```
```
El lector no puede gestionar
alertas.
```
```
Sí / No
```
```
4 Gestión de
notificaciones
```
```
Se envía un correo y un
mensaje al buzón con los
resultados de una indexación
```
```
Sí / No
```
```
5 Interfaz de
usuario
```
```
Visualización de temas más
candentes mediante nubes de
palabras por categoría.
```
```
Sí / No
```
```
6 Interfaz de
usuario
```
```
Visualización de estadísticas
globales de extracción de
información: nº de fuentes, nº
de noticias, nº de noticias por
categoría, nº de alertas y nº de
alertas por categoría
```
```
Sí / No
```
```
7 Interfaz de
usuario
```
```
Se puede cambiar el idioma y
ver la aplicación de usuario en
dos idiomas (no los contenidos).
```
```
Sí / No
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

## ANEXO II: Muestra de ejemplos de pantallas

A continuación se muestran posibles ejemplos de pantallas. Es un interfaz
generado con Google AI Studio^2.

```
Figura 3 Pantalla principal con visualización de métricas globales.
```
(^2) https://ai.studio/apps/fd91d5a0-c916- 4916 - 9f23-957b3948d2ae?fullscreenApplet=true


Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
Figura 4 Pantalla de entrada del usuario.
```
```
Figura 5 Pantalla de creación de cuenta de usuario.
```
```
Figura 6 Pantalla de entrada de usuario registrado.
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
Figura 7 Pantalla de visualización de nubes de palabras globales y por categoría.
```
```
Figura 8 Pantalla de gestión de alertas.
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
Figura 9 Pantalla de creación de alerta.
```
```
Figura 10 Pantalla de gestión de canales RSS.
```

Grado en Ingeniería Informática
Desarrollo y operación de sistemas software

```
Figura 11 Pantalla de gestión del buzón de notificaciones.
```
```
Figura 12 Pantalla de edición perfil de usuario.
```

