import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config_models import BaseConfig


def create_file_logger(base_config: BaseConfig, debug: bool = False) -> None:
    """
    Create a rotating file logger for the application.
    Logs debug-level messages if debug=True, otherwise logs only errors/critical.
    The logger uses paths and settings from BaseConfig.
    """
    # Ensure the log directory exists
    base_config.log_dir.mkdir(parents=True, exist_ok=True)

    # Decide log file based on mode
    log_file = base_config.log_dir / ("debug.log" if debug else "prod.log")

    # Set logging level
    log_level = logging.DEBUG if debug else logging.ERROR

    # Configure rotating file handler
    handler = RotatingFileHandler(
        log_file,
        maxBytes=getattr(base_config, "max_log_size_bytes", 10_000_000),
        backupCount=getattr(base_config, "backup_count", 5),
        encoding="utf-8"
    )

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Clear any existing handlers to avoid duplicate logs
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # log that logger has been initialized
    root_logger.debug(f"Logger initialized. Log file: {log_file}, Level: {logging.getLevelName(log_level)}")
