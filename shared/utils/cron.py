from __future__ import annotations

from datetime import datetime, timedelta, timezone

from croniter import croniter


def floor_to_minute(value: datetime) -> datetime:
    """Normaliza un datetime a UTC con precision de minuto."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(second=0, microsecond=0)


def validate_minute_cron_expression(expression: str) -> None:
    """Valida cron de 5 campos (resolucion minima: 1 minuto)."""
    parts = expression.split()
    if len(parts) != 5:
        raise ValueError(
            "cron_expression debe usar exactamente 5 campos "
            "(minuto hora dia mes dia-semana)"
        )
    if not croniter.is_valid(expression):
        raise ValueError("cron_expression no es una expresion cron valida")


def next_run_on_or_after(expression: str, reference: datetime) -> datetime:
    """Devuelve la primera ejecucion programada >= minuto de referencia."""
    validate_minute_cron_expression(expression)
    start = floor_to_minute(reference)
    # Se usa el minuto anterior como base para obtener el primer match >= start.
    return croniter(expression, start - timedelta(minutes=1)).get_next(datetime)


def next_run_after(expression: str, reference: datetime) -> datetime:
    """Devuelve la primera ejecucion programada > minuto de referencia."""
    validate_minute_cron_expression(expression)
    start = floor_to_minute(reference)
    return croniter(expression, start).get_next(datetime)


__all__ = [
    "floor_to_minute",
    "next_run_after",
    "next_run_on_or_after",
    "validate_minute_cron_expression",
]