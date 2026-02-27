"""
Purpose:
Loads, validates, and sanitizes configuration before it reaches the pipeline.

Description:
Acts as the single entry point for obtaining ready-to-use config objects.
BaseConfig is validated against the filesystem to catch bad paths or values
early. QueryConfig is sanitized against the actual data — invalid regions,
out-of-range years, and unrecognized operations are silently reset to None
rather than propagating errors downstream. Falls back to hardcoded defaults
if the base config file is missing or invalid.

Functions
---------
_validate_base_config(config)
    Internal — raise if any BaseConfig field is invalid or points to a missing path.
_sanitize_region(region, valid_regions)
    Internal — return None if region is not in the DataFrame's known regions.
_sanitize_years(start, end, year_range)
    Internal — clamp or nullify year values that fall outside the data's actual range.
_sanitize_operation(operation)
    Internal — return None if operation is not a recognized aggregation string.
_sanatize_query_config(config, regions, year_range)
    Internal — run all sanitization steps and return a corrected QueryConfig.
get_base_config()
    Load and validate BaseConfig from disk, falling back to defaults on failure.
get_query_config(df)
    Load QueryConfig from disk and sanitize it against the actual DataFrame.

See Also
--------
config_load.load_base_config     : Parses base_config.json into a BaseConfig.
config_load.load_query_config    : Parses query_config.json into a QueryConfig.
config_load.load_default_config  : Returns a hardcoded fallback BaseConfig.
config_models.BaseConfig         : Immutable model for application-level settings.
config_models.QueryConfig        : Immutable model for query parameters.

Notes
-----
- _validate_base_config() raises ValueError or FileNotFoundError on bad input.
- All query sanitization is silent — invalid values are reset to None, never raised.
- get_base_config() swallows all exceptions and falls back to load_default_config().
- get_query_config() requires a loaded DataFrame to validate regions and year range.

Examples
--------
>>> config = get_base_config()
>>> query  = get_query_config(df)

"""

from dataclasses import replace
from typing import Iterable, Tuple, Optional

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from .config_models import BaseConfig, QueryConfig
from .config_load import load_base_config, load_query_config, load_default_config
from .paths import get_base_config_path, get_query_config_path
from src.core.metadata import get_valid_attr


def _validate_base_config(config: BaseConfig) -> None:
    """
    Raise if any field in BaseConfig is invalid or points to a missing path.

    Checks that max_log_size is positive, data_filename is non-empty,
    data_dir exists and is a directory, the data file itself exists inside
    data_dir, and that log_dir (if it exists) is a directory.

    Parameters
    ----------
    config : BaseConfig
        The config object to validate.

    Raises
    ------
    ValueError
        If max_log_size is not positive, data_filename is empty, data_dir
        is not a directory, or log_dir exists but is not a directory.
    FileNotFoundError
        If data_dir or the data file inside it does not exist on disk.
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


def _sanitize_region(
    region: Optional[str], valid_regions: Iterable[str]
) -> Optional[str]:
    """
    Return None if region is not among the known valid regions.

    Parameters
    ----------
    region : str or None
        Region value from QueryConfig.
    valid_regions : Iterable[str]
        Known region names extracted from the actual DataFrame.

    Returns
    -------
    str or None
        Original region if valid, None otherwise.
    """
    if not region:
        return None

    valid_set = {r.lower() for r in valid_regions}

    if region.lower() not in valid_set:
        logger.debug(f"Invalid region '{region}' → resetting to None")
        return None

    return region


def _sanitize_years(
    start: Optional[int], end: Optional[int], year_range: Tuple[int, int]
) -> Tuple[Optional[int], Optional[int]]:
    """
    Nullify year values that fall outside the data's actual range.

    Resets start to None if it precedes the earliest year in the data,
    resets end to None if it exceeds the latest year, and resets both to
    None if end is less than start after individual checks.

    Parameters
    ----------
    start : int or None
        Requested lower bound year.
    end : int or None
        Requested upper bound year.
    year_range : Tuple[int, int]
        (min_year, max_year) derived from the actual DataFrame.

    Returns
    -------
    Tuple[Optional[int], Optional[int]]
        Sanitized (start, end) pair. Either or both may be None.
    """
    min_year, max_year = year_range

    validated_start = start
    validated_end = end

    if validated_start is not None and validated_start < min_year:
        logger.debug(f"startYear {validated_start} out of range → resetting")
        validated_start = None

    if validated_end is not None and validated_end > max_year:
        logger.debug(f"endYear {validated_end} out of range → resetting")
        validated_end = None

    if (
        validated_start is not None
        and validated_end is not None
        and validated_end < validated_start
    ):
        logger.debug("endYear < startYear → resetting both to None")
        return None, None

    return validated_start, validated_end


def _sanitize_operation(operation: Optional[str]) -> Optional[str]:
    """
    Return None if operation is not a recognized aggregation string.

    Parameters
    ----------
    operation : str or None
        Aggregation string from QueryConfig.

    Returns
    -------
    str or None
        Original operation if valid ("sum", "avg", "average"), None otherwise.
    """
    if not operation:
        return None

    valid_ops = {"sum", "avg", "average"}

    if operation.lower() not in valid_ops:
        logger.debug(f"Invalid operation '{operation}' → resetting to None")
        return None

    return operation


def _sanatize_query_config(config: QueryConfig, regions, year_range) -> QueryConfig:
    """
    Run all sanitization steps and return a corrected QueryConfig.

    Applies region, year, and operation sanitization in sequence and
    returns a new frozen QueryConfig with invalid fields reset to None.

    Parameters
    ----------
    config : QueryConfig
        Raw QueryConfig loaded directly from disk.
    regions : Iterable[str]
        Valid region names from the actual DataFrame.
    year_range : Tuple[int, int]
        (min_year, max_year) from the actual DataFrame.

    Returns
    -------
    QueryConfig
        New QueryConfig instance with all invalid fields set to None.
    """
    region = _sanitize_region(config.region, regions)

    start, end = _sanitize_years(config.startYear, config.endYear, year_range)

    operation = _sanitize_operation(config.operation)

    normalized = replace(
        config, region=region, startYear=start, endYear=end, operation=operation
    )

    logger.debug(f"Normalized query config: {normalized}")
    return normalized


def get_base_config() -> BaseConfig:
    """
    Load and validate BaseConfig from disk, falling back to defaults on failure.

    Attempts to read base_config.json and validate it. If the file is missing,
    malformed, or fails validation for any reason, silently falls back to
    load_default_config() instead of propagating the error.

    Returns
    -------
    BaseConfig
        Validated config from disk, or hardcoded defaults on any failure.

    Examples
    --------
    >>> config = get_base_config()
    """
    try:
        base_config = load_base_config(get_base_config_path())
        _validate_base_config(base_config)
    except Exception:
        base_config = load_default_config()

    return base_config


def get_query_config(df: pd.DataFrame) -> QueryConfig:
    """
    Load QueryConfig from disk and sanitize it against the actual DataFrame.

    Reads query_config.json, then validates region, year range, and operation
    against values present in df. Any field that fails validation is silently
    reset to None.

    Parameters
    ----------
    df : pd.DataFrame
        The loaded long-format DataFrame used to derive valid regions and year range.

    Returns
    -------
    QueryConfig
        Sanitized query configuration ready to be passed into the pipeline.

    Examples
    --------
    >>> config = get_query_config(df)
    """
    raw_config = load_query_config(get_query_config_path())
    regions, year_range = get_valid_attr(df)

    return _sanatize_query_config(raw_config, regions, year_range)