"""
Configuration Validation and Sanitization
==========================================

Validation and sanitization functions for configurations. BaseConfig validated
with exceptions, QueryConfig sanitized by setting invalid values to None.

Functions
---------
validate_base_config(config)
    Validate system configuration (raises on errors)
sanatize_query_config(config, regions, year_range)
    Sanitize query config against valid regions/years

See Also
--------
config_models : Configuration dataclasses
config_loader : Loading functions

Notes
-----
Different error handling strategies:
- BaseConfig: Raises exceptions (system configuration must be valid)
- QueryConfig: Sets invalid fields to None (user input may be partial/invalid)

Examples
--------
>>> validate_base_config(config)  # Raises if invalid
>>> clean_query = sanatize_query_config(query, ["Asia", "Europe"], (1960, 2020))
"""
from pathlib import Path
from dataclasses import replace

import pandas as pd

from .config_models import BaseConfig, QueryConfig
from .config_load import load_base_config, load_query_config, load_default_config

from .paths import get_base_config_path, get_query_config_path
from .metadata import get_valid_attr

def _validate_base_config(config: BaseConfig) -> None:
    """
    Validate system configuration constraints.

    Validates paths exist, log size positive, and default file accessible.
    Raises exceptions on validation failures.

    Parameters
    ----------
    config : BaseConfig
        Configuration to validate

    Raises
    ------
    ValueError
        If max_log_size <= 0, data_filename empty, or paths invalid
    FileNotFoundError
        If data_dir or data_filename doesn't exist

    Notes
    -----
    Validation checks:
    1. max_log_size > 0
    2. data_filename non-empty string
    3. data_dir exists and is directory
    4. data_filename exists in data_dir
    5. log_dir is directory if it exists

    Examples
    --------
    >>> config = BaseConfig(Path("data"), "gdp.csv", Path("logs"), 1000000)
    >>> validate_base_config(config)  # Passes if valid, raises if not
    """
    if config.max_log_size <= 0:
        raise ValueError("max_log_size must be positive")

    if not config.data_filename or not config.data_filename.strip():
        raise ValueError("data_filename cannot be empty")

    if not config.data_dir.exists():
        raise FileNotFoundError(f"data_dir does not exist: {config.data_dir}")

    if not config.data_dir.is_dir():
        raise ValueError(f"data_dir is not a directory: {config.data_dir}")

    default_path = config.data_dir / config.data_filename
    if not default_path.is_file():
        raise FileNotFoundError(f"data_filename not found: {default_path}")

    if config.log_dir.exists() and not config.log_dir.is_dir():
        raise ValueError(f"log_dir is not a directory: {config.log_dir}")

def _sanatize_query_config(config: QueryConfig, regions, year_range) -> QueryConfig:
    """
    Sanitize query configuration against valid regions and year range.

    Sets invalid fields to None rather than raising exceptions. Allows
    graceful handling of partial or invalid user input.

    Parameters
    ----------
    config : QueryConfig
        Query configuration to sanitize
    regions : list
        Valid region names (case-insensitive comparison)
    year_range : tuple of (int, int)
        Valid (min_year, max_year) range

    Returns
    -------
    QueryConfig
        New config with invalid fields set to None

    Notes
    -----
    Sanitization rules:
    - region: Set to None if not in regions list (case-insensitive)
    - startYear: Set to None if < year_range[0]
    - endYear: Set to None if > year_range[1]
    - Both years: Set to None if endYear < startYear
    - operation: Set to None if not in ["sum", "avg", "average"]

    Examples
    --------
    >>> query = QueryConfig("InvalidRegion", 1950, 2025, "median")
    >>> clean = sanatize_query_config(query, ["Asia"], (1960, 2020))
    >>> print(clean)
    QueryConfig(region=None, startYear=None, endYear=None, operation=None)
    """
    validated_region = config.region
    validated_startYear = config.startYear
    validated_endYear = config.endYear
    validated_operation = config.operation

    if config.region and config.region.lower() not in [r.lower() for r in regions]:
        validated_region = None

    if config.startYear is not None and config.startYear < year_range[0]:
        validated_startYear = None

    if config.endYear is not None and config.endYear > year_range[1]:
        validated_endYear = None

    if config.endYear < config.startYear:
        config.startYear = None
        config.endYear = None

    if config.operation and config.operation.lower() not in ["sum", "avg", "average"]:
        validated_operation = None

    return replace(
        config,
        region=validated_region,
        startYear=validated_startYear,
        endYear=validated_endYear,
        operation=validated_operation
    )

def get_base_config() -> BaseConfig:
    """
    Load and validate base configuration with fallback to defaults.

    Attempts to load from file and validate. On any failure (missing file,
    invalid JSON, validation error), falls back to hardcoded defaults.

    Parameters
    ----------
    base_config_path : Path
        Path to base_config.json

    Returns
    -------
    BaseConfig
        Validated configuration or defaults

    Notes
    -----
    Exceptions silently caught - always returns valid config. Use for
    graceful degradation when config files unavailable.

    Examples
    --------
    >>> config = get_base_config(Path("data/configs/base_config.json"))
    >>> print(config.data_dir)
    data
    """
    try:
        base_config = load_base_config(get_base_config_path())
        _validate_base_config(base_config)
    except Exception as e:
        #print(f"error in loading or validating base config : {e}")
        base_config = load_default_config()

    return base_config

def get_query_config(df: pd.DataFrame) -> QueryConfig:
    """
    Load and sanitize query configuration against DataFrame.

    Loads query config from file and validates regions/years against actual
    data. Invalid values set to None.

    Parameters
    ----------
    df : pd.DataFrame
        Wide-format data for validation

    Returns
    -------
    QueryConfig
        Sanitized query configuration

    Notes
    -----
    Extracts valid regions and year range from df, then sanitizes loaded
    config against these constraints.

    Examples
    --------
    >>> df = load_data(Path("data/gdp_data.csv"))
    >>> query = get_query_config(df)
    >>> print(query.region)
    Asia
    """
    query_config = _sanatize_query_config(load_query_config(get_query_config_path()), *get_valid_attr(df))
    return query_config