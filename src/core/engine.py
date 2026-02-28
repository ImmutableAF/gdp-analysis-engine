"""
Purpose:
Core query engine — transforms, filters, and aggregates GDP data based on user-defined parameters.

Description:
Operates on the wide-format raw DataFrame produced by the data loader and converts it into
a long format suitable for filtering and aggregation. All filtering and aggregation logic
lives here and is driven by a Filters config object. This module is the main computational
layer between raw data and query results.

Pipeline Flow:
Wide DataFrame → transform() → Long DataFrame → apply_filters() → Filtered DataFrame → aggregate_all() → Result

Functions
---------
transform(df)
    Reshape wide-format DataFrame (one column per year) into long format (one row per year).
_filter_by_region(df, region)
    Internal — filter rows to a specific continent (case-insensitive).
_filter_by_country(df, country)
    Internal — filter rows to a specific country (case-insensitive).
_filter_by_year(df, start, end)
    Internal — filter rows to a year or year range.
aggregate_by_region(df, operation)
    Aggregate values grouped by continent.
aggregate_by_country(df, operation)
    Aggregate values grouped by country name.
aggregate_by_country_code(df, operation)
    Aggregate values grouped by country code.
aggregate_all(df, operation)
    Aggregate values while preserving all identifier columns.
apply_filters(df, region, country, start_year, end_year)
    Chain all filters in one call and drop rows with null values.
get_query_result(df, filters)
    Run the full pipeline and print the result.
run_pipeline(df, filters, inLongFormat)
    Run the full pipeline and return the result, optionally skipping aggregation.

See Also
--------
contracts.Filters : Filter parameter model passed to get_query_result and run_pipeline.

Notes
-----
- All public functions return copies — originals are never modified.
- Internal helpers prefixed with _ are not intended to be called directly.
- Filters are case-insensitive on string columns.
- Passing None to any filter parameter skips that filter and returns a full copy.
- Unrecognized operation strings in aggregate_all() return the DataFrame unchanged.
- apply_filters() always drops rows where Value is NaN regardless of filter inputs.

Examples
--------
>>> # Step-by-step
>>> long_df  = transform(wide_df)
>>> filtered = apply_filters(long_df, region="Asia", start_year=2000, end_year=2020)
>>> result   = aggregate_all(filtered, "sum")

>>> # All-in-one
>>> filters = Filters(region="Asia", startYear=2000, endYear=2020, operation="sum")
>>> result  = run_pipeline(wide_df, filters)

>>> # Long format (skip aggregation)
>>> result = run_pipeline(wide_df, filters, inLongFormat=True)
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)
from .contracts import Filters


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reshape wide-format DataFrame into long format. This is
    required before any filtering or aggregation can be performed.

    Parameters
    ----------
    df : pd.DataFrame
        Wide-format input with columns: "Country Name", "Continent",
        "Indicator Name", "Indicator Code", "Country Code", and one column
        per year (e.g. "1960", "1961", ..., "2024").

    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with all original id columns plus "Year" (int)
        and "Value" (float) columns.

    Examples
    --------
    >>> long_df = transform(wide_df)
    """
    return df.melt(
        id_vars=[
            "Country Name",
            "Continent",
            "Indicator Name",
            "Indicator Code",
            "Country Code",
        ],
        var_name="Year",
        value_name="Value",
    ).assign(Year=lambda x: x["Year"].astype(int))


def _filter_by_region(df: pd.DataFrame, region: str | None) -> pd.DataFrame:
    """
    Filter rows to a specific continent (case-insensitive).

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with a "Continent" column.
    region : str or None
        Continent name to keep. None returns a full copy with no filtering.

    Returns
    -------
    pd.DataFrame
        Filtered copy.
    """
    logger.debug(f"Filtering by region: {region}, input shape: {df.shape}")
    if region is None:
        logger.debug("No region provided, skipping region filter")
        return df.copy()
    result = df[df["Continent"].str.lower() == region.lower()].copy()
    logger.debug(f"Region filter applied. Resulting shape: {result.shape}")
    return result


def _filter_by_country(df: pd.DataFrame, country: str | None) -> pd.DataFrame:
    """
    Filter rows to a specific country (case-insensitive).

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with a "Country Name" column.
    country : str or None
        Country name to keep. None returns a full copy with no filtering.

    Returns
    -------
    pd.DataFrame
        Filtered copy.
    """
    logger.debug(f"Filtering by country: {country}, input shape: {df.shape}")
    if country is None:
        logger.debug("No country provided, skipping country filter")
        return df.copy()
    result = df[df["Country Name"].str.lower() == country.lower()].copy()
    logger.debug(f"Country filter applied. Resulting shape: {result.shape}")
    return result


def _filter_by_year(
    df: pd.DataFrame, start: int | None = None, end: int | None = None
) -> pd.DataFrame:
    """
    Filter rows to a specific year or inclusive year range.

    Behavior depends on which arguments are provided:
    - Both start and end → keep rows where Year is between start and end (inclusive).
    - Only start → keep rows where Year equals start exactly.
    - Only end → keep rows where Year equals end exactly.
    - Neither → return a full copy with no filtering.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with a "Year" column (int).
    start : int or None
        Lower bound year (inclusive). When end is None, treated as an exact match.
    end : int or None
        Upper bound year (inclusive). When start is None, treated as an exact match.

    Returns
    -------
    pd.DataFrame
        Filtered copy.
    """
    logger.debug(f"Filtering by year: start={start}, end={end}, input shape={df.shape}")
    if start is None and end is None:
        logger.debug("No year range provided, skipping year filter")
        return df.copy()

    if end is None:
        result = df[df["Year"] == start].copy()
        logger.debug(f"Filtered by start year={start}, resulting shape={result.shape}")
        return result

    if start is None:
        result = df[df["Year"] == end].copy()
        logger.debug(f"Filtered by end year={end}, resulting shape={result.shape}")
        return result

    result = df[df["Year"].between(start, end)].copy()
    logger.debug(
        f"Filtered by year range {start}-{end}, resulting shape={result.shape}"
    )
    return result


def aggregate_by_region(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """
    Aggregate values grouped by continent.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with "Continent" and "Value" columns.
    operation : str
        "sum" for total. Any other value computes mean.

    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame with "Continent" and "Value" columns.
    """
    if operation == "sum":
        return df.groupby("Continent", as_index=False)["Value"].sum()
    return df.groupby("Continent", as_index=False)["Value"].mean()


def aggregate_by_country(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """
    Aggregate values grouped by country name.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with "Country Name" and "Value" columns.
    operation : str
        "sum" for total. Any other value computes mean.

    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame with "Country Name" and "Value" columns.
    """
    if operation == "sum":
        return df.groupby("Country Name", as_index=False)["Value"].sum()
    return df.groupby("Country Name", as_index=False)["Value"].mean()


def aggregate_by_country_code(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """
    Aggregate values grouped by country code.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with "Country Code" and "Value" columns.
    operation : str
        "sum" for total. Any other value computes mean.

    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame with "Country Code" and "Value" columns.
    """
    if operation == "sum":
        return df.groupby("Country Code", as_index=False)["Value"].sum()
    return df.groupby("Country Code", as_index=False)["Value"].mean()


def aggregate_all(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """
    Groups by all non-value columns and computes the requested aggregate
    across years.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame with all identifier columns and "Value".
    operation : str or None
        "sum" to total values. "avg" or "average" to
        average them. None defaults to "avg". Any other string returns
        the DataFrame unchanged.

    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame with an "Operation" column added ("Sum" or "Average").
        Returns full copy unchanged for unrecognized operation strings.

    Examples
    --------
    >>> result = aggregate_all(df, "sum")
    >>> print(result["Operation"].iloc[0])
    Sum
    """
    if operation is None:
        operation = "avg"
    operation = operation.lower()
    group_cols = [
        "Country Name",
        "Country Code",
        "Indicator Name",
        "Indicator Code",
        "Continent",
    ]

    logger.debug(f"Aggregating all: operation={operation}, input shape={df.shape}")

    if operation == "sum":
        result = (
            df.groupby(group_cols, as_index=False)["Value"]
            .sum()
            .assign(Operation="Sum")
        )

    elif operation in ["avg", "average"]:
        result = (
            df.groupby(group_cols, as_index=False)["Value"]
            .mean()
            .assign(Operation="Average")
        )

    else:
        result = df.copy()
        logger.debug("Unknown operation, returning original DataFrame")

    logger.debug(f"Aggregation complete, resulting shape={result.shape}")
    return result


def apply_filters(
    df: pd.DataFrame,
    region: str | None = None,
    country: str | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
) -> pd.DataFrame:
    """
    Apply all filters in sequence and drop rows with missing values.

    Chains filters in order: region → country → year → drop NaN values.
    Each step that receives None for its argument is skipped entirely.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format DataFrame (run transform() first).
    region : str or None
        Continent to filter on. None skips this filter.
    country : str or None
        Country name to filter on. None skips this filter.
    start_year : int or None
        Year range lower bound. None skips the year filter unless end_year is set.
    end_year : int or None
        Year range upper bound. None skips the year filter unless start_year is set.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame with rows where Value is NaN removed.

    Examples
    --------
    >>> filtered = apply_filters(df, region="Asia", start_year=2000, end_year=2020)
    """
    logger.info(
        f"Applying filters: region={region}, country={country}, years={start_year}-{end_year}"
    )
    result = df.copy()

    if region is not None:
        result = _filter_by_region(result, region)

    if country is not None:
        result = _filter_by_country(result, country)

    if start_year is not None or end_year is not None:
        result = _filter_by_year(result, start_year, end_year)

    result = result.dropna(subset=["Value"])
    logger.debug(f"Filters applied, resulting shape={result.shape}")
    return result


def get_query_result(df: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    """
    Run the full pipeline and print the result to stdout.

    Convenience function for interactive inspection. Executes the complete
    pipeline — transform, filter, drop nulls, aggregate — and prints the
    resulting DataFrame instead of returning it.

    Parameters
    ----------
    df : pd.DataFrame
        Raw wide-format DataFrame.
    filters : Filters
        Config object with fields: region, country, startYear, endYear, operation.

    Examples
    --------
    >>> filters = Filters(region="Asia", startYear=2000, endYear=2020, operation="sum")
    >>> get_query_result(raw_df, filters)
    """
    result = (
        df.pipe(transform)
        .pipe(_filter_by_region, filters.region)
        .pipe(_filter_by_country, filters.country)
        .pipe(_filter_by_year, filters.startYear, filters.endYear)
        .dropna(subset=["Value"])
        .pipe(aggregate_all, filters.operation)
    )

    print(result)


def run_pipeline(
    df: pd.DataFrame, filters: Filters, inLongFormat: bool = False
) -> pd.DataFrame:
    """
    Run the full pipeline and return the result.

    Executes transform → filter → drop nulls → aggregate in sequence.
    When inLongFormat is True, aggregation is skipped and the filtered
    long-format DataFrame is returned as-is.

    Parameters
    ----------
    df : pd.DataFrame
        Raw wide-format DataFrame.
    filters : Filters
        Config object with fields: region, country, startYear, endYear, operation.
    inLongFormat : bool
        If True, skip aggregation and return the filtered long-format DataFrame.
        Default is False.

    Returns
    -------
    pd.DataFrame
        Aggregated result by default, or filtered long-format DataFrame if
        inLongFormat is True.

    Examples
    --------
    >>> filters = Filters(region="Asia", startYear=2000, endYear=2020, operation="sum")
    >>> result = run_pipeline(raw_df, filters)
    >>> long_df = run_pipeline(raw_df, filters, inLongFormat=True)
    """
    return (
        df.pipe(transform)
        .pipe(_filter_by_region, filters.region)
        .pipe(_filter_by_country, filters.country)
        .pipe(_filter_by_year, filters.startYear, filters.endYear)
        .dropna(subset=["Value"])
        .pipe(lambda d: d if inLongFormat else aggregate_all(d, filters.operation))
    )