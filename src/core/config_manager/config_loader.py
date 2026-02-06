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
        max_log_size=data["max_log_size"],
        logging_level=data["logging_level"]
    )

def load_query_config(config_path: Path) -> QueryConfig:
    with open(config_path) as f:
        data = json.load(f)
    return QueryConfig(
        region=data.get("region"),
        year=data.get("year"),
        country=data.get("country"),
        operation=data.get("operation")
    )

def load_default_config() -> BaseConfig:
    return BaseConfig(
        data_directory= "data",
        default_file= Path("gdp_with_continent_filled.csv"),
        log_directory= Path("logs"),
        max_log_size= 10000000,
        logging_level= "INFO"
    )