import logging
import pandas as pd
from pathlib import Path
from typing import Tuple
import keyboard as keyboard

from src.utils.args_manager import parse_cli_args
from src.utils.logging_factory import initialize_logging
from src.core.data_loader.loader_registry import LoaderRegistry
from src.core.config_manager.config_models import BaseConfig
from src.core.config_manager.config_models import QueryConfig
from src.pipeline.orchesterator import run_pipeline
from src.core.config_manager.config_handler import validate_base_config, sanatize_query_config
from src.core.config_manager.config_loader import load_base_config, load_default_config, load_query_config

def get_paths() -> Tuple[Path, Path]:
    base_dir = Path(__file__).parent

    base_config_path = base_dir / "data" / "configs" / "base_config.json"
    query_config_path = base_dir / "data" / "configs" / "query_config.json"

    return base_config_path, query_config_path

def get_base_config(base_config_path: Path) -> BaseConfig:
    try:
        base_config = load_base_config(base_config_path)
        validate_base_config(base_config)
    except Exception as e:
        base_config = load_default_config()

    return base_config

def get_valid_attr(df):
    regions = df["Continent"].unique().tolist()
    countries = df["Country Name"].unique().tolist()

    years = list(map(int, filter(str.isdigit, df.columns)))
    year_range = (min(years), max(years))

    return regions, countries, year_range

def load_data(file_path: Path) -> pd.Dataframe:
    registry = LoaderRegistry()
    df = registry.load(file_path)
    return df

if __name__ == "__main__":
    args = parse_cli_args()
    base_config = get_base_config(get_paths()[0])
    initialize_logging(base_config, args.debug)
    logger = logging.getLogger("main")
    
    filepath = Path(args.fpath) if args.fpath and Path(args.fpath).is_file() else base_config.data_directory / base_config.default_file
    logger.debug(f"filepath of data : {filepath}")

    df = load_data(filepath)
    logger.info("data is not empty") if not df.empty else None

    query_config = sanatize_query_config(load_query_config(get_paths()[1]), *get_valid_attr(df))
    logger.debug(f"query config : {query_config}")

    run_pipeline(df, query_config)