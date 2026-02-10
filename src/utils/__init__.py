"""
Utilities Package
=================

Provides cross-cutting utility functions for command-line argument parsing
and logging system initialization. These utilities are used across the
application for consistent behavior.

Modules
-------
args_manager
    Command-line argument parsing for debug mode and file path options
logging_factory
    Logging system initialization with rotating file handlers

Functions
---------
parse_cli_args
    Parse command-line arguments
initialize_logging
    Initialize application-wide logging system

Purpose
-------
The utilities package handles infrastructure concerns that don't fit into
the core business logic or UI layers:

**CLI Management**
    Parse and validate command-line arguments for controlling application
    behavior (debug mode, custom data file paths)

**Logging Infrastructure**
    Set up comprehensive logging with file rotation, appropriate log levels,
    and formatted output for debugging and production monitoring

Command-Line Interface
----------------------
The application supports the following CLI arguments:

--debug
    Enable debug mode with verbose logging and debug log file
-fpath PATH
    Specify custom data file path instead of using default

Examples::

    # Production mode with default data file
    python main.py

    # Debug mode with verbose logging
    python main.py --debug

    # Custom data file
    python main.py -fpath data/custom_gdp.csv

    # Combined options
    python main.py --debug -fpath data/test_data.csv

Logging System
--------------
The logging system provides:

**Dual Mode Operation**
    - Production: ERROR level, writes to ``logs/prod.log``
    - Debug: DEBUG level, writes to ``logs/debug.log``

**Rotating Files**
    - Maximum file size configured via BaseConfig
    - Keeps 3 backup files
    - Automatic rotation when size limit reached

**Structured Output**
    - Timestamp (HH:MM:SS format)
    - Log level
    - Logger name
    - Message

Example log entry::

    14:23:45 [ERROR] main: Failed to load configuration file

Integration
-----------
These utilities are typically used during application initialization:

>>> from src.utils import parse_cli_args, initialize_logging
>>> from src.core.config_manager import load_base_config
>>>
>>> # Parse CLI
>>> args = parse_cli_args()
>>>
>>> # Load config
>>> config = load_base_config(Path("data/configs/base_config.json"))
>>>
>>> # Initialize logging
>>> initialize_logging(config, debug=args.debug)
>>>
>>> # Now logging is available throughout the application
>>> import logging
>>> logger = logging.getLogger(__name__)
>>> logger.info("Application started")

See Also
--------
args_manager.parse_cli_args : CLI argument parser
logging_factory.initialize_logging : Logging system initializer

Notes
-----
The logging system clears existing handlers before initialization to ensure
clean state. This prevents duplicate log entries in long-running applications
or interactive environments.

UTF-8 encoding is enforced for all log files to handle international
characters in region names and error messages.

Error Handling
--------------
argparse.ArgumentError
    Raised for invalid command-line arguments
FileNotFoundError
    Raised if specified file path doesn't exist (at usage time, not parse time)
"""

from .args_manager import parse_cli_args
from .logging_factory import initialize_logging

__all__ = [
    'parse_cli_args',
    'initialize_logging',
]