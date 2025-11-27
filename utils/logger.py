import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


def get_logger(name: str = "finance_coach") -> logging.Logger:
    """Configure and return a module-level logger with rotating file handler."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    project_root = Path(__file__).resolve().parents[1]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d")
    log_path = logs_dir / f"finance_agent_{timestamp}.log"

    file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    logger.debug("Logger initialized")

    return logger