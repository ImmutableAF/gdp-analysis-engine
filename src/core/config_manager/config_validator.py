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
    
def validate_query_config(config: QueryConfig) -> QueryConfig:
    try:
        if not config.operation or not config.operation.strip():
            raise ValueError(f"Operation cannot be empty.")
        if config.region is not None:
            if not config.region.strip():
                raise ValueError(f"Region cannot be empty string.")
        if config.year is not None:
            if config.year < 1600 or config.year > 2024:
                raise ValueError(f"Invalid year: {config.year}. Must be between 1900 and 2024.")
        if config.country is not None:
            if not config.country.strip():
                raise ValueError(f"Country cannot be empty string.")
        return config
    except (ValueError, AttributeError) as e:
        print(f"QueryConfig validation failes: {e}. Using default configuration.")
      