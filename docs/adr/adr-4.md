# ADR 004: Tecnología de Frontend

* **Fecha:** 12/03/2026
* **Decisores:** Equipo NewsRadar 

## Contexto
El sistema requiere un Dashboard dinámico con visualizaciones de datos (nubes de palabras y estadísticas) y una gestión fluida de alertas y fuentes.

## Decisión
Utilizar **React.js** .

## Motivo
1. **Componentización:** Permite reutilizar elementos de la interfaz (como las tarjetas de noticias o los formularios de alertas), facilitando el trabajo paralelo de los 2 miembros de frontend.
2. **Ecosistema de Visualización:** React posee librerías maduras (como `d3-cloud` o `recharts`) para implementar las nubes de palabras exigidas.
3. **SPA (Single Page Application):** Mejora la experiencia de usuario al evitar recargas de página, consumiendo la API de FastAPI de forma asíncrona.

## Consecuencias
* Se requiere configurar un entorno de Node.js en Docker para el desarrollo y build de la aplicación.
