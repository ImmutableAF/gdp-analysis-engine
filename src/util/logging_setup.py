"""
Logging System Factory
======================

Configures rotating file handler for application logging with dual-mode
support (production/debug).

Functions
---------
initialize_logging(base_config, debug)
    Setup rotating file handler with mode-specific configuration

See Also
--------
config_manager.BaseConfig : System configuration with log settings

Notes
-----
Logging modes:
- Production: ERROR level, prod.log file
- Debug: DEBUG level, debug.log file

Both modes use RotatingFileHandler with 3 backup files and UTF-8 encoding.
Log directory created automatically if missing.

Examples
--------
>>> from config_manager import BaseConfig
>>> config = BaseConfig(Path("data"), "gdp.csv", Path("logs"), 1000000)
>>> initialize_logging(config, debug=True)
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .logging_contract import LogPolicy

def initialize_logging(base_config: LogPolicy, debug: bool = False) -> None:
    """
    Initialize rotating file handler for application logging.
    
    Creates log directory, configures handler with rotation, and sets root
    logger level based on debug flag.
    
    Parameters
    ----------
    base_config : BaseConfig
        Configuration with log_directory and max_log_size
    debug : bool, default=False
        If True, use DEBUG level and debug.log; if False, use ERROR level and prod.log
    
    Notes
    -----
    Configuration:
    - File rotation: maxBytes from config, 3 backups
    - Format: "HH:MM:SS [LEVEL] logger_name: message"
    - Encoding: UTF-8
    - Clears existing handlers before adding new one
    
    Log directory created with parents=True if it doesn't exist.
    
    Examples
    --------
    Production mode:
    >>> config = BaseConfig(Path("data"), "gdp.csv", Path("logs"), 1000000)
    >>> initialize_logging(config, debug=False)
    # Creates logs/prod.log at ERROR level
    
    Debug mode:
    >>> initialize_logging(config, debug=True)
    # Creates logs/debug.log at DEBUG level
    """
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
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    root_logger.setLevel(log_level)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    root_logger.info(f"Logger initialized. Log file: {log_file}, Level: {logging.getLevelName(log_level)}")