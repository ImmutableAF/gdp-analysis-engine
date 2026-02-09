"""
Core Data Processing Package
=============================

Provides the fundamental data processing, pipeline, and configuration capabilities
for the GDP Analysis Engine. This package contains all business logic and data
transformation functions.

Subpackages
-----------
config_manager
    Configuration loading, validation, and sanitization
data_loader
    Pluggable data loading system with support for multiple file formats

Modules
-------
data_cleaning
    Data cleaning and preprocessing functions
handle
    Metadata extraction and data inspection utilities
pipeline
    Pure functional data transformation pipeline

Architecture
------------
The core package follows a functional programming paradigm with clear data flow:

1. **Load**: Dynamic loader registry loads data from files
2. **Clean**: Remove invalid values, fill missing data, handle duplicates
3. **Transform**: Convert wide format to long format for analysis
4. **Filter**: Apply region, country, and temporal filters
5. **Aggregate**: Compute statistics grouped by various dimensions

All transformations are **pure functions** that return new dataframes without
modifying input data, ensuring predictable behavior and easy testing.

Data Flow
---------
::

    Raw CSV/Excel → LoaderRegistry → DataFrame (wide format)
         ↓
    Clean (remove invalid, fill missing, drop duplicates)
         ↓
    Transform (wide → long format with Year column)
         ↓
    Filter (region, country, year range)
         ↓
    Aggregate (sum/average by grouping)
         ↓
    Visualization/Export

Key Components
--------------
Pipeline Functions
    Pure functions for transforming and filtering data
Cleaning Functions
    Validate, clean, and normalize GDP data
Metadata Extractors
    Extract regions, countries, and year ranges from data
Configuration System
    Immutable configurations with validation
Loader Registry
    Plugin-based system for loading different file formats

Design Patterns
---------------
- **Pure Functions**: No side effects in data transformations
- **Immutable Data**: Configurations use frozen dataclasses
- **Plugin Architecture**: Loaders discovered automatically via introspection
- **Separation of Concerns**: Each module has single responsibility

Type Safety
-----------
All functions use type hints extensively. The package expects:

- DataFrames with specific column schemas
- Path objects for file operations
- Typed configuration objects (BaseConfig, QueryConfig)

Examples
--------
Complete workflow example:

>>> from pathlib import Path
>>> from src.core import (
...     LoaderRegistry,
...     clean_gdp_data,
...     transform,
...     apply_filters,
...     aggregate_all
... )
>>> from src.core.config_manager import QueryConfig
>>>
>>> # Load data
>>> registry = LoaderRegistry()
>>> raw_df = registry.load(Path("data/gdp.csv"))
>>>
>>> # Clean
>>> clean_df = clean_gdp_data(raw_df, fill_method='ffill')
>>>
>>> # Transform to long format
>>> long_df = transform(clean_df)
>>>
>>> # Filter by region and years
>>> asia_df = apply_filters(long_df, region='Asia', start_year=2000, end_year=2020)
>>>
>>> # Aggregate
>>> result = aggregate_all(asia_df, operation='sum')

See Also
--------
config_manager : Configuration management system
data_loader : Dynamic data loading system
pipeline : Data transformation pipeline
data_cleaning : Data cleaning utilities

Notes
-----
The core package has no dependencies on the UI layer, making it suitable
for use in batch processing, APIs, or other non-interactive contexts.
"""

from .data_cleaning import clean_gdp_data
from .metadata import get_all_regions, get_all_countries, get_year_range
from .pipeline import transform, apply_filters, aggregate_all, run_pipeline
from .data_loader import LoaderRegistry

__all__ = [
    'clean_gdp_data',
    'get_all_regions',
    'get_all_countries',
    'get_year_range',
    'transform',
    'apply_filters',
    'aggregate_all',
    'run_pipeline',
    'LoaderRegistry',
]