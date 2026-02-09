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

import logging
from dataclasses import replace
from .config_models import BaseConfig, QueryConfig
from pathlib import Path


def validate_base_config(config: BaseConfig) -> None:
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
        If max_log_size <= 0, default_file empty, or paths invalid
    FileNotFoundError
        If data_directory or default_file doesn't exist
    
    Notes
    -----
    Validation checks:
    1. max_log_size > 0
    2. default_file non-empty string
    3. data_directory exists and is directory
    4. default_file exists in data_directory
    5. log_directory is directory if it exists
    
    Examples
    --------
    >>> config = BaseConfig(Path("data"), "gdp.csv", Path("logs"), 1000000)
    >>> validate_base_config(config)  # Passes if valid, raises if not
    """
    if config.max_log_size <= 0:
        raise ValueError("max_log_size must be positive")

    if not config.default_file or not config.default_file.strip():
        raise ValueError("default_file cannot be empty")

    if not config.data_directory.exists():
        raise FileNotFoundError(f"data_directory does not exist: {config.data_directory}")

    if not config.data_directory.is_dir():
        raise ValueError(f"data_directory is not a directory: {config.data_directory}")

    default_path = config.data_directory / config.default_file
    if not default_path.is_file():
        raise FileNotFoundError(f"default_file not found: {default_path}")

    if config.log_directory.exists() and not config.log_directory.is_dir():
        raise ValueError(f"log_directory is not a directory: {config.log_directory}")


def sanatize_query_config(config: QueryConfig, regions, year_range) -> QueryConfig:
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