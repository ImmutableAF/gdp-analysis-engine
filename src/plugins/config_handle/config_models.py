"""
Purpose:
Immutable dataclasses that hold configuration values used across the package.

Description:
Frozen dataclasses that represent the four distinct configuration concerns —
application setup (BaseConfig), query parameters (QueryConfig), analytics
chart defaults (AnalyticsConfig), and server port bindings (PortsConfig).

Models
------
BaseConfig
    Application-level settings: data paths, logging, and output mode.
QueryConfig
    Query-level filter and aggregation parameters passed to the pipeline.
AnalyticsConfig
    Default filter values for the analytics tab charts.
PortsConfig
    Port numbers for the core and analytics API servers.

Notes
-----
- All models are frozen — fields cannot be modified after construction.
- All models are constructed once.
- QueryConfig and AnalyticsConfig fields are all optional; None means no filter
  or default behavior applies.
- PortsConfig fields are never None — sanitization always resolves them to
  valid port numbers before the servers start.

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
>>> ports = PortsConfig(core_port=8010, analytics_port=8011)
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

    Fields are Optional only to allow partial JSON files on disk — missing
    keys load as None. However, handle.get_analytics_config() always returns
    a fully sanitized instance with no None values: year fields are clamped
    to the actual data range, topN is clamped to [5, 30], and consecutiveYears
    is clamped to [2, 10]. Never consume a raw AnalyticsConfig from config_load
    directly — always go through handle.get_analytics_config().

    Attributes
    ----------
    continent : str or None
        Default continent for continent-picker widgets.
        None only before sanitization — resolved to a valid region by handle.py.
    defaultYear : int or None
        Default single-year value for the Top/Bottom countries picker.
        None only before sanitization — resolved to a valid year by handle.py.
    startYear : int or None
        Default start of year range for all range-based charts.
        None only before sanitization — resolved to a valid year by handle.py.
    endYear : int or None
        Default end of year range for all range-based charts.
        None only before sanitization — resolved to a valid year by handle.py.
    topN : int or None
        Default N for the Top/Bottom N slider (5–30).
        None only before sanitization — resolved to 10 by handle.py.
    consecutiveYears : int or None
        Default consecutive years for the Consistent Decline slider (2–10).
        None only before sanitization — resolved to 3 by handle.py.
    referenceYear : int or None
        Default reference year for the Consistent Decline chart.
        None only before sanitization — resolved to a valid year by handle.py.
    """

    continent: Optional[str]
    defaultYear: Optional[int]
    startYear: Optional[int]
    endYear: Optional[int]
    topN: Optional[int]
    consecutiveYears: Optional[int]
    referenceYear: Optional[int]


@dataclass(frozen=True)
class PortsConfig:
    """
    Port bindings for the core and analytics API servers.

    Fields are Optional only to allow partial JSON files on disk — missing
    keys load as None. handle.get_ports_config() always returns a fully
    resolved instance with no None values. Never consume a raw PortsConfig
    from config_load directly — always go through handle.get_ports_config().

    Attributes
    ----------
    core_port : int or None
        Port for the core API server (:8010 by default).
        None only before sanitization — resolved to 8010 by handle.py.
    analytics_port : int or None
        Port for the analytics API server (:8011 by default).
        None only before sanitization — resolved to 8011 by handle.py.
    """

    core_port: Optional[int]
    analytics_port: Optional[int]
