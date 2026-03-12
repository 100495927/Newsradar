# ADR 001: Selección de Lenguaje de Programación y Versión

* **Fecha:** 12/03/2026
* **Decisores:** Equipo NewsRadar (6 miembros)

## Contexto
El proyecto NewsRadar requiere una alta eficiencia en el procesamiento de texto (NLP), manejo de concurrencia para la extracción de feeds RSS y facilidad de despliegue en contenedores.

## Decisión
Utilizaremos **Python 3.12-slim** como base del desarrollo.

## Motivo
1. **Rendimiento:** Python 3.12 introduce mejoras significativas en la velocidad de ejecución y manejo de tipos.
2. **Ecosistema:** Disponibilidad de librerías clave como FastAPI, Pydantic y clientes asíncronos para MongoDB (Motor).
3. **DevOps (Optimización):** La variante `-slim` reduce el tamaño de las imágenes Docker (aprox. 150MB frente a los >900MB de la versión completa), acelerando los tiempos de build y despliegue en el pipeline.

## Consecuencias
* Todos los desarrolladores deben usar `venv` o `conda` con la versión 3.12.
* Se debe asegurar la compatibilidad de librerías externas con esta versión.
