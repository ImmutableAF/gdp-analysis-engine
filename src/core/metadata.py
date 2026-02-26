from typing import List, Tuple
import pandas as pd


DEFAULT_YEAR_RANGE: Tuple[int, int] = (1960, 2024)


def extract_column(df: pd.DataFrame, column: str) -> pd.Series:
    return df[column] if column in df.columns else pd.Series(dtype=object)


def normalize_strings(series: pd.Series) -> List[str]:
    return series.dropna().astype(str).str.title().unique().tolist()


def get_all_regions(df: pd.DataFrame) -> List[str]:
    return normalize_strings(extract_column(df, "Continent"))


def get_all_countries(df: pd.DataFrame) -> List[str]:
    return normalize_strings(extract_column(df, "Country Name"))


def get_year_range(df: pd.DataFrame) -> Tuple[int, int]:
    years = extract_column(df, "Year").pipe(pd.to_numeric, errors="coerce").dropna()

    if years.empty:
        return DEFAULT_YEAR_RANGE

    return int(years.min()), int(years.max())


def get_valid_attr(df: pd.DataFrame) -> Tuple[List[str], Tuple[int, int]]:
    return (get_all_regions(df), get_year_range(df))


def get_metadata(df: pd.DataFrame) -> dict:
    return {
        "regions": sorted(get_all_regions(df)),
        "countries": sorted(get_all_countries(df)),
        "year_range": get_year_range(df),
    }
