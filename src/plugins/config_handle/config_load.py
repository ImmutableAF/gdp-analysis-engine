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
load_analytics_config(config_path)
    Parse a JSON file into an AnalyticsConfig object.
load_default_config()
    Return a hardcoded BaseConfig with sensible default values.
load_default_analytics_config()
    Return a hardcoded AnalyticsConfig with sensible default values.

Notes
-----
- All functions return validated config model instances, not raw dicts.
- load_default_config() and load_default_analytics_config() require no file
  on disk and are safe to call at any time.
- Missing optional fields in analytics/query configs resolve to None via dict.get().
"""

import json
import logging
from pathlib import Path

from .config_models import BaseConfig, QueryConfig, AnalyticsConfig

logger = logging.getLogger(__name__)


def load_base_config(config_path: Path) -> BaseConfig:
    """
    Parse a JSON config file into a BaseConfig object.

    Parameters
    ----------
    config_path : Path
        Path to the JSON file containing base configuration fields.

    Returns
    -------
    BaseConfig
        Populated base configuration object.
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
    logger.info("Base configuration loaded")
    logger.debug(f"config: {config}")
    return config


def load_query_config(config_path: Path) -> QueryConfig:
    """
    Parse a JSON config file into a QueryConfig object.

    All query fields are optional — any key absent from the file resolves to None.

    Parameters
    ----------
    config_path : Path
        Path to the JSON file containing query fields.

    Returns
    -------
    QueryConfig
        Populated query configuration object. Missing fields default to None.
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


def load_analytics_config(config_path: Path) -> AnalyticsConfig:
    """
    Parse a JSON config file into an AnalyticsConfig object.

    All fields are optional — any key absent from the file resolves to None,
    which causes the views layer to fall back to safe defaults.

    Parameters
    ----------
    config_path : Path
        Path to analytics_config.json.

    Returns
    -------
    AnalyticsConfig
        Populated analytics configuration object. Missing fields default to None.

    Raises
    ------
    ValueError
        If a present field has an incorrect type (e.g. a string where int is expected).
    """
    logger.info(f"Loading analytics configuration from {config_path}")
    with open(config_path) as f:
        data = json.load(f)

    # Type-check every field that is present — wrong types are caught early
    # rather than silently producing bad widget defaults.
    int_fields = [
        "defaultYear",
        "startYear",
        "endYear",
        "topN",
        "consecutiveYears",
        "referenceYear",
    ]
    for field in int_fields:
        value = data.get(field)
        if value is not None and not isinstance(value, int):
            raise ValueError(
                f"analytics_config.json: field '{field}' must be an integer, got {type(value).__name__!r}"
            )

    config = AnalyticsConfig(
        continent=data.get("continent"),
        defaultYear=data.get("defaultYear"),
        startYear=data.get("startYear"),
        endYear=data.get("endYear"),
        topN=data.get("topN"),
        consecutiveYears=data.get("consecutiveYears"),
        referenceYear=data.get("referenceYear"),
    )
    logger.debug(f"Analytics configuration loaded: {config}")
    return config


def load_default_config() -> BaseConfig:
    """
    Return a BaseConfig populated with hardcoded default values.

    Used as a fallback when no config file is provided.

    Returns
    -------
    BaseConfig
        Default configuration.
    """
    logger.info("Loading default base configuration")
    config = BaseConfig(
        data_dir=Path("data"),
        data_filename="gdp_with_continent_filled.xlsx",
        log_dir=Path("logs"),
        max_log_size=1000000,
        output_mode="ui",
    )
    logger.debug(f"Default base configuration loaded: {config}")
    return config


def load_default_analytics_config() -> AnalyticsConfig:
    """
    Return an AnalyticsConfig populated with hardcoded default values.

    Used as a fallback when analytics_config.json is missing or invalid.
    All values are intentionally conservative and always valid.

    Returns
    -------
    AnalyticsConfig
        Default analytics configuration.
    """
    logger.info("Loading default analytics configuration")
    config = AnalyticsConfig(
        defaultYear=2020,
        startYear=2015,
        endYear=2020,
        topN=10,
        consecutiveYears=3,
        referenceYear=2020,
    )
    logger.debug(f"Default analytics configuration loaded: {config}")
    return config
