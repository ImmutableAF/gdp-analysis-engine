"""
Data Pipeline Operations
=========================

Pure functional transformations for GDP data processing. All functions are
side-effect free and return new DataFrames.

Pipeline Flow:
Wide Format → transform() → Long Format → filter_*() → aggregate_*() → Output

Functions
---------
transform(df)
    Convert wide format to long format
filter_by_region(df, region)
    Filter by continent/region
filter_by_country(df, country)
    Filter by country name
filter_by_year(df, start, end)
    Filter by year range
aggregate_by_region(df, operation)
    Aggregate values by region
aggregate_by_country(df, operation)
    Aggregate values by country
aggregate_by_country_code(df, operation)
    Aggregate values by country code
aggregate_all(df, operation)
    Aggregate with all dimensions preserved
apply_filters(df, **kwargs)
    Chain multiple filters
run_pipeline(df, query_config)
    Execute complete transformation pipeline

See Also
--------
config_manager.QueryConfig : Query parameter configuration

Notes
-----
All functions return copies - original DataFrames never modified. Filters
return full copies even when no filtering occurs (via .copy()).

Examples
--------
>>> wide_df = pd.DataFrame({"Country Name": ["USA"], "2020": [100], "2021": [110]})
>>> long_df = transform(wide_df)
>>> filtered = filter_by_year(long_df, 2020, 2021)
>>> aggregated = aggregate_by_country(filtered, "sum")
"""

import pandas as pd
from src.core.config_manager.config_models import QueryConfig


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform wide-format GDP data to long format.
    
    Converts year columns (e.g., "1960", "1961") to rows with Year and Value
    columns. Preserves all identifier columns.
    
    Parameters
    ----------
    df : pd.DataFrame
        Wide format with year columns as strings
    
    Returns
    -------
    pd.DataFrame
        Long format with Year (int) and Value columns
    
    Notes
    -----
    Expected wide format:
    - ID columns: Country Name, Continent, Indicator Name, Indicator Code, Country Code
    - Year columns: "1960", "1961", ..., "2020" (as strings)
    
    Output format:
    - All ID columns preserved
    - Year column (integer)
    - Value column (GDP values)
    
    Examples
    --------
    >>> wide = pd.DataFrame({
    ...     "Country Name": ["USA"],
    ...     "Continent": ["North America"],
    ...     "2020": [100],
    ...     "2021": [110]
    ... })
    >>> long = transform(wide)
    >>> print(long.columns)
    Index(['Country Name', 'Continent', 'Year', 'Value'])
    """
    return df.melt(
        id_vars=["Country Name", "Continent", "Indicator Name", "Indicator Code", "Country Code"],
        var_name="Year",
        value_name="Value"
    ).assign(Year=lambda x: x["Year"].astype(int))


def filter_by_region(df: pd.DataFrame, region: str | None) -> pd.DataFrame:
    """
    Filter DataFrame by region (case-insensitive).
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Continent" column
    region : str or None
        Region name to filter, None returns full copy
    
    Returns
    -------
    pd.DataFrame
        Filtered DataFrame copy
    
    Examples
    --------
    >>> df = pd.DataFrame({"Continent": ["Asia", "Europe"], "Value": [100, 200]})
    >>> filter_by_region(df, "asia")
    """
    if region is None:
        return df.copy()
    return df[df["Continent"].str.lower() == region.lower()].copy()


def filter_by_country(df: pd.DataFrame, country: str | None) -> pd.DataFrame:
    """
    Filter DataFrame by country name (case-insensitive).
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Country Name" column
    country : str or None
        Country name to filter, None returns full copy
    
    Returns
    -------
    pd.DataFrame
        Filtered DataFrame copy
    
    Examples
    --------
    >>> df = pd.DataFrame({"Country Name": ["USA", "Canada"], "Value": [100, 200]})
    >>> filter_by_country(df, "usa")
    """
    if country is None:
        return df.copy()
    return df[df["Country Name"].str.lower() == country.lower()].copy()


def filter_by_year(df: pd.DataFrame, start: int | None = None, end: int | None = None) -> pd.DataFrame:
    """
    Filter DataFrame by year range.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Year" column
    start : int or None
        Start year (inclusive), None for no lower bound
    end : int or None
        End year (inclusive), None for no upper bound
    
    Returns
    -------
    pd.DataFrame
        Filtered DataFrame copy
    
    Notes
    -----
    Behavior:
    - Both None: Return full copy
    - Only start: Filter to exact year match
    - Only end: Filter to exact year match
    - Both specified: Filter to range [start, end]
    
    Examples
    --------
    >>> df = pd.DataFrame({"Year": [2000, 2010, 2020], "Value": [1, 2, 3]})
    >>> filter_by_year(df, 2000, 2010)
    """
    if start is None and end is None:
        return df.copy()
    
    if end is None:
        return df[df["Year"] == start].copy()
    
    if start is None:
        return df[df["Year"] == end].copy()

    return df[df["Year"].between(start, end)].copy()


def aggregate_by_region(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """
    Aggregate GDP values by region.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Continent" and "Value" columns
    operation : str
        "sum" for total, any other value for mean
    
    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame with Continent and Value columns
    
    Examples
    --------
    >>> df = pd.DataFrame({"Continent": ["Asia", "Asia"], "Value": [100, 200]})
    >>> aggregate_by_region(df, "sum")
    """
    if operation == "sum":
        return df.groupby("Continent", as_index=False)["Value"].sum()
    return df.groupby("Continent", as_index=False)["Value"].mean()


def aggregate_by_country(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """
    Aggregate GDP values by country name.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Country Name" and "Value" columns
    operation : str
        "sum" for total, any other value for mean
    
    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame with Country Name and Value columns
    
    Examples
    --------
    >>> df = pd.DataFrame({"Country Name": ["USA", "USA"], "Value": [100, 200]})
    >>> aggregate_by_country(df, "sum")
    """
    if operation == "sum":
        return df.groupby("Country Name", as_index=False)["Value"].sum()
    return df.groupby("Country Name", as_index=False)["Value"].mean()


def aggregate_by_country_code(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """
    Aggregate GDP values by country code.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with "Country Code" and "Value" columns
    operation : str
        "sum" for total, any other value for mean
    
    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame with Country Code and Value columns
    
    Examples
    --------
    >>> df = pd.DataFrame({"Country Code": ["USA", "USA"], "Value": [100, 200]})
    >>> aggregate_by_country_code(df, "sum")
    """
    if operation == "sum":
        return df.groupby("Country Code", as_index=False)["Value"].sum()
    return df.groupby("Country Code", as_index=False)["Value"].mean()


def aggregate_all(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """
    Aggregate values while preserving all core dimensions.
    
    Groups by all identifier columns (Country Name, Country Code, Indicator Name,
    Indicator Code, Continent) and adds Operation column to result.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with core dimension columns and Value
    operation : str
        "sum", "avg", or "average" (case-insensitive)
    
    Returns
    -------
    pd.DataFrame
        Aggregated with Operation column added, or full copy if invalid operation
    
    Notes
    -----
    Invalid operations return full copy without aggregation.
    
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     "Country Name": ["USA", "USA"],
    ...     "Country Code": ["US", "US"],
    ...     "Value": [100, 200]
    ... })
    >>> agg = aggregate_all(df, "sum")
    >>> print(agg["Operation"].iloc[0])
    Sum
    """
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
    """
    Apply multiple filters in sequence.
    
    Chains region, country, and year filters, then drops rows with null Values.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to filter
    region : str or None
        Region filter
    country : str or None
        Country filter
    start_year : int or None
        Start year (inclusive)
    end_year : int or None
        End year (inclusive)
    
    Returns
    -------
    pd.DataFrame
        Filtered DataFrame with null Values removed
    
    Notes
    -----
    Filter application order: region → country → year → drop nulls.
    Each filter creates new DataFrame copy.
    
    Examples
    --------
    >>> df = transform(wide_df)
    >>> filtered = apply_filters(df, region="Asia", start_year=2000, end_year=2020)
    """
    result = df.copy()
    
    if region is not None:
        result = filter_by_region(result, region)
    
    if country is not None:
        result = filter_by_country(result, country)
    
    if start_year is not None or end_year is not None:
        result = filter_by_year(result, start_year, end_year)
    
    return result.dropna(subset=["Value"])


def run_pipeline(df: pd.DataFrame, query_config: QueryConfig):
    """
    Execute complete transformation pipeline with QueryConfig.
    
    Pipeline: transform → filter region → filter country → filter year → 
    drop nulls → aggregate → print
    
    Parameters
    ----------
    df : pd.DataFrame
        Wide-format source DataFrame
    query_config : QueryConfig
        Query parameters (region, country, years, operation)
    
    Notes
    -----
    Uses pandas pipe() for method chaining. Prints result to stdout.
    
    Examples
    --------
    >>> config = QueryConfig(region="Asia", startYear=2000, endYear=2020, operation="sum")
    >>> run_pipeline(wide_df, config)
    """
    result = (
        df.pipe(transform)
        .pipe(filter_by_region, query_config.region)
        .pipe(filter_by_year, query_config.startYear, query_config.endYear)
        .dropna(subset=["Value"])
        .pipe(aggregate_all, query_config.operation)
    )

    print(result)