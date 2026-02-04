# pipeline/run_pipeline.py
from pathlib import Path
import logging
import pandas as pd

from loading_core.loader_registry import LoaderRegistry
# Import the functional validator instead of the class
from pipeline.data_validator import validate_data 
from config_core.config_models import QueryConfig
from pipeline.transform import transform_raw_gdp
from pipeline.filter import filter_data
from pipeline.aggregate import aggregate_data


def run_pipeline(file_path: Path, query_config: QueryConfig) -> pd.DataFrame:
    """
    Main pipeline orchestrator refactored for functional purity.
    """
    logger = logging.getLogger("pipeline")
    registry = LoaderRegistry()

    # ------------------- Load -------------------
    # Registry ensures the returned df is normalized from a CSV
    logger.info(f"Loading data from {file_path}")
    df = registry.load(file_path)
    logger.info(f"Data loaded successfully: {df.shape}")

    # ------------------- Transform -------------------
    # Wide-to-long conversion and renaming 'Continent' -> 'Region'
    df = transform_raw_gdp(df)
    logger.debug(f"Data transformed to long format: {df.shape}")

    # ------------------- Validate -------------------
    # Using the functional validate_data to enforce Region/Country integrity
    df = validate_data(df)
    logger.info(f"Data validated successfully: {df.shape[0]} rows remaining")

    # ------------------- Filter -------------------
    # Subsetting data based on query_config criteria (Region, Year, Country)
    df_filtered = filter_data(df, query_config)
    logger.info(f"Data filtered: {df_filtered.shape[0]} rows remaining")
    logger.debug(f"Filtered DataFrame head:\n{df_filtered.head()}")

    # ------------------- Aggregate -------------------
    # Final statistical computation (Sum/Average)
    result_df = aggregate_data(df_filtered, query_config)
    logger.info("Data aggregation complete")
    logger.debug(f"Aggregated DataFrame head:\n{result_df.head()}")

    return result_df