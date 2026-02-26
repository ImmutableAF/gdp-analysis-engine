"""
Purpose:
Extracts available filter options from a cleaned DataFrame for use in the API or UI.

Functions
---------
extract_column(df, column)
    Safely extract a column, returning an empty Series if the column does not exist.
normalize_strings(series)
    Deduplicate and title-case a string Series into a plain list.
get_all_regions(df)
    Return all unique continent names present in the DataFrame.
get_all_countries(df)
    Return all unique country names present in the DataFrame.
get_year_range(df)
    Return the (min, max) year tuple found in the DataFrame.
get_valid_attr(df)
    Return regions and year range together as a single tuple.
get_metadata(df)
    Return all filter options bundled in a dictionary.

Notes
-----
- If a column is missing, extract_column() returns an empty Series rather than raising.
- If no valid years exist, get_year_range() falls back to DEFAULT_YEAR_RANGE (1960–2024).
"""

from typing import List, Tuple
import pandas as pd


DEFAULT_YEAR_RANGE: Tuple[int, int] = (1960, 2024)


def extract_column(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Safely extract a column from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    column : str
        Column name to extract.

    Returns
    -------
    pd.Series
        The column if it exists, otherwise an empty Series.
    """
    return df[column] if column in df.columns else pd.Series(dtype=object)


def normalize_strings(series: pd.Series) -> List[str]:
    """
    Deduplicate and title-case a string Series.

    Parameters
    ----------
    series : pd.Series
        Raw string values, may contain NaN.

    Returns
    -------
    List[str]
        Unique, title-cased strings with NaN removed.
    """
    return series.dropna().astype(str).str.title().unique().tolist()


def get_all_regions(df: pd.DataFrame) -> List[str]:
    """
    Return all unique continent names in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with a "Continent" column.

    Returns
    -------
    List[str]
        Unique continent names, title-cased.
    """
    return normalize_strings(extract_column(df, "Continent"))


def get_all_countries(df: pd.DataFrame) -> List[str]:
    """
    Return all unique country names in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with a "Country Name" column.

    Returns
    -------
    List[str]
        Unique country names, title-cased.
    """
    return normalize_strings(extract_column(df, "Country Name"))


def get_year_range(df: pd.DataFrame) -> Tuple[int, int]:
    """
    Return the minimum and maximum years present in the DataFrame.

    Falls back to DEFAULT_YEAR_RANGE (1960, 2024) if the "Year" column
    is missing or contains no valid numeric values.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with a "Year" column.

    Returns
    -------
    Tuple[int, int]
        (min_year, max_year) drawn from the data, or (1960, 2024) as fallback.
    """
    years = extract_column(df, "Year").pipe(pd.to_numeric, errors="coerce").dropna()

    if years.empty:
        return DEFAULT_YEAR_RANGE

    return int(years.min()), int(years.max())


def get_valid_attr(df: pd.DataFrame) -> Tuple[List[str], Tuple[int, int]]:
    """
    Return regions and year range together.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame.

    Returns
    -------
    Tuple[List[str], Tuple[int, int]]
        (regions, (min_year, max_year))
    """
    return (get_all_regions(df), get_year_range(df))


def get_metadata(df: pd.DataFrame) -> dict:
    """
    Bundle all available filter options into a single dictionary.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame.

    Returns
    -------
    dict
        Keys: "regions" (sorted list), "countries" (sorted list),
        "year_range" (min, max tuple).
    """
    return {
        "regions": sorted(get_all_regions(df)),
        "countries": sorted(get_all_countries(df)),
        "year_range": get_year_range(df),
    }