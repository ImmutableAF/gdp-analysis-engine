import pandas as pd
from typing import Tuple, List


def convert_years_to_numeric(df: pd.DataFrame, start_year: int = 1960, end_year: int = 2024) -> pd.DataFrame:
    """
    Convert year columns to numeric values. Non-convertible values become NaN.
    """
    df = df.copy()
    year_cols = [str(y) for y in range(start_year, end_year + 1) if str(y) in df.columns]
    df[year_cols] = df[year_cols].apply(pd.to_numeric, errors='coerce')
    return df


def fill_missing_years(df: pd.DataFrame, method: str = "ffill", start_year: int = 1960, end_year: int = 2024) -> pd.DataFrame:
    """
    Fill missing values in year columns.
    method: 'ffill', 'bfill', 'zero'
    """
    df = df.copy()
    year_cols = [str(y) for y in range(start_year, end_year + 1) if str(y) in df.columns]
    
    if method == "zero":
        df[year_cols] = df[year_cols].fillna(0)
    elif method in ["ffill", "bfill"]:
        df[year_cols] = df[year_cols].fillna(method=method, axis=1)
    
    return df


def remove_invalid_values(df: pd.DataFrame, start_year: int = 1960, end_year: int = 2024) -> pd.DataFrame:
    """
    Remove invalid data. For GDP, negative values are invalid.
    Sets them to NaN.
    """
    df = df.copy()
    year_cols = [str(y) for y in range(start_year, end_year + 1) if str(y) in df.columns]
    df[year_cols] = df[year_cols].applymap(lambda x: x if pd.isna(x) or x >= 0 else None)
    return df


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop duplicate rows based on Country Name + Indicator Code.
    """
    return df.drop_duplicates(subset=["Country Name", "Indicator Code"])


def clean_gdp_data(df: pd.DataFrame, fill_method: str = "ffill") -> pd.DataFrame:
    """
    Full cleaning pipeline for GDP dataset.
    """
    df = convert_years_to_numeric(df)
    df = fill_missing_years(df, method=fill_method)
    df = remove_invalid_values(df)
    df = drop_duplicates(df)
    return df
