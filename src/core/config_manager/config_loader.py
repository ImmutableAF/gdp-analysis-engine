import json
from pathlib import Path
from .config_models import BaseConfig, QueryConfig


def load_base_config(config_path: Path) -> BaseConfig:
    with open(config_path) as f:
        data = json.load(f)
    return BaseConfig(
        data_directory=Path(data["data_directory"]),
        default_file=data["default_file"],
        log_directory=Path(data["log_directory"]),
        max_log_size=data["max_log_size"]
    )

def load_query_config(config_path: Path) -> QueryConfig:
    with open(config_path) as f:
        data = json.load(f)
    return QueryConfig(
        region=data.get("region"),
        startYear=data.get("startYear"),
        endYear=data.get("endYear"),      
        country=data.get("country"),
        operation=data.get("operation")
    )

def load_default_config() -> BaseConfig:
    return BaseConfig(
        data_directory=Path("data"), 
        default_file="gdp_with_continent_filled.csv", 
        log_directory=Path("logs"),
        max_log_size=1000000,
        logging_level="INFO"
    )