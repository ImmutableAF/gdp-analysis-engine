import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import AppConfig


def create_file_logger(config: AppConfig, debug: bool) -> None:
    config.log_dir.mkdir(exist_ok=True)

    log_file = (
        config.debug_log_file if debug else config.prod_log_file
    )
    level = logging.DEBUG if debug else logging.ERROR

    handler = RotatingFileHandler(
        log_file,
        maxBytes=config.max_log_size_bytes,
        backupCount=config.backup_count,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
