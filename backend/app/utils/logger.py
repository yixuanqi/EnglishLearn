"""Logger configuration."""

import logging
import sys
from typing import Any

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure application logging."""
    logger = logging.getLogger("english_trainer")
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = setup_logging()
