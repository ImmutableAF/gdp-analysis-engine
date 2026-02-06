from dataclasses import dataclass
from typing import Optional, Union
import pandas as pd
from pathlib import Path

from src.core.config_manager.config_models import QueryConfig
from src.core.config_manager.config_loader import load_query_config
from src.core.config_manager.config_handler import sanatize_query_config

class WBFrame:
    def __init__(self, source: Union[str, pd.DataFrame]):
        # Polymorphic init: Handles both initial CSV load and intermediate DataFrame wrapping
        if isinstance(source, str):
            self._df = self._ingest(source)
        else:
            self._df = source

    def _ingest(self, csv_path: str) -> pd.DataFrame:
        """Private pure helper for initial data loading."""
        return (
            pd.read_csv(csv_path)
            .melt(
                id_vars=[
                    "Country Name", "Country Code", "Indicator Name", 
                    "Indicator Code", "Continent"
                ],
                var_name="Year",
                value_name="Value",
            )
            .assign(Year=lambda x: x["Year"].astype(int))
        )

    def filter_by_region(self, region: str | None) -> 'WBFrame':
        if region is None:
            return self
        return WBFrame(self._df[self._df["Continent"] == region])

    def filter_by_year(self, start: int | None, end: int | None = None) -> 'WBFrame':
        if start is None:
            return self
            
        if end is None:
            new_df = self._df[self._df["Year"] == start]
        else:
            new_df = self._df[self._df["Year"].between(start, end)]
            
        return WBFrame(new_df)

    def filter_by_country(self, country: str | None) -> 'WBFrame':
        if country is None:
            return self
        return WBFrame(self._df[self._df["Country Name"] == country])

    def drop_na(self) -> 'WBFrame':
        return WBFrame(self._df.dropna(subset=["Value"]))

    def aggregate(self, operation: str | None) -> 'WBFrame':
        if operation is None:
            return self
        
        op = operation.lower()
        group_cols = ["Country Name", "Country Code", "Indicator Name", "Indicator Code", "Continent"]
        
        if op == "sum":
            new_df = self._df.groupby(group_cols, as_index=False)["Value"].sum().assign(Operation="sum")
            return WBFrame(new_df)
        elif op in ["avg", "average"]:
            new_df = self._df.groupby(group_cols, as_index=False)["Value"].mean().assign(Operation="avg")
            return WBFrame(new_df)
        
        print(f"Warning: Unknown operation '{op}', skipping aggregation")
        return self

    def result(self) -> pd.DataFrame:
        return self._df

# --- CONFIG & EXECUTION ---

csv_path = "data/gdp_with_continent_filled.csv"

# Metadata loading (Purely for config sanitization)
temp_df = pd.read_csv(csv_path)
regions = temp_df["Continent"].unique().tolist()
countries = temp_df["Country Name"].unique().tolist()
years = sorted([int(c) for c in temp_df.columns if c.isdigit()])
year_range = (min(years), max(years))

query_config_path = Path(__file__).resolve().parent / "data" / "configs" / "query_config.json"
query_config = load_query_config(query_config_path)
query_config = sanatize_query_config(query_config, regions, countries, year_range)

print(f"\nActive filters:")
print(f"  Region: {query_config.region or 'ALL'}")
print(f"  Country: {query_config.country or 'ALL'}")
print(f"  Start Year: {query_config.startYear or 'ALL'}")
print(f"  End Year: {query_config.endYear or 'ALL'}")
print(f"  Operation: {query_config.operation or 'NONE'}\n")

# Pipeline 1: Single Year
single_year = (
    WBFrame(csv_path)
        .filter_by_region(query_config.region)
        .filter_by_year(query_config.startYear)
        .filter_by_country(query_config.country)
        .drop_na()
        .aggregate(query_config.operation)
        .result()
)

print("Single year:")
print(single_year)  

# Pipeline 2: Year Range
year_range_result = (
    WBFrame(csv_path)
        .filter_by_region(query_config.region)
        .filter_by_year(query_config.startYear, query_config.endYear)
        .filter_by_country(query_config.country)
        .drop_na()
        .aggregate(query_config.operation)
        .result()
)

print("\nYear range:")
print(year_range_result)