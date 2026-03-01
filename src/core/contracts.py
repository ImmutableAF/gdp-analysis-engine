"""
Purpose:
Defines the Protocols that decouple modules from
concrete implementations throughout the core.

Description:
Any object that satisfies the required attributes or methods is accepted —
no inheritance needed. This allows loaders, writers, and filter objects to
be swapped freely as long as they match the expected shape.

Contracts
---------
DataFrameLoadable
    Any object with a load(source) method that returns a DataFrame.
DataFrameOutput
    Any object with a write(df) method that accepts a DataFrame.
Filters
    Any object carrying the five query parameters: region, country,
    startYear, endYear, and operation.

Notes
-----
- No inheritance is required — any object matching the shape satisfies the contract.
- These interfaces are type-checking aids; Python does not enforce them at runtime.
- Filters.operation defaults to "avg" in engine.py when None is passed.
"""

from typing import Protocol
import pandas as pd


class Filters(Protocol):
    """
    Protocol for the query parameters passed into the pipeline.

    Any object carrying these attributes satisfies the contract and
    can be used in other modules. Concrete implementations are free to add
    validation or defaults.

    Attributes
    ----------
    region : str or None
        Continent to filter on (case-insensitive). None skips region filtering.
    country : str or None
        Country name to filter on (case-insensitive). None skips country filtering.
    startYear : int or None
        Lower bound of the year range (inclusive). When endYear is None, treated
        as an exact year match. None skips or relaxes the year filter.
    endYear : int or None
        Upper bound of the year range (inclusive). When startYear is None, treated
        as an exact year match. None skips or relaxes the year filter.
    operation : str or None
        Aggregation to apply — "sum", "avg", or "average" (case-insensitive).
        None defaults to "avg" inside engine.py.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>>
    >>> @dataclass
    ... class QueryFilters:
    ...     region: str | None = None
    ...     country: str | None = None
    ...     startYear: int | None = None
    ...     endYear: int | None = None
    ...     operation: str | None = None
    ...
    >>> filters: Filters = QueryFilters(region="Asia", startYear=2000, endYear=2020, operation="sum")
    """

    region: str | None
    country: str | None
    startYear: int | None
    endYear: int | None
    operation: str | None
