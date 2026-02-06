import pandas as pd
from pathlib import Path
from core.data_loader.loader_registry import LoaderRegistry
from core.config_manager.config_validator import validate_base_config, validate_query_config
from core.config_manager.config_loader import load_base_config, load_default_config, load_query_config
from core.config_manager.config_models import BaseConfig, QueryConfig
filepath = Path("data/gdp_with_continent_filled.csv")


def load_metadata():
    base_dir = Path(__file__).resolve.parent
    base_config_path = base_dir / "data" / "configs" / "base_config.json"
    query_config_path = base_dir / "data" / "configs" / "query_config.json"
    try:
        base_config = load_base_config(base_config_path)
        validate_base_config(base_config)
    except Exception:
        base_config = load_default_config()

    return base_config, query_config_path

def get_valid_attr(df):
    regions = df["Continent"].unique().tolist()
    countries = df["Country Name"].tolist()

    years = map(int, (filter(str.isdigit, df.columns)))
    year_range = (min(years), max(years))

    return regions, countries, year_range


def load_data(file_path: Path):
    registry = LoaderRegistry()
    df = registry.load(file_path)
    return df

if __name__ == "__main__":
    base_config, query_config_path = load_metadata()
    df = load_data(filepath)

    regions, countries, year_range = get_valid_attr(df)
    query_config = load_query_config(query_config_path)

    validate_query_config(query_config, regions, countries, year_range)

    print(query_config)
    print(df)