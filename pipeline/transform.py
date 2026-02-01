# pipeline/transform.py
import pandas as pd


def transform_raw_gdp(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform wide-format GDP CSV/Excel to long-format:
    - Rename 'Continent' → 'Region'
    - Melt year columns (1960-2024) → 'Year' & 'Value'
    """
    if "Continent" not in df.columns:
        raise ValueError("Missing required column 'Continent' in raw data")

    df = df.rename(columns={"Continent": "Region"})

    # Detect year columns (all numeric)
    year_cols = [col for col in df.columns if col.isdigit()]

    # Melt wide → long
    df_long = df.melt(
        id_vars=["Country Name", "Region"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Value"
    )

    # Convert types
    df_long["Year"] = pd.to_numeric(df_long["Year"], errors="coerce", downcast="integer")
    df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce")

    return df_long
