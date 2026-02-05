from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass(frozen=True)
class QueryConfig:
    region: str
    country: str
    startYear: int
    endYear: Optional[int] = None

class WBFrame:
    def __init__(self, csv_path: str):
        df = pd.read_csv(csv_path)

        # Convert wide year columns -> long format
        self.df = df.melt(
            id_vars=[
                "Country Name",
                "Country Code",
                "Indicator Name",
                "Indicator Code",
                "Continent",
            ],
            var_name="Year",
            value_name="Value",
        )

        # Clean types
        self.df["Year"] = self.df["Year"].astype(int)

    def filter_by_region(self, region: str):
        self.df = self.df[self.df["Continent"] == region]
        return self

    def filter_by_year(self, start_year: int, end_year: int | None = None):
        """
        filter_by_year(2010) -> only 2010
        filter_by_year(2000, 2010) -> inclusive range
        """
        if end_year is None:
            self.df = self.df[self.df["Year"] == start_year]
        else:
            self.df = self.df[
                (self.df["Year"] >= start_year) &
                (self.df["Year"] <= end_year)
            ]
        return self

    def filter_by_country(self, country: str):
        self.df = self.df[self.df["Country Name"] == country]
        return self

    def drop_na(self):
        self.df = self.df.dropna(subset=["Value"])
        return self

    def result(self) -> pd.DataFrame:
        return self.df


if __name__ == "__main__":
    # --- CONFIG ---
    query_config = QueryConfig(
        region="Asia",
        country="Pakistan",
        startYear=2010,
        endYear=2013,  # set to None for single-year behavior
    )
    
    # Single year
    single_year = (
        WBFrame("data/gdp_with_continent_filled.csv")
            .filter_by_region(query_config.region)
            .filter_by_year(query_config.startYear)
            .filter_by_country(query_config.country)
            .drop_na()
            .result()
    )

    print("Single year:")
    print(single_year)  

    # Year range
    year_range = (
        WBFrame("data/gdp_with_continent_filled.csv")
            .filter_by_region(query_config.region)
            .filter_by_year(query_config.startYear, query_config.endYear)
            .filter_by_country(query_config.country)
            .drop_na()
            .result()
    )

    print("\nYear range:")
    print(year_range)
