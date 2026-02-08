"""
Data pipeline operations
All functions are pure - no side effects
"""

import pandas as pd
from src.core.config_manager.config_models import QueryConfig


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Transform wide-format GDP data to long format"""
    return df.melt(
        id_vars=["Country Name", "Continent", "Indicator Name", "Indicator Code", "Country Code"],
        var_name="Year",
        value_name="Value"
    ).assign(Year=lambda x: x["Year"].astype(int))


def filter_by_region(df: pd.DataFrame, region: str | None) -> pd.DataFrame:
    """Filter dataframe by region"""
    if region is None:
        return df.copy()
    return df[df["Continent"].str.lower() == region.lower()].copy()


def filter_by_country(df: pd.DataFrame, country: str | None) -> pd.DataFrame:
    """Filter dataframe by country"""
    if country is None:
        return df.copy()
    return df[df["Country Name"].str.lower() == country.lower()].copy()


def filter_by_year(df: pd.DataFrame, start: int | None = None, end: int | None = None) -> pd.DataFrame:
    """Filter dataframe by year range"""
    if start is None and end is None:
        return df.copy()
    
    if end is None:
        return df[df["Year"] == start].copy()
    
    if start is None:
        return df[df["Year"] == end].copy()

    return df[df["Year"].between(start, end)].copy()


def aggregate_by_region(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """Aggregate values by region"""
    if operation == "sum":
        return df.groupby("Continent", as_index=False)["Value"].sum()
    return df.groupby("Continent", as_index=False)["Value"].mean()


def aggregate_by_country(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """Aggregate values by country"""
    if operation == "sum":
        return df.groupby("Country Name", as_index=False)["Value"].sum()
    return df.groupby("Country Name", as_index=False)["Value"].mean()

def aggregate_by_country_code(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """Aggregate values by country code"""
    if operation == "sum":
        return df.groupby("Country Code", as_index=False)["Value"].sum()
    return df.groupby("Country Code", as_index=False)["Value"].mean()


def aggregate_all(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """Aggregate all values with grouping by core dimensions"""
    operation = operation.lower()
    group_cols = ["Country Name", "Country Code", "Indicator Name", "Indicator Code", "Continent"]
    
    if operation == "sum":
        return (
            df.groupby(group_cols, as_index=False)["Value"]
            .sum()
            .assign(Operation="Sum")
        )
    
    if operation in ["avg", "average"]:
        return (
            df.groupby(group_cols, as_index=False)["Value"]
            .mean()
            .assign(Operation="Average")
        )
    
    return df.copy()


def apply_filters(
    df: pd.DataFrame,
    region: str | None = None,
    country: str | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
) -> pd.DataFrame:
    """Apply multiple filters in sequence - returns new dataframe"""
    result = df.copy()
    
    if region is not None:
        result = filter_by_region(result, region)
    
    if country is not None:
        result = filter_by_country(result, country)
    
    if start_year is not None or end_year is not None:
        result = filter_by_year(result, start_year, end_year)
    
    return result.dropna(subset=["Value"])


def run_pipeline(df: pd.DataFrame, query_config: QueryConfig):
    """Execute full pipeline with query config"""
    result = (
        df.pipe(transform)
        .pipe(filter_by_region, query_config.region)
        .pipe(filter_by_country, query_config.country)
        .pipe(filter_by_year, query_config.startYear, query_config.endYear)
        .dropna(subset=["Value"])
        .pipe(aggregate_all, query_config.operation)
    )

    print(result)