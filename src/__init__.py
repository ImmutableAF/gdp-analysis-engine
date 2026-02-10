"""
GDP Analysis Engine - Package
===================================

A comprehensive data analysis system for processing and visualizing global GDP data
with support for temporal analysis, regional comparisons, and interactive dashboards.

Modules
-------
core
    Core data processing, pipeline, and configuration management
ui
    Streamlit-based user interface and visualization components
utils
    Utility functions for argument parsing and logging

Architecture Overview
---------------------
The GDP Analysis Engine follows a modular architecture with clear separation
of concerns:

- **Data Layer** (core.data_loader): Pluggable data loading system
- **Processing Layer** (core.pipeline): Pure functional data transformations
- **Configuration Layer** (core.config_manager): Immutable configuration management
- **Presentation Layer** (ui): Streamlit-based interactive dashboard
- **Utilities Layer** (utils): Cross-cutting concerns (logging, CLI)

Key Features
------------
- Dynamic plugin-based data loading supporting CSV and Excel formats
- Pure functional data pipeline with no side effects
- Immutable configuration with validation and sanitization
- Interactive visualizations with Plotly
- Export capabilities (CSV, PNG charts)
- Comprehensive logging system

Design Principles
-----------------
1. **Separation of Concerns**: Each package has a single, well-defined responsibility
2. **Immutability**: Configuration and data structures are immutable where possible
3. **Pure Functions**: Data transformations have no side effects
4. **Plugin Architecture**: Extensible loader system without modifying core code
5. **Type Safety**: Extensive use of type hints and dataclasses

Typical Workflow
----------------
>>> from src.core.data_loader import LoaderRegistry
>>> from src.core.data_cleaning import clean_gdp_data
>>> from src.core.pipeline import transform, apply_filters
>>>
>>> # Load data
>>> registry = LoaderRegistry()
>>> df = registry.load(Path("data/gdp.csv"))
>>>
>>> # Clean and transform
>>> clean_df = clean_gdp_data(df, fill_method='ffill')
>>> long_df = transform(clean_df)
>>>
>>> # Filter and analyze
>>> filtered = apply_filters(long_df, region='Asia', start_year=2000, end_year=2020)

See Also
--------
core : Core data processing and pipeline functionality
ui : User interface and visualization components
utils : Utility functions and helpers

Notes
-----
This package requires Python 3.10+ and depends on pandas, plotly, and streamlit.

Examples
--------
See the ``examples/`` directory for complete usage examples and tutorials.
"""

__all__ = ['core', 'ui', 'utils']