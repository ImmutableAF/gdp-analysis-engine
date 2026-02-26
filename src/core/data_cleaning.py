"""
Purpose:
Cleans and standardizes raw GDP DataFrame before it enters the analysis pipeline.

Description:
This module fixes string-typed year columns, missing or negative values, and duplicate country-indicator 
rows and exposes a single entry-point function, clean_gdp_data(), that runs the full cleaning pipeline in one call.

Pipeline Flow:
Raw DataFrame → convert_years_to_numeric() → fill_missing_years() → remove_invalid_values() → drop_duplicates() → Clean DataFrame

Functions
---------
_year_columns(df, start_year, end_year)
    Internal helper — returns the list of year column names present in the DataFrame.
convert_years_to_numeric(df, start_year, end_year)
    Cast year columns from strings to numbers, turning unparseable entries into NaN.
fill_missing_years(df, method, start_year, end_year)
    Fill NaN cells in year columns using forward-fill, backward-fill, or zero.
remove_invalid_values(df, start_year, end_year)
    Null out any negative numbers in year columns (negative GDP is not meaningful).
drop_duplicates(df)
    Keep only the first row for each unique Country Name + Indicator Code pair.
clean_gdp_data(df, fill_method)
    Run the complete cleaning pipeline and return a clean copy of the DataFrame.

Notes
-----
- All functions return copies — the original DataFrame is never modified.
- Year columns are detected by name (e.g. "1960", "2024"); non-year columns are untouched.
- _year_columns() is an internal helper and is not intended to be called directly.

Examples
--------
>>> # Full pipeline in one call
>>> clean_df = clean_gdp_data(raw_df, fill_method="ffill")

>>> # Step by step
>>> df = convert_years_to_numeric(raw_df)
>>> df = fill_missing_years(df, method="zero")
>>> df = remove_invalid_values(df)
>>> df = drop_duplicates(df)
"""

import pandas as pd
from typing import List


def _year_columns(
    df: pd.DataFrame, start_year: int = 1960, end_year: int = 2024
) -> List[str]:
    """
    Return year column names present in the DataFrame within the given range.
    """
    return [str(y) for y in range(start_year, end_year + 1) if str(y) in df.columns]


def convert_years_to_numeric(
    df: pd.DataFrame, start_year: int = 1960, end_year: int = 2024
) -> pd.DataFrame:
    """
    Cast year columns from strings to numeric values.

    Any cell that cannot be parsed as a number (e.g. "..", "N/A", empty
    strings) is replaced with NaN so downstream functions can handle it
    explicitly rather than silently operating on bad data.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame with year columns stored as strings.
    start_year : int
        First year column to convert. Default is 1960.
    end_year : int
        Last year column to convert. Default is 2024.

    Returns
    -------
    pd.DataFrame
        Copy of df with year columns converted to float64; unparseable
        values become NaN.

    Examples
    --------
    >>> df = convert_years_to_numeric(raw_df)
    """
    year_cols = _year_columns(df, start_year, end_year)
    return df.assign(
        **{col: pd.to_numeric(df[col], errors="coerce") for col in year_cols}
    )


def fill_missing_years(
    df: pd.DataFrame,
    method: str = "ffill",
    start_year: int = 1960,
    end_year: int = 2024,
) -> pd.DataFrame:
    """
    Fill NaN cells in year columns using the specified strategy.

    Three strategies are supported:

    - "ffill"  — propagate the last valid value forward across years (left → right).
    - "bfill"  — propagate the next valid value backward across years (right → left).
    - "zero"   — replace every NaN with 0.

    Any other string leaves year columns unchanged. Filling is applied row-wise,
    meaning each country's own values are used to fill its own gaps.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with numeric year columns (run convert_years_to_numeric first).
    method : str
        Fill strategy: "ffill", "bfill", or "zero". Default is "ffill".
    start_year : int
        First year column to fill. Default is 1960.
    end_year : int
        Last year column to fill. Default is 2024.

    Returns
    -------
    pd.DataFrame
        Copy of df with NaN values in year columns filled according to method.
        Columns outside the year range are not affected.

    Examples
    --------
    >>> df = fill_missing_years(df, method="ffill")
    >>> df = fill_missing_years(df, method="zero")
    """
    year_cols = _year_columns(df, start_year, end_year)

    if method == "zero":
        filled = {col: df[col].fillna(0) for col in year_cols}
    elif method in ["ffill", "bfill"]:
        filled = {
            col: df[year_cols].fillna(method=method, axis=1)[col] for col in year_cols
        }
    else:
        filled = {col: df[col] for col in year_cols}

    return df.assign(**filled)


def remove_invalid_values(
    df: pd.DataFrame, start_year: int = 1960, end_year: int = 2024
) -> pd.DataFrame:
    """
    Replace negative values in year columns with NaN.

    GDP cannot be negative, so any negative number is treated as a data
    error. NaN values are left as-is; only values that are both non-null
    and less than zero are nulled out.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with numeric year columns.
    start_year : int
        First year column to sanitize. Default is 1960.
    end_year : int
        Last year column to sanitize. Default is 2024.

    Returns
    -------
    pd.DataFrame
        Copy of df with negative year values replaced by NaN.

    Examples
    --------
    >>> df = remove_invalid_values(df)
    """
    year_cols = _year_columns(df, start_year, end_year)
    sanitized = {
        col: df[col].map(lambda x: x if pd.isna(x) or x >= 0 else None)
        for col in year_cols
    }
    return df.assign(**sanitized)


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows based on Country Name and Indicator Code.

    When the same country-indicator pair appears more than once, only the
    first occurrence is kept.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Country Name" and "Indicator Code" columns.

    Returns
    -------
    pd.DataFrame
        Copy with duplicate country-indicator rows removed.

    Examples
    --------
    >>> df = drop_duplicates(df)
    """
    return df.drop_duplicates(subset=["Country Name", "Indicator Code"])


def clean_gdp_data(df: pd.DataFrame, fill_method: str = "ffill") -> pd.DataFrame:
    """
    Run the full cleaning pipeline and return a clean DataFrame.

    Executes all four cleaning steps in the correct order:
    convert_years_to_numeric → fill_missing_years → remove_invalid_values → drop_duplicates.

    This is the recommended entry point for cleaning raw GDP data. Use the
    individual step functions only if you need finer control over the process.

    Parameters
    ----------
    df : pd.DataFrame
        Raw GDP DataFrame straight from the data loader.
    fill_method : str
        Strategy for filling missing year values. Passed directly to
        fill_missing_years(). "ffill", "bfill", or "zero". Default is "ffill".

    Returns
    -------
    pd.DataFrame
        Fully cleaned DataFrame ready for transformation and analysis.

    Examples
    --------
    >>> clean_df = clean_gdp_data(raw_df)
    >>> clean_df = clean_gdp_data(raw_df, fill_method="zero")
    """
    return (
        df.pipe(convert_years_to_numeric)
        .pipe(fill_missing_years, method=fill_method)
        .pipe(remove_invalid_values)
        .pipe(drop_duplicates)
    )