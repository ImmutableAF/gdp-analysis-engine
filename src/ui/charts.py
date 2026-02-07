"""
Chart generation functions
All functions are pure and return new figure objects
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


DEFAULT_LAYOUT = dict(
    template="plotly_dark",
    height=480,
    title_x=0.5,
    margin=dict(l=40, r=40, t=60, b=40),
)


def _require_columns(df: pd.DataFrame, cols: set, chart_name: str):
    """Validate required columns exist"""
    missing = cols - set(df.columns)
    if missing:
        raise ValueError(f"{chart_name}: missing columns {missing}")


def _aggregate_by_year(df: pd.DataFrame, interpolate: bool) -> pd.DataFrame:
    """Helper to aggregate data by year"""
    yearly = (
        df.groupby("Year", as_index=False)["Value"]
        .sum()
        .sort_values("Year")
    )

    if interpolate:
        yearly["Value"] = yearly["Value"].interpolate()

    return yearly


def region_bar(df: pd.DataFrame) -> go.Figure:
    """Bar chart comparing regions"""
    _require_columns(df, {"Continent", "Value"}, "region_bar")

    fig = px.bar(
        df.sort_values("Value", ascending=False),
        x="Continent",
        y="Value",
        color="Value",
        color_continuous_scale="Turbo",
        text_auto=".2s",
        title="GDP by Region",
    )

    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def country_bar(df: pd.DataFrame, title_suffix: str = "") -> go.Figure:
    """Bar chart comparing countries"""
    _require_columns(df, {"Country Name", "Value"}, "country_bar")

    fig = px.bar(
        df.sort_values("Value", ascending=False).head(20),
        x="Country Name",
        y="Value",
        color="Value",
        color_continuous_scale="Viridis",
        text_auto=".2s",
        title=f"Top Countries by GDP{title_suffix}",
    )

    fig.update_layout(**DEFAULT_LAYOUT)
    fig.update_xaxes(tickangle=-45)
    return fig


def country_treemap(df: pd.DataFrame) -> go.Figure:
    """Treemap showing country distribution"""
    _require_columns(df, {"Country Name", "Value"}, "country_treemap")

    fig = px.treemap(
        df,
        path=["Country Name"],
        values="Value",
        color="Value",
        color_continuous_scale="Viridis",
        title="GDP Distribution by Country",
    )

    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def year_scatter(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    """Scatter plot showing GDP over time"""
    yearly = _aggregate_by_year(df, interpolate)

    fig = px.scatter(
        yearly,
        x="Year",
        y="Value",
        size="Value",
        color="Value",
        trendline="ols",
        color_continuous_scale="Plasma",
        title=f"GDP Over Time{title_suffix}",
    )

    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def year_line(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    """Line chart showing GDP over time"""
    yearly = _aggregate_by_year(df, interpolate)

    fig = px.line(
        yearly,
        x="Year",
        y="Value",
        markers=True,
        title=f"GDP Over Time{title_suffix}",
    )

    fig.update_traces(
        line=dict(color="#3498db", width=3),
        marker=dict(size=8, color="#e74c3c"),
    )

    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def year_bar(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    """Bar chart showing GDP by year"""
    yearly = _aggregate_by_year(df, interpolate)

    fig = px.bar(
        yearly,
        x="Year",
        y="Value",
        color="Value",
        color_continuous_scale="Blues",
        text_auto=".2s",
        title=f"GDP by Year{title_suffix}",
    )

    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def growth_rate(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure | None:
    """Bar chart showing year-over-year growth rate"""
    yearly = _aggregate_by_year(df, interpolate)

    if len(yearly) < 2:
        return None

    yearly["Growth"] = yearly["Value"].pct_change() * 100
    yearly = yearly.dropna()

    fig = px.bar(
        yearly,
        x="Year",
        y="Growth",
        color="Growth",
        color_continuous_scale=["#e74c3c", "#f1c40f", "#2ecc71"],
        text_auto=".1f",
        title=f"Year-over-Year Growth Rate{title_suffix}",
    )

    fig.update_layout(
        **DEFAULT_LAYOUT,
        yaxis_title="Growth (%)",
    )

    return fig