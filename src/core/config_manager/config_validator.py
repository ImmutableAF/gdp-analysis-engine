import logging
from .config_models import BaseConfig, QueryConfig

def validate_base_config(config: BaseConfig) -> None:
    try:
        if config.max_log_size <= 0:
            raise ValueError(f"max_log_size must be positive.")
        if not config.default_file or not config.default_file.strip():
            raise ValueError(f"default_file cannot be empty.")
        if not hasattr(logging, config.logging_level.upper()):
            raise ValueError(f"Invalid logging_level: '{config.logging_level}'")
    except (ValueError, AttributeError) as e:
        print(f"BaseConfig validation failed: {e}. Using default configuration.")
    
def validate_query_config(config: QueryConfig, regions, countries, year_range) -> None:
    if config.region not in regions:
        config.region = None
    if config.country not in countries:
        config.country = None
    if year_range[0] > config.year or config.year > year_range[1]:
        config.year = None
    if config.operation not in ["sum", "avg"]:
        config.operation = None