import json
from pathlib import Path
from config_models import BaseConfig, QueryConfig

def load_base_config(config_path: Path) -> BaseConfig:
    with open(config_path) as f:
        data = json.load(f)
    return BaseConfig(
        data_dir=Path(data["data_dir"]),
        default_file=data["default_file"],
        log_dir=Path(data["log_dir"]),
        max_log_size_bytes=data["max_log_size_bytes"],
        default_logging_level=data["default_logging_level"]
    )

def load_query_config(config_path: Path) -> QueryConfig:
    with open(config_path) as f:
        data = json.load(f)
    return QueryConfig(
        region=data.get("region"),
        year=data.get("year"),
        country=data.get("country"),
        operation=data["operation"],
        dashboard_charts=data.get("dashboard_charts", [])
    )
