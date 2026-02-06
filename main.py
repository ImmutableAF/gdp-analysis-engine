import pandas as pd
from pathlib import Path

from src.core.data_loader.loader_registry import LoaderRegistry
from src.core.config_manager.config_handler import validate_base_config, sanatize_query_config
from src.core.config_manager.config_loader import load_base_config, load_default_config, load_query_config

def load_metadata():
    base_dir = Path(__file__).resolve().parent

    base_config_path = base_dir / "data" / "configs" / "base_config.json"
    query_config_path = base_dir / "data" / "configs" / "query_config.json"

    try:
        base_config = load_base_config(base_config_path)
        validate_base_config(base_config)
    except Exception as e:  # CHANGED: added exception variable to log if needed
        print(f"Failed to load base config: {e}. Using defaults.")  # CHANGED: added error message
        base_config = load_default_config()

    return base_config, query_config_path

def get_valid_attr(df):
    regions = df["Continent"].unique().tolist()
    countries = df["Country Name"].unique().tolist()  # CHANGED: added .unique() to avoid duplicates

    years = list(map(int, filter(str.isdigit, df.columns)))
    year_range = (min(years), max(years))

    return regions, countries, year_range

def load_data(file_path: Path):
    registry = LoaderRegistry()
    df = registry.load(file_path)
    return df

if __name__ == "__main__":
    base_config, query_config_path = load_metadata()
    
    filepath = base_config.data_directory / base_config.default_file
    df = load_data(filepath)
    
    query_config = sanatize_query_config(load_query_config(query_config_path), *get_valid_attr(df))

    print(query_config)