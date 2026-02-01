# pipeline/filter.py
import pandas as pd
from config_models import QueryConfig


def filter_data(df: pd.DataFrame, config: QueryConfig) -> pd.DataFrame:
    """
    Filter DataFrame based on query_config:
    - Region
    - Country
    - Year
    """
    if config.region:
        df = df[df["Region"] == config.region]

    if config.country:
        df = df[df["Country Name"] == config.country]

    if config.year:
        df = df[df["Year"] == config.year]

    return df
