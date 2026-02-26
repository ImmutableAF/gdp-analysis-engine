"""
Purpose:
Immutable dataclasses that hold configuration values to be used across the package.

Description:
Frozen dataclasses that represent the two distinct configuration concerns —
application setup (BaseConfig) and query parameters (QueryConfig). 


Notes
-----
- Both models are frozen — fields cannot be modified after construction.
- Both models are constructed once.
- QueryConfig fields are all optional; None means no filter or default behavior applies.
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