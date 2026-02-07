from typing import List, Tuple
import pandas as pd

def get_all_regions(df: pd.DataFrame) -> List[str]:
    if "Continent" not in df.columns:
        return []
    return df["Continent"].dropna().str.title().unique().tolist()

def get_all_countries(df: pd.DataFrame) -> List[str]:
    if "Country Name" not in df.columns:
        return []
    return df["Country Name"].dropna().str.title().unique().tolist()

def get_year_range(df: pd.DataFrame) -> Tuple[int, int]:
    if "Year" not in df.columns or df["Year"].empty:
        return (1960, 2024)
    
    years = pd.to_numeric(df["Year"], errors='coerce').dropna()
    if years.empty:
        return (1960, 2024)

    stats = years.agg(['min', 'max'])
    return int(stats['min']), int(stats['max'])