"""
Pure visualization layer
STRICT input contracts
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional


# -------------------------
# VALIDATION
# -------------------------
def _require(df: pd.DataFrame, cols: set[str], name: str):
    if not cols.issubset(df.columns):
        raise ValueError(f"{name} requires columns {cols}")


# -------------------------
# REGION / COUNTRY
# -------------------------
def region_bar(df: pd.DataFrame) -> go.Figure:
    _require(df, {"Continent", "Value"}, "region_bar")

    return px.bar(
        df.sort_values("Value", ascending=False),
        x="Continent",
        y="Value",
        title="GDP by Region",
    )


def country_bar(df: pd.DataFrame, title_suffix="") -> go.Figure:
    _require(df, {"Country Name", "Value"}, "country_bar")

    return px.bar(
        df.sort_values("Value", ascending=False),
        x="Country Name",
        y="Value",
        title=f"GDP by Country{title_suffix}",
    )


def country_treemap(df: pd.DataFrame) -> go.Figure:
    _require(df, {"Country Name", "Value"}, "country_treemap")

    return px.treemap(
        df,
        path=["Country Name"],
        values="Value",
        title="GDP Distribution",
    )


# -------------------------
# TEMPORAL
# -------------------------
def _yearly(df: pd.DataFrame, interpolate: bool):
    _require(df, {"Year", "Value"}, "temporal chart")

    yearly = df.groupby("Year", as_index=False)["Value"].sum().sort_values("Year")

    if interpolate:
        yearly = (
            yearly.set_index("Year")
            .reindex(range(yearly["Year"].min(), yearly["Year"].max() + 1))
            .interpolate()
            .reset_index()
        )

    return yearly


def year_scatter(df, title="", interpolate=False) -> go.Figure:
    y = _yearly(df, interpolate)
    return px.scatter(y, x="Year", y="Value", trendline="ols",
                      title=f"GDP Scatter{title}")


def year_line(df, title="", interpolate=False) -> go.Figure:
    y = _yearly(df, interpolate)
    return px.line(y, x="Year", y="Value", markers=True,
                   title=f"GDP Trend{title}")


def year_bar(df, title="", interpolate=False) -> go.Figure:
    y = _yearly(df, interpolate)
    return px.bar(y, x="Year", y="Value",
                  title=f"GDP by Year{title}")


def growth_rate(df, title="", interpolate=False) -> Optional[go.Figure]:
    y = _yearly(df, interpolate)

    if len(y) < 2:
        return None

    y["Growth"] = y["Value"].pct_change() * 100
    y = y.dropna()

    fig = go.Figure()
    fig.add_bar(x=y["Year"], y=y["Growth"])
    fig.update_layout(title=f"YoY Growth{title}",
                      yaxis_title="%")

    return fig
