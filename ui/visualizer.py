import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List
from config_core.config_models import QueryConfig

def plot_bar(df: pd.DataFrame, config: QueryConfig):
    """Region-wise GDP Bar Chart."""
    plt.figure(figsize=(10, 6))
    # Using 'Region' and 'Value' (or the aggregated column name)
    # Note: df comes from aggregate_data, so column is 'Average GDP' or 'Total GDP'
    val_col = [c for c in df.columns if "GDP" in c][0]
    sns.barplot(data=df, x="Region", y=val_col, palette="viridis")
    plt.title(f"{config.operation.capitalize()} GDP by Region ({config.year})")
    plt.ylabel("GDP Value")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_pie(df: pd.DataFrame, config: QueryConfig):
    """Region-wise GDP Distribution (Pie Chart)."""
    val_col = [c for c in df.columns if "GDP" in c][0]
    plt.figure(figsize=(8, 8))
    plt.pie(df[val_col], labels=df["Region"], autopct='%1.1f%%', startangle=140)
    plt.title(f"Regional Distribution of {config.operation.capitalize()} GDP")
    plt.show()

def generate_dashboard(df: pd.DataFrame, config: QueryConfig):
    """
    Main entry point for visualization.
    Uses functional mapping to avoid traditional loops.
    """
    if df.empty:
        print("No data available for visualization.")
        return

    # Dispatch dictionary mapping config strings to functions
    chart_dispatch = {
        "bar": plot_bar,
        "pie": plot_pie
    }

    # Functional Construct: Use filter to get valid chart types, 
    # then map to execute them via lambda.
    valid_charts = filter(lambda x: x in chart_dispatch, config.dashboard_charts)
    list(map(lambda chart_type: chart_dispatch[chart_type](df, config), valid_charts))