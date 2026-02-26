from dataclasses import replace
from typing import Iterable, Tuple, Optional

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from .config_models import BaseConfig, QueryConfig
from .config_load import load_base_config, load_query_config, load_default_config
from .paths import get_base_config_path, get_query_config_path
from ...core.metadata import get_valid_attr


def _validate_base_config(config: BaseConfig) -> None:
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

    if not operation:
        return None

    valid_ops = {"sum", "avg", "average"}

    if operation.lower() not in valid_ops:
        logger.debug(f"Invalid operation '{operation}' → resetting to None")
        return None

    return operation


def _sanatize_query_config(config: QueryConfig, regions, year_range) -> QueryConfig:

    region = _sanitize_region(config.region, regions)

    start, end = _sanitize_years(config.startYear, config.endYear, year_range)

    operation = _sanitize_operation(config.operation)

    normalized = replace(
        config, region=region, startYear=start, endYear=end, operation=operation
    )

    logger.debug(f"Normalized query config: {normalized}")
    return normalized


def get_base_config() -> BaseConfig:
    try:
        base_config = load_base_config(get_base_config_path())
        _validate_base_config(base_config)
    except Exception:
        base_config = load_default_config()

    return base_config


def get_query_config(df: pd.DataFrame) -> QueryConfig:
    raw_config = load_query_config(get_query_config_path())
    regions, year_range = get_valid_attr(df)

    return _sanatize_query_config(raw_config, regions, year_range)
