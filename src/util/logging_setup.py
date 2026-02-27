"""
Purpose:
Configures the root logger with a rotating file handler for the application.

Description:
Sets up logging to a file that rotates when it reaches a size limit, keeping
the last 3 backups. Switches between debug.log and prod.log based on the
debug flag, and sets the log level to DEBUG or ERROR accordingly.

Functions
---------
initialize_logging(base_config, debug)
    Configure the root logger with a rotating file handler.

Notes
-----
- Clears any existing handlers on the root logger before adding the new one.
- Log directory is created automatically if it does not exist.
- max_log_size falls back to 100000 bytes if not present on base_config.

Examples
--------
>>> initialize_logging(base_config, debug=True)
>>> initialize_logging(base_config, debug=False)
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .logging_contract import LogPolicy


def initialize_logging(base_config: LogPolicy, debug: bool = False) -> None:
    """
    Configure the root logger with a rotating file handler.

    Creates the log directory if it does not exist. Selects debug.log at
    DEBUG level or prod.log at ERROR level based on the debug flag. Builds
    a RotatingFileHandler that rotates when the file reaches max_log_size,
    keeping the last 3 backups. Attaches a formatter that includes timestamp,
    level, logger name, and message. Clears all existing handlers on the root
    logger before attaching the new one.

    Parameters
    ----------
    base_config : LogPolicy
        Config object with log_dir (Path) and max_log_size (int) attributes.
    debug : bool
        If True, writes to debug.log at DEBUG level.
        If False, writes to prod.log at ERROR level. Default is False.

    Returns
    -------
    None

    Examples
    --------
    >>> initialize_logging(base_config, debug=True) 
    >>> initialize_logging(base_config, debug=False)
    """
    
    base_config.log_dir.mkdir(parents=True, exist_ok=True)

    log_file = base_config.log_dir / ("debug.log" if debug else "prod.log")
    log_level = logging.DEBUG if debug else logging.ERROR

    handler = RotatingFileHandler(
        log_file,
        maxBytes=getattr(base_config, "max_log_size", 100000),
        backupCount=3,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    root_logger.setLevel(log_level)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    root_logger.info(f"Logger initialized. Log file: {log_file}, Level: {logging.getLevelName(log_level)}")