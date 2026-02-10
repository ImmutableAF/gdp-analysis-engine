"""
Data Extraction Helpers
=======================

Pure functions for extracting metadata from GDP DataFrames. All functions
are side-effect free and return new data structures.

Functions
---------
get_all_regions(df)
    Extract unique region/continent names
get_all_countries(df)
    Extract unique country names
get_year_range(df)
    Extract min and max years from data

Notes
-----
All functions handle missing columns and empty data gracefully with sensible
defaults. String values normalized to title case for consistency.

Examples
--------
>>> df = pd.DataFrame({"Continent": ["asia", "EUROPE"], "Year": [2000, 2010]})
>>> get_all_regions(df)
['Asia', 'Europe']
>>> get_year_range(df)
(2000, 2010)
"""

from typing import List, Tuple
import pandas as pd


def get_all_regions(df: pd.DataFrame) -> List[str]:
    """
    Extract unique region names from DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Continent" column
    
    Returns
    -------
    List[str]
        Unique region names in title case, empty list if column missing
    
    Examples
    --------
    >>> df = pd.DataFrame({"Continent": ["asia", "EUROPE", "asia"]})
    >>> get_all_regions(df)
    ['Asia', 'Europe']
    """
    if "Continent" not in df.columns:
        return []
    return df["Continent"].dropna().str.title().unique().tolist()


def get_all_countries(df: pd.DataFrame) -> List[str]:
    """
    Extract unique country names from DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Country Name" column
    
    Returns
    -------
    List[str]
        Unique country names in title case, empty list if column missing
    
    Examples
    --------
    >>> df = pd.DataFrame({"Country Name": ["usa", "CANADA"]})
    >>> get_all_countries(df)
    ['Usa', 'Canada']
    """
    if "Country Name" not in df.columns:
        return []
    return df["Country Name"].dropna().str.title().unique().tolist()


def get_year_range(df: pd.DataFrame) -> Tuple[int, int]:
    """
    Extract minimum and maximum years from DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Year" column (numeric or convertible to numeric)
    
    Returns
    -------
    Tuple[int, int]
        (min_year, max_year), defaults to (1960, 2024) if column missing/empty
    
    Notes
    -----
    Handles non-numeric values via coercion. Returns default range if no valid
    years found.
    
    Examples
    --------
    >>> df = pd.DataFrame({"Year": [2000, 2010, 2005]})
    >>> get_year_range(df)
    (2000, 2010)
    
    >>> empty_df = pd.DataFrame({"Year": []})
    >>> get_year_range(empty_df)
    (1960, 2024)
    """
    if "Year" not in df.columns or df["Year"].empty:
        return (1960, 2024)
    
    years = pd.to_numeric(df["Year"], errors='coerce').dropna()
    if years.empty:
        return (1960, 2024)

    stats = years.agg(['min', 'max'])
    return int(stats['min']), int(stats['max'])