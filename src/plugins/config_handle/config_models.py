"""
Purpose:
Immutable dataclasses that hold configuration values used across the package.

Description:
Frozen dataclasses that represent the three distinct configuration concerns —
application setup (BaseConfig), query parameters (QueryConfig), and analytics
chart defaults (AnalyticsConfig).

Models
------
BaseConfig
    Application-level settings: data paths, logging, and output mode.
QueryConfig
    Query-level filter and aggregation parameters passed to the pipeline.
AnalyticsConfig
    Default filter values for the analytics tab charts.

Notes
-----
- All models are frozen — fields cannot be modified after construction.
- All models are constructed once.
- QueryConfig and AnalyticsConfig fields are all optional; None means no filter
  or default behavior applies.

Examples
--------
>>> base = BaseConfig(
...     data_dir=Path("data"),
...     data_filename="gdp_data.xlsx",
...     log_dir=Path("logs"),
...     max_log_size=1000000,
...     output_mode="ui"
... )
>>> query = QueryConfig(region="Asia", country=None, startYear=2000, endYear=2020, operation="sum")
>>> analytics = AnalyticsConfig(defaultYear=2020, startYear=2015, endYear=2020, topN=10, consecutiveYears=3, referenceYear=2020)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class BaseConfig:
    """
    Application-level configuration for paths, logging, and output mode.

    Attributes
    ----------
    data_dir : Path
        Directory where the input data file is located.
    data_filename : str
        Name of the data file to load (e.g. "gdp_data.xlsx").
    log_dir : Path
        Directory where log files are written.
    max_log_size : int
        Maximum size of a single log file in bytes before rotation.
    output_mode : str
        Determines how results are presented (e.g. "ui", "cli").
    """

    data_dir: Path
    data_filename: str
    log_dir: Path
    max_log_size: int
    output_mode: str


@dataclass(frozen=True)
class QueryConfig:
    """
    Query-level configuration carrying filter and aggregation parameters.

    All fields are optional. None on any field means no constraint is applied
    for that parameter.

    Attributes
    ----------
    region : str or None
        Continent to filter on (case-insensitive).
    country : str or None
        Country name to filter on (case-insensitive).
    startYear : int or None
        Lower bound of the year range (inclusive).
    endYear : int or None
        Upper bound of the year range (inclusive).
    operation : str or None
        Aggregation to apply — "sum", "avg", or "average". Defaults to "avg" in engine.py.
    """

    region: Optional[str]
    country: Optional[str]
    startYear: Optional[int]
    endYear: Optional[int]
    operation: Optional[str]


@dataclass(frozen=True)
class AnalyticsConfig:
    """
    Default filter values for the analytics tab charts.

    All fields are optional. When None, the views layer falls back to
    safe hardcoded defaults (e.g. max_year for year fields, 10 for topN).

    Attributes
    ----------
    defaultYear : int or None
        Default single-year value used by the Top/Bottom countries picker.
    startYear : int or None
        Default start of year range used by all range-based charts.
    endYear : int or None
        Default end of year range used by all range-based charts.
    topN : int or None
        Default N for the Top/Bottom N slider (5–30).
    consecutiveYears : int or None
        Default consecutive years for the Consistent Decline slider (2–10).
    referenceYear : int or None
        Default reference year for the Consistent Decline chart.
    """

    continent: Optional[str]
    defaultYear: Optional[int]
    startYear: Optional[int]
    endYear: Optional[int]
    topN: Optional[int]
    consecutiveYears: Optional[int]
    referenceYear: Optional[int]
