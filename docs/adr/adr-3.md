# ADR 003: Framework de Desarrollo API

* **Fecha:** 12/03/2026
* **Decisores:** Equipo NewsRadar (6 miembros)

## Contexto
La asignatura exige una API REST documentada bajo el estándar OpenAPI/Swagger y una arquitectura modular fácil de testear.

## Decisión
Utilizar **FastAPI** como framework web.

## Motivo
1. **Documentación Nativa:** Genera automáticamente la interfaz Swagger UI (`/docs`), cumpliendo con los requisitos de la asignatura.
2. **Velocidad y Asincronía:** Soporte nativo para `async/await`, crucial para las llamadas de red a los feeds RSS.
3. **Validación de Datos:** Pydantic garantiza que los datos de entrada y salida cumplen con los requisitos definidos, reduciendo errores en producción.

## Consecuencias
* Se requiere definir modelos de datos claros antes de implementar los endpoints para facilitar el trabajo del equipo de Frontend.
