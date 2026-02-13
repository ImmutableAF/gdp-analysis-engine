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
from typing import Tuple
from pathlib import Path

from src.paths import get_base_config_path
from src.utils.args_manager import parse_cli_args
from src.utils.logging_factory import initialize_logging

from src.core.pipeline import run_pipeline
from src.core.data_cleaning import clean_gdp_data
from src.core.data_loader.data_loading import load_data
from src.core.config_manager.config_models import QueryConfig
from src.core.config_manager.config_handle import get_base_config, get_query_config


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
    base_config = get_base_config(get_base_config_path())
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
    df_raw, query_config = initialize_system()
    df_clean = clean_gdp_data(df_raw, fill_method="ffill")
    run_pipeline(df_clean, query_config)