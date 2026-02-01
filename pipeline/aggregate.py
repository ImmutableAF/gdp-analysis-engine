# pipeline/aggregate.py
import pandas as pd
from config_models import QueryConfig


def aggregate_data(df: pd.DataFrame, config: QueryConfig) -> pd.DataFrame:
    """
    Aggregates filtered data based on query_config.operation:
    - 'sum' → sum of GDP values per Region
    - 'average' → mean of GDP values per Region
    """
    if df.empty:
        return df

    # Ignore rows with missing Value
    df = df.dropna(subset=["Value"])

    if config.operation.lower() == "average":
        result = df.groupby("Region", as_index=False)["Value"].mean()
        result.rename(columns={"Value": "Average GDP"}, inplace=True)
    elif config.operation.lower() == "sum":
        result = df.groupby("Region", as_index=False)["Value"].sum()
        result.rename(columns={"Value": "Total GDP"}, inplace=True)
    else:
        raise ValueError(f"Unsupported operation: {config.operation}")

    return result
