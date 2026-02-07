from dataclasses import dataclass
from typing import Optional, Union
import pandas as pd
from pathlib import Path
from src.core.config_manager.config_models import QueryConfig

def transform(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.melt(
            id_vars=["Country Name", "Continent", "Indicator Name", "Indicator Code", "Country Code"],
            var_name="Year",
            value_name="Value"
        ).assign(Year=lambda x: x["Year"].astype(int))
    )

def filter_by_region(df: pd.DataFrame, region: str | None):
    return df[df["Continent"].str.lower() == region.lower()] if region is not None else df

def filter_by_country(df: pd.DataFrame, country: str | None):
    return df[df["Country Name"].str.lower() == country.lower()] if country is not None else df

def filter_by_year(df: pd.DataFrame, start: int | None = None, end: int | None = None):
    if start is None and end is None:
        return df
    elif end is None:
        return df[df["Year"] == start]
    elif start is None:
        return df[df["Year"] == end]

    return df[df["Year"].between(start, end)]

def aggregate(df: pd.DataFrame, operation: str | None):
    if operation is None:
        return df
    
    operation = operation.lower()
    group_cols = ["Country Name", "Country Code", "Indicator Name", "Indicator Code", "Continent"]
    
    if operation == "sum":
        return (df
        .groupby(group_cols, as_index=False)["Value"]
        .sum()
        .assign(Operation="Sum"))

    elif operation in ["avg", "average"]:
        return (df
            .groupby(group_cols, as_index=False)["Value"]
            .mean()
            .assign(Operation="Average"))
    
    return df

def aggregate_by_region(df: pd.DataFrame, op: str) -> pd.DataFrame:
    if op == "sum":
        return df.groupby("Continent", as_index=False)["Value"].sum()
    return df.groupby("Continent", as_index=False)["Value"].mean()


def aggregate_by_country(df: pd.DataFrame, op: str) -> pd.DataFrame:
    if op == "sum":
        return df.groupby("Country Name", as_index=False)["Value"].sum()
    return df.groupby("Country Name", as_index=False)["Value"].mean()

def run_pipeline(df: pd.DataFrame, query_config: QueryConfig):
    result = (
        df.pipe(transform)
        .pipe(filter_by_region, query_config.region)
        .pipe(filter_by_country, query_config.country)
        .pipe(filter_by_year, query_config.startYear, query_config.endYear)
        .dropna(subset=["Value"])
        .pipe(aggregate, query_config.operation)
    )

    print(result)