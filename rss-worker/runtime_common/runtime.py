from __future__ import annotations

import logging


def configure_logging(worker_name: str) -> None:
    """Configura un formato de logs consistente para cada worker."""
    logging.basicConfig(
        level=logging.INFO,
        format=f"[{worker_name}] %(asctime)s %(levelname)s %(message)s",
    )
