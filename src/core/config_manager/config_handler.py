import logging
from dataclasses import replace
from .config_models import BaseConfig, QueryConfig

from pathlib import Path

def validate_base_config(config: BaseConfig) -> None:
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

def sanatize_query_config(config: QueryConfig, regions, countries, year_range) -> QueryConfig:
    validated_region = config.region
    validated_country = config.country
    validated_startYear = config.startYear
    validated_endYear = config.endYear
    validated_operation = config.operation
    
    if config.region and config.region.lower() not in [r.lower() for r in regions]:
        validated_region = None
    
    if config.country and config.country.lower() not in [c.lower() for c in countries]:
        validated_country = None
    
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
        country=validated_country,
        startYear=validated_startYear,
        endYear=validated_endYear,
        operation=validated_operation
    )