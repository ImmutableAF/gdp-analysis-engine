"""
GDP Analysis Engine - CLI Entry Point
======================================

Command-line interface for non-UI data processing pipeline. Handles configuration
loading, data ingestion, cleaning, and query execution.

Execution Flow:
1. Parse CLI args (--debug, -fpath)
2. Load/validate base configuration
3. Initialize logging system
4. Load and clean data file
5. Load and sanitize query configuration
6. Execute pipeline with query parameters

Functions
---------
get_paths()
    Resolve configuration file paths
get_base_config(base_config_path)
    Load and validate base config, fallback to defaults
get_valid_attr(df)
    Extract valid regions and year range from DataFrame
load_data(file_path)
    Load data via LoaderRegistry
get_query_config(df)
    Load and sanitize query config against data
initialize_system()
    Orchestrate system initialization
    
See Also
--------
src.ui.app : Streamlit web interface entry point
src.core.pipeline : Data transformation functions

Notes
-----
Uses fallback strategy for missing/invalid configs. CLI args override config
file settings. Debug mode affects logging level and file destination.

Examples
--------
Basic execution:
$ python main.py

With debug and custom file:
$ python main.py --debug -fpath data/custom_gdp.csv
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Tuple
import keyboard as keyboard

from src.utils.args_manager import parse_cli_args
from src.utils.logging_factory import initialize_logging

from src.core.pipeline import run_pipeline
from src.core.data_cleaning import clean_gdp_data
from src.core.data_loader.loader_registry import LoaderRegistry
from src.core.config_manager.config_models import BaseConfig, QueryConfig
from src.core.config_manager.config_handle import validate_base_config, sanatize_query_config
from src.core.config_manager.config_loader import load_base_config, load_default_config, load_query_config


def get_paths() -> Tuple[Path, Path]:
    """
    Resolve configuration file paths relative to script location.
    
    Returns
    -------
    Tuple[Path, Path]
        (base_config_path, query_config_path)
    
    Notes
    -----
    Paths resolved as: script_dir/data/configs/*.json
    
    Examples
    --------
    >>> base_path, query_path = get_paths()
    >>> print(base_path.name)
    base_config.json
    """
    base_dir = Path(__file__).parent

    base_config_path = base_dir / "data" / "configs" / "base_config.json"
    query_config_path = base_dir / "data" / "configs" / "query_config.json"

    return base_config_path, query_config_path


def get_base_config(base_config_path: Path) -> BaseConfig:
    """
    Load and validate base configuration with fallback to defaults.
    
    Attempts to load from file and validate. On any failure (missing file,
    invalid JSON, validation error), falls back to hardcoded defaults.
    
    Parameters
    ----------
    base_config_path : Path
        Path to base_config.json
    
    Returns
    -------
    BaseConfig
        Validated configuration or defaults
    
    Notes
    -----
    Exceptions silently caught - always returns valid config. Use for
    graceful degradation when config files unavailable.
    
    Examples
    --------
    >>> config = get_base_config(Path("data/configs/base_config.json"))
    >>> print(config.data_directory)
    data
    """
    try:
        base_config = load_base_config(base_config_path)
        validate_base_config(base_config)
    except Exception as e:
        base_config = load_default_config()

    return base_config


def get_valid_attr(df):
    """
    Extract valid regions and year range from wide-format DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Wide-format DataFrame with Continent column and year columns
    
    Returns
    -------
    tuple
        (regions_list, (min_year, max_year))
    
    Notes
    -----
    Assumes year columns are digit-only strings. Filters columns via
    str.isdigit() before conversion to int.
    
    Examples
    --------
    >>> df = pd.DataFrame({"Continent": ["Asia"], "1960": [100], "2020": [200]})
    >>> regions, years = get_valid_attr(df)
    >>> print(regions)
    ['Asia']
    >>> print(years)
    (1960, 2020)
    """
    regions = df["Continent"].unique().tolist()

    years = list(map(int, filter(str.isdigit, df.columns)))
    year_range = (min(years), max(years))

    return regions, year_range


def load_data(file_path: Path) -> pd.DataFrame:
    """
    Load data file via LoaderRegistry plugin system.
    
    Parameters
    ----------
    file_path : Path
        Data file path (CSV, Excel, etc.)
    
    Returns
    -------
    pd.DataFrame
        Loaded data in wide format
    
    Raises
    ------
    ValueError
        If no loader supports file type
    FileNotFoundError
        If file doesn't exist
    
    Examples
    --------
    >>> df = load_data(Path("data/gdp_data.csv"))
    >>> print(df.shape)
    (266, 65)
    """
    registry = LoaderRegistry()
    df = registry.load(file_path)
    return df


def get_query_config(df: pd.DataFrame) -> QueryConfig:
    """
    Load and sanitize query configuration against DataFrame.
    
    Loads query config from file and validates regions/years against actual
    data. Invalid values set to None.
    
    Parameters
    ----------
    df : pd.DataFrame
        Wide-format data for validation
    
    Returns
    -------
    QueryConfig
        Sanitized query configuration
    
    Notes
    -----
    Extracts valid regions and year range from df, then sanitizes loaded
    config against these constraints.
    
    Examples
    --------
    >>> df = load_data(Path("data/gdp_data.csv"))
    >>> query = get_query_config(df)
    >>> print(query.region)
    Asia
    """
    query_config = sanatize_query_config(load_query_config(get_paths()[1]), *get_valid_attr(df))
    return query_config


def initialize_system() -> Tuple[pd.DataFrame, QueryConfig]:
    """
    Orchestrate complete system initialization.
    
    Execution sequence:
    1. Parse CLI arguments
    2. Load base configuration (with fallback)
    3. Initialize logging system
    4. Determine data file path (CLI override or config default)
    5. Load data via registry
    6. Load and sanitize query config
    
    Returns
    -------
    Tuple[pd.DataFrame, QueryConfig]
        (loaded_dataframe, sanitized_query_config)
    
    Notes
    -----
    CLI -fpath argument overrides config default_file if valid path provided.
    Logger initialized before data loading for error capture.
    
    Examples
    --------
    >>> df, query = initialize_system()
    >>> print(df.shape)
    (266, 65)
    >>> print(query.operation)
    sum
    """
    args = parse_cli_args()
    base_config = get_base_config(get_paths()[0])
    initialize_logging(base_config, args.debug)
    logger = logging.getLogger("main")
    
    filepath = Path(args.fpath) if args.fpath and Path(args.fpath).is_file() else base_config.data_directory / base_config.default_file
    logger.debug(f"filepath of data : {filepath}")

    df = load_data(filepath)

    return df, get_query_config(df)


if __name__ == "__main__":
    """
    Main execution block for CLI mode.
    
    Workflow:
    1. Initialize system (config, logging, data load)
    2. Clean loaded data (forward fill missing values)
    3. Run pipeline with query parameters
    4. Print results to stdout
    
    Notes
    -----
    Pipeline results printed via run_pipeline(). For programmatic access,
    use pipeline functions directly instead of run_pipeline().
    """
    df, query_config = initialize_system()
    df_clean = clean_gdp_data(df, fill_method="ffill")
    run_pipeline(df_clean, query_config)