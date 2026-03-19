"""
Logging configuration for the trading bot.

Sets up a logger named "trading_bot" with:
- Console handler at INFO level
- Rotating file handler at DEBUG level (logs/trading_bot.log)
"""

import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(module)s] - %(message)s"

MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


def setup_logger() -> logging.Logger:
    """Create and configure the trading_bot logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Ensure logs directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("trading_bot")

    # Prevent adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOG_FORMAT)

    # ── Console handler (INFO) ──────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # ── Rotating file handler (DEBUG) ───────────────────────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
