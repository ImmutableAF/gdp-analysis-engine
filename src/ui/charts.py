"""
Chart generation functions
All functions are pure and return new figure objects
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Set, Optional

# Reusable configuration for visual consistency across the dashboard
DEFAULT_LAYOUT = dict(
    template="plotly_dark",
    height=480,
    title_x=0.5,
    margin=dict(l=40, r=40, t=60, b=40),
)

# ---------- Internal Helpers ----------

def _require_columns(df: pd.DataFrame, cols: Set[str], chart_name: str) -> None:
    missing = cols - set(df.columns)
    if missing:
        raise ValueError(f"{chart_name}: missing columns {missing}")


def _aggregate_by_year(df: pd.DataFrame, interpolate: bool) -> pd.DataFrame:
    yearly = (
        df.groupby("Year", as_index=False)["Value"]
        .sum()
        .sort_values("Year")
    )
    if interpolate:
        yearly["Value"] = yearly["Value"].interpolate()
    return yearly


# ---------- Visualization Functions ----------

def region_bar(df: pd.DataFrame) -> go.Figure:
    """Bar chart comparing regions by total GDP."""
    _require_columns(df, {"Continent", "Value"}, "region_bar")

    # Color scale for regions based on GDP
    color_scale = "Viridis"  # used for continuous value shading

    fig = px.bar(
        df.sort_values("Value", ascending=False),
        x="Continent",
        y="Value",
        color="Value",
        color_continuous_scale=color_scale,
        text_auto=".2s",
        title="GDP by Region",
    )
    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def country_bar(df: pd.DataFrame, title_suffix: str = "") -> go.Figure:
    """Bar chart comparing the top 20 countries by GDP."""
    _require_columns(df, {"Country Code", "Value"}, "country_bar")

    # Color scale for top countries based on GDP value
    color_scale = "Viridis"  # continuous scale for shading bars by GDP

    top_df = df.sort_values("Value", ascending=False).head(20)

    fig = px.bar(
        top_df,
        x="Country Code",
        y="Value",
        color="Value",
        color_continuous_scale=color_scale,
        text_auto=".2s",
        title=f"Top 20 Countries by GDP{title_suffix}",
    )
    fig.update_layout(**DEFAULT_LAYOUT, autosize=True)
    fig.update_yaxes(nticks=10)
    fig.update_xaxes(tickangle=-45)
    fig.update_coloraxes(colorbar_len=1.1, colorbar_thickness=15, colorbar_y=0.5)
    return fig


def country_treemap(df: pd.DataFrame) -> go.Figure:
    """Treemap showing proportional GDP distribution by country code."""
    _require_columns(df, {"Country Code", "Value"}, "country_treemap")

    # Color palette for proportional country GDP
    color_scale = "cividis"  # continuous shading by GDP value

    fig = px.treemap(
        df,
        path=["Country Code"],
        values="Value",
        color="Value",
        color_continuous_scale=color_scale,
        title="GDP Distribution by Country",
    )
    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def year_scatter(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    """Scatter plot with OLS trendline showing GDP evolution."""
    yearly = _aggregate_by_year(df, interpolate)

    # Color scale for scatter points
    color_scale = "turbo"  # points colored by GDP value

    fig = px.scatter(
        yearly,
        x="Year",
        y="Value",
        size="Value",
        size_max=10,
        color="Value",
        trendline="ols",
        color_continuous_scale=color_scale,
        title=f"GDP Over Time{title_suffix}",
    )
    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def year_line(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    """High-contrast line chart for temporal GDP trends."""
    yearly = _aggregate_by_year(df, interpolate)

    # Line and marker colors for visibility
    line_color = "#3498db"  # line color
    marker_color = "#e74c3c"  # marker color

    fig = px.line(
        yearly,
        x="Year",
        y="Value",
        markers=True,
        title=f"GDP Over Time{title_suffix}",
    )
    fig.update_traces(line=dict(color=line_color, width=3),
                      marker=dict(size=8, color=marker_color))
    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def year_bar(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    """Bar chart representing annual GDP volume."""
    yearly = _aggregate_by_year(df, interpolate)

    # Color scale for bars over years
    color_scale = "Blues"

    fig = px.bar(
        yearly,
        x="Year",
        y="Value",
        color="Value",
        color_continuous_scale=color_scale,
        text_auto=".2s",
        title=f"GDP by Year{title_suffix}",
    )
    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def growth_rate(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> Optional[go.Figure]:
    """Calculates and visualizes YoY growth percentage."""
    yearly = _aggregate_by_year(df, interpolate)

    if len(yearly) < 2:
        return None

    yearly["Growth"] = yearly["Value"].pct_change() * 100
    yearly = yearly.dropna()

    # Color scale for YoY growth
    color_scale = ["#872419", "#15064D"]  # red → blue for negative → positive growth

    fig = px.bar(
        yearly,
        x="Year",
        y="Growth",
        color="Growth",
        color_continuous_scale=color_scale,
        text_auto=".1f",
        title=f"Year-over-Year Growth Rate{title_suffix}",
    )
    fig.update_layout(**DEFAULT_LAYOUT, yaxis_title="Growth (%)")
    return fig
