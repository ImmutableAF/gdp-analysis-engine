import logging
import pandas as pd
from typing import List

# Updated to match the columns AFTER transform.py has run
REQUIRED_COLUMNS = ["Country Name", "Region"]

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Functional validator using vectorized operations and boolean indexing.
    """
    logger = logging.getLogger("data_validator")
    
    if df.empty:
        return df

    # 1. Check Schema (Functional approach: all() with list comprehension)
    if not all(col in df.columns for col in REQUIRED_COLUMNS):
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        raise ValueError(f"Missing required columns: {missing}")

    # 2. Row-level validation (Functional: Boolean Indexing instead of loops)
    # We create a mask where REQUIRED_COLUMNS are NOT NA and NOT empty strings
    is_valid = df[REQUIRED_COLUMNS].notna().all(axis=1) & \
               (df[REQUIRED_COLUMNS] != "").all(axis=1)
    
    # Log dropped rows using functional filter/lambda logic
    dropped_count = len(df) - is_valid.sum()
    if dropped_count > 0:
        logger.error(f"Dropped {dropped_count} rows due to missing required data.")

    # Apply the filter
    validated_df = df[is_valid].copy()

    # 3. Handle Optional Years dynamically (Functional: set difference)
    # This replaces your manual 1960-2024 list
    all_years = [str(year) for year in range(1960, 2025)]
    missing_years = list(filter(lambda y: y not in validated_df.columns, all_years))
    
    # Vectorized assignment for missing columns
    if missing_years:
        logger.warning(f"Missing {len(missing_years)} year columns. Filling with NaN.")
        for year in missing_years:
            validated_df[year] = pd.NA

    logger.info(f"Validation complete. {len(validated_df)} rows remaining.")
    return validated_df