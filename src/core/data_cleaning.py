"""
GDP Data Cleaning - Functional Pipeline
=======================================

Pure functional helpers for cleaning GDP datasets. All functions are 
side-effect free and return new DataFrames, preserving original inputs.

Functions
---------
convert_years_to_numeric(df, start_year=1960, end_year=2024)
    Convert year columns to numeric, invalid entries become NaN.
fill_missing_years(df, method='ffill', start_year=1960, end_year=2024)
    Fill missing values in year columns using specified method.
remove_invalid_values(df, start_year=1960, end_year=2024)
    Replace negative GDP values with NaN.
drop_duplicates(df)
    Drop duplicate rows based on Country Name + Indicator Code.
clean_gdp_data(df, fill_method='ffill')
    Full functional pipeline: numeric conversion, filling, sanitization, deduplication.

Notes
-----
- All functions handle missing year columns gracefully.
- String or invalid numeric values are coerced to NaN.
- Functional composition ensures no in-place mutation.

Examples
--------
>>> import pandas as pd
>>> df = pd.DataFrame({
...     "Country Name": ["A", "A", "B"],
...     "Indicator Code": ["GDP", "GDP", "GDP"],
...     "1960": ["100", "100", "-50"],
...     "1961": ["200", None, "30"]
... })
>>> df_clean = clean_gdp_data(df)
>>> df_clean
  Country Name Indicator Code 1960 1961
0            A            GDP 100.0 200.0
2            B            GDP  NaN  30.0
"""

import pandas as pd
from typing import List

# --- Helpers ---
def _year_columns(df: pd.DataFrame, start_year: int = 1960, end_year: int = 2024) -> List[str]:
    """
    Return list of year columns that exist in the DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input GDP DataFrame.
    start_year : int
        Starting year for selection.
    end_year : int
        Ending year for selection.
    
    Returns
    -------
    List[str]
        List of string year column names.
    """
    return [str(y) for y in range(start_year, end_year + 1) if str(y) in df.columns]


# --- Functional transformations ---
def convert_years_to_numeric(df: pd.DataFrame, start_year: int = 1960, end_year: int = 2024) -> pd.DataFrame:
    """
    Convert year columns to numeric values; invalid entries become NaN.
    
    Parameters
    ----------
    df : pd.DataFrame
        GDP dataset with year columns.
    start_year : int
        Starting year for conversion.
    end_year : int
        Ending year for conversion.
    
    Returns
    -------
    pd.DataFrame
        New DataFrame with numeric year columns.
    
    Examples
    --------
    >>> df = pd.DataFrame({"1960": ["100", "abc"]})
    >>> convert_years_to_numeric(df)
       1960
    0  100.0
    1    NaN
    """
    year_cols = _year_columns(df, start_year, end_year)
    return df.assign(**{col: pd.to_numeric(df[col], errors='coerce') for col in year_cols})


def fill_missing_years(df: pd.DataFrame, method: str = "ffill", start_year: int = 1960, end_year: int = 2024) -> pd.DataFrame:
    """
    Fill missing year values using 'ffill', 'bfill', or zero replacement.
    
    Parameters
    ----------
    df : pd.DataFrame
        GDP dataset with numeric year columns.
    method : str
        'ffill', 'bfill', or 'zero'.
    start_year : int
        Start year for filling.
    end_year : int
        End year for filling.
    
    Returns
    -------
    pd.DataFrame
        New DataFrame with missing year values filled.
    
    Examples
    --------
    >>> df = pd.DataFrame({"1960": [100, None]})
    >>> fill_missing_years(df, method="zero")
       1960
    0  100.0
    1    0.0
    """
    year_cols = _year_columns(df, start_year, end_year)

    if method == "zero":
        filled = {col: df[col].fillna(0) for col in year_cols}
    elif method in ["ffill", "bfill"]:
        filled = {col: df[year_cols].fillna(method=method, axis=1)[col] for col in year_cols}
    else:
        filled = {col: df[col] for col in year_cols}

    return df.assign(**filled)


def remove_invalid_values(df: pd.DataFrame, start_year: int = 1960, end_year: int = 2024) -> pd.DataFrame:
    """
    Replace negative GDP values with NaN.
    
    Parameters
    ----------
    df : pd.DataFrame
        GDP dataset with numeric year columns.
    start_year : int
        Start year for sanitization.
    end_year : int
        End year for sanitization.
    
    Returns
    -------
    pd.DataFrame
        New DataFrame with invalid values set to NaN.
    
    Examples
    --------
    >>> df = pd.DataFrame({"1960": [100, -50]})
    >>> remove_invalid_values(df)
       1960
    0  100.0
    1    NaN
    """
    year_cols = _year_columns(df, start_year, end_year)
    sanitized = {col: df[col].map(lambda x: x if pd.isna(x) or x >= 0 else None) for col in year_cols}
    return df.assign(**sanitized)


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop duplicate rows based on Country Name + Indicator Code.
    
    Parameters
    ----------
    df : pd.DataFrame
        GDP dataset.
    
    Returns
    -------
    pd.DataFrame
        DataFrame without duplicates.
    
    Examples
    --------
    >>> df = pd.DataFrame({"Country Name": ["A","A"], "Indicator Code": ["GDP","GDP"]})
    >>> drop_duplicates(df)
      Country Name Indicator Code
    0            A            GDP
    """
    return df.drop_duplicates(subset=["Country Name", "Indicator Code"])


def clean_gdp_data(df: pd.DataFrame, fill_method: str = "ffill") -> pd.DataFrame:
    """
    Full functional cleaning pipeline for GDP dataset.
    
    Steps
    -----
    1. Convert year columns to numeric
    2. Fill missing year values
    3. Remove negative GDP values
    4. Drop duplicate rows
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw GDP dataset.
    fill_method : str
        Method to fill missing values ('ffill', 'bfill', 'zero')
    
    Returns
    -------
    pd.DataFrame
        Cleaned GDP dataset.
    
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     "Country Name": ["A", "A", "B"],
    ...     "Indicator Code": ["GDP", "GDP", "GDP"],
    ...     "1960": ["100", "100", "-50"],
    ...     "1961": ["200", None, "30"]
    ... })
    >>> clean_gdp_data(df)
      Country Name Indicator Code 1960 1961
    0            A            GDP 100.0 200.0
    2            B            GDP  NaN  30.0
    """
    return (
        df
        .pipe(convert_years_to_numeric)
        .pipe(fill_missing_years, method=fill_method)
        .pipe(remove_invalid_values)
        .pipe(drop_duplicates)
    )
