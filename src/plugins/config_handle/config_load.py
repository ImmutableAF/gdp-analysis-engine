"""
Purpose:
Loads and constructs configuration objects from JSON files or built-in defaults.

Description:
Bridges raw JSON files on disk to the typed config models the rest of the
package depends on. Each loader reads a file, extracts the relevant keys,
and hands back a fully constructed, immutable config object.

Functions
---------
load_base_config(config_path)
    Parse a JSON file into a BaseConfig object.
load_query_config(config_path)
    Parse a JSON file into a QueryConfig object.
load_default_config()
    Return a hardcoded BaseConfig with sensible default values.

Notes
-----
- All functions return validated config model instances, not raw dicts.
- load_default_config() requires no file on disk and is safe to call at any time.
- Missing optional query fields (region, country, etc.) resolve to None via dict.get().

Examples
--------
>>> config = load_base_config(Path("config/base.json"))
>>> config = load_query_config(Path("config/query.json"))
>>> config = load_default_config()
"""

import json
from pathlib import Path
from .config_models import BaseConfig, QueryConfig
import logging

logger = logging.getLogger(__name__)


def load_base_config(config_path: Path) -> BaseConfig:
    """
    Parse a JSON config file into a BaseConfig object.

    Reads the file at config_path, extracts the expected keys, and
    constructs a BaseConfig instance. All fields are required — a missing
    key will raise a KeyError.

    Parameters
    ----------
    config_path : Path
        Path to the JSON file containing base configuration fields:
        data_dir, data_filename, log_dir, max_log_size, and output_mode.

    Returns
    -------
    BaseConfig
        Populated base configuration object.

    Examples
    --------
    >>> config = load_base_config(Path("config/base.json"))
    """
    logger.info(f"Loading base configuration from {config_path}")
    with open(config_path) as f:
        data = json.load(f)
    config = BaseConfig(
        data_dir=Path(data["data_dir"]),
        data_filename=data["data_filename"],
        log_dir=Path(data["log_dir"]),
        max_log_size=data["max_log_size"],
        output_mode=data["output_mode"],
    )
    logger.info(f"Base configuration loaded")
    logger.debug(f"config : {config}")
    return config


def load_query_config(config_path: Path) -> QueryConfig:
    """
    Parse a JSON config file into a QueryConfig object.

    All query fields are optional — any key absent from the file resolves
    to None.

    Parameters
    ----------
    config_path : Path
        Path to the JSON file containing query fields: region, country,
        startYear, endYear, and operation.

    Returns
    -------
    QueryConfig
        Populated query configuration object. Missing fields default to None.

    Examples
    --------
    >>> config = load_query_config(Path("config/query.json"))
    """
    logger.info(f"Loading query configuration from {config_path}")
    with open(config_path) as f:
        data = json.load(f)
    config = QueryConfig(
        region=data.get("region"),
        country=data.get("country"),
        startYear=data.get("startYear"),
        endYear=data.get("endYear"),
        operation=data.get("operation"),
    )
    logger.debug(f"Query configuration loaded: {config}")
    return config


def load_default_config() -> BaseConfig:
    """
    Return a BaseConfig populated with hardcoded default values.

    Used as a fallback when no config file is provided. Safe to call at
    any time — requires no file on disk.

    Returns
    -------
    BaseConfig
        Default configuration with:
        data_dir="data", data_filename="gdp_with_continent_filled.xlsx",
        log_dir="logs", max_log_size=1000000, output_mode="ui".

    Examples
    --------
    >>> config = load_default_config()
    """
    logger.info(f"Loading default configuration")
    config = BaseConfig(
        data_dir=Path("data"),
        data_filename="gdp_with_continent_filled.xlsx",
        log_dir=Path("logs"),
        max_log_size=1000000,
        output_mode="ui",
    )
    logger.debug(f"Default configuration loaded: {config}")
    return config