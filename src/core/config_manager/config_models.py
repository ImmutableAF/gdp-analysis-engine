"""
Immutable Configuration Data Models
====================================

Defines frozen dataclasses for system and query configurations. Immutability
enforced via frozen=True ensures configurations cannot be modified after creation.

Classes
-------
BaseConfig
    System configuration (paths, logging)
QueryConfig
    User query parameters (region, years, operations)

Notes
-----
Both classes use frozen dataclasses for immutability. Modifications require
creating new instances via dataclasses.replace().

Examples
--------
>>> config = BaseConfig(
...     data_directory=Path("data"),
...     default_file="gdp.csv",
...     log_directory=Path("logs"),
...     max_log_size=1000000
... )
>>> config.max_log_size = 500000  # Raises FrozenInstanceError
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class BaseConfig:
    """
    System configuration for data paths and logging.
    
    Immutable configuration containing file system paths and logging parameters.
    Validated by config_handler.validate_base_config() after loading.
    
    Attributes
    ----------
    data_directory : Path
        Directory containing GDP data files
    default_file : str
        Default CSV filename to load
    log_directory : Path
        Directory for log file storage
    max_log_size : int
        Maximum log file size in bytes (for rotation)
    
    See Also
    --------
    config_loader.load_base_config : Load from JSON
    config_handler.validate_base_config : Validate constraints
    
    Notes
    -----
    Frozen dataclass prevents modification. Use dataclasses.replace() for updates.
    
    Examples
    --------
    >>> config = BaseConfig(
    ...     data_directory=Path("data"),
    ...     default_file="gdp_data.csv",
    ...     log_directory=Path("logs"),
    ...     max_log_size=1000000
    ... )
    """
    data_directory: Path
    default_file: str
    log_directory: Path
    max_log_size: int


@dataclass(frozen=True)
class QueryConfig:
    """
    User query parameters for data filtering and aggregation.
    
    Immutable configuration for pipeline operations. Optional fields allow
    partial specification. Sanitized by config_handler.sanatize_query_config().
    
    Attributes
    ----------
    region : Optional[str]
        Geographic region filter (e.g., "Asia", "Europe")
    startYear : Optional[int]
        Start year for time range filter
    endYear : Optional[int]
        End year for time range filter
    operation : Optional[str]
        Aggregation operation ("sum", "avg", "average")
    
    See Also
    --------
    config_loader.load_query_config : Load from JSON
    config_handler.sanatize_query_config : Validate and sanitize
    
    Notes
    -----
    All fields optional to support flexible querying. Invalid values set to None
    during sanitization rather than raising errors.
    
    Examples
    --------
    >>> query = QueryConfig(
    ...     region="Asia",
    ...     startYear=2000,
    ...     endYear=2020,
    ...     operation="avg"
    ... )
    """
    region: Optional[str]
    startYear: Optional[int]
    endYear: Optional[int]
    operation: Optional[str]