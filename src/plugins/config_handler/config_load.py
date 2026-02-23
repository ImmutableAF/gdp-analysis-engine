"""
Configuration File Loaders
===========================

JSON loading functions for BaseConfig and QueryConfig. Converts raw JSON
dictionaries to validated immutable dataclass instances.

Functions
---------
load_base_config(config_path)
    Load BaseConfig from JSON file
load_query_config(config_path)
    Load QueryConfig from JSON file
load_default_config()
    Create BaseConfig with hardcoded defaults

See Also
--------
config_models : Configuration dataclasses
config_handler : Validation functions

Notes
-----
Path fields automatically converted from strings to Path objects.
QueryConfig uses .get() for optional fields (returns None if missing).

Examples
--------
>>> config = load_base_config(Path("data/configs/base_config.json"))
>>> query = load_query_config(Path("data/configs/query_config.json"))
>>> default = load_default_config()
"""

import json
from pathlib import Path
from .config_models import BaseConfig, QueryConfig
import logging
logger = logging.getLogger(__name__)

def load_base_config(config_path: Path) -> BaseConfig:
    """
    Load system configuration from JSON file.

    Parameters
    ----------
    config_path : Path
        Path to JSON config file

    Returns
    -------
    BaseConfig
        Immutable configuration instance

    Raises
    ------
    FileNotFoundError
        If config file doesn't exist
    json.JSONDecodeError
        If JSON is malformed
    KeyError
        If required fields missing

    Examples
    --------
    >>> config = load_base_config(Path("data/configs/base_config.json"))
    >>> print(config.data_dir)
    data
    """
    logger.info(f"Loading base configuration from {config_path}")
    with open(config_path) as f:
        data = json.load(f)
    config = BaseConfig(
        data_dir=Path(data["data_dir"]),
        data_filename=data["data_filename"],
        log_dir=Path(data["log_dir"]),
        max_log_size=data["max_log_size"],
    )
    logger.info(f"Base configuration loaded")
    logger.debug(f"config : {config}")
    return config

def load_query_config(config_path: Path) -> QueryConfig:
    """
    Load query parameters from JSON file.

    Parameters
    ----------
    config_path : Path
        Path to JSON config file

    Returns
    -------
    QueryConfig
        Immutable query configuration

    Raises
    ------
    FileNotFoundError
        If config file doesn't exist
    json.JSONDecodeError
        If JSON is malformed

    Notes
    -----
    Uses .get() for all fields - missing fields become None.

    Examples
    --------
    >>> query = load_query_config(Path("data/configs/query_config.json"))
    >>> print(query.region)
    Asia
    """
    logger.info(f"Loading query configuration from {config_path}")
    with open(config_path) as f:
        data = json.load(f)
    config =  QueryConfig(
        region=data.get("region"),
        country=data.get("country"),
        startYear=data.get("startYear"),
        endYear=data.get("endYear"),
        operation=data.get("operation")
    )
    logger.debug(f"Query configuration loaded: {config}")
    return config

def load_default_config() -> BaseConfig:
    """
    Create BaseConfig with hardcoded default values.

    Returns
    -------
    BaseConfig
        Configuration with standard defaults

    Notes
    -----
    Default values:
    - data_dir: "data"
    - data_filename: "gdp_with_continent_filled.csv"
    - log_dir: "logs"
    - max_log_size: 1000000 bytes (1 MB)

    Examples
    --------
    >>> config = load_default_config()
    >>> print(config.data_filename)
    gdp_with_continent_filled.csv
    """
    logger.info(f"Loading default configuration")
    config =  BaseConfig(
        data_dir=Path("data"),
        data_filename="gdp_with_continent_filled.xlsx",
        log_dir=Path("logs"),
        max_log_size=1000000
    )
    logger.debug(f"Default configuration loaded: {config}")
    return config