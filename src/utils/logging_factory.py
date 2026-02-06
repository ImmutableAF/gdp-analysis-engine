import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..core.config_manager.config_models import BaseConfig


def initialize_logging(base_config: BaseConfig, debug: bool = False) -> None:

    base_config.log_directory.mkdir(parents=True, exist_ok=True)

    log_file = base_config.log_directory / ("debug.log" if debug else "prod.log")
    log_level = logging.DEBUG if debug else logging.ERROR

    handler = RotatingFileHandler(
        log_file,
        maxBytes=getattr(base_config, "max_log_size", 100000),
        backupCount=3,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    root_logger.info(f"Logger initialized. Log file: {log_file}, Level: {logging.getLevelName(log_level)}")