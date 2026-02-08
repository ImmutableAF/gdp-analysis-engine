"""
Chart generation functions
Fully hands-off palette: single CUSTOM_PALETTE drives all charts
Safe for large datasets and reruns
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Set, Optional
from itertools import cycle

# ---------- Base palette ----------
CUSTOM_PALETTE = ["#FF5555", "#FF937E", "#C1E59F", "#A3D78A"]

# ---------- Layout ----------
LAYOUT = dict(
    template="plotly_dark",
    height=480,
    title_x=0.5,
    margin=dict(l=40, r=40, t=60, b=40),
)

# ---------- Helpers ----------

def _require_columns(df: pd.DataFrame, cols: Set[str], chart_name: str) -> None:
    missing = cols - set(df.columns)
    if missing:
        raise ValueError(f"{chart_name}: missing columns {missing}")

def _aggregate_by_year(df: pd.DataFrame, interpolate: bool) -> pd.DataFrame:
    yearly = df.groupby("Year", as_index=False)["Value"].sum().sort_values("Year")
    if interpolate:
        yearly["Value"] = yearly["Value"].interpolate()
    return yearly

def _make_continuous(colors: list[str], steps: int = 100) -> list[str]:
    """Generates a continuous colorscale from discrete colors"""
    if len(colors) <= 1:
        return colors * steps
    try:
        from matplotlib.colors import LinearSegmentedColormap, to_hex
        cmap = LinearSegmentedColormap.from_list("auto_cmap", colors)
        return [to_hex(cmap(i / (steps - 1))) for i in range(steps)]
    except ImportError:
        return colors * steps  # fallback without matplotlib

def _safe_palette(n: int, chart_name: str, max_cont: int = 30) -> tuple[bool, list[str]]:
    """
    Returns (use_continuous, palette)
    - Continuous for small n
    - Discrete cycling for large n
    """
    scale = _make_continuous(CUSTOM_PALETTE)
    if n <= max_cont:
        return True, scale.copy()
    return False, [CUSTOM_PALETTE[i % len(CUSTOM_PALETTE)] for i in range(n)]

# ---------- Chart Functions ----------

def region_bar(df: pd.DataFrame) -> go.Figure:
    _require_columns(df, {"Continent", "Value"}, "region_bar")
    if df.empty: return go.Figure()
    use_cont, palette = _safe_palette(len(df), "region_bar", 30)
    
    fig = px.bar(
        df.sort_values("Value", ascending=False),
        x="Continent",
        y="Value",
        color="Value" if use_cont else None,
        color_continuous_scale=palette if use_cont else None,
        text_auto=".2s",
        title="GDP by Region"
    )
    if not use_cont:
        fig.update_traces(marker_color=palette)
    fig.update_layout(**LAYOUT)
    return fig

def country_bar(df: pd.DataFrame, title_suffix: str = "", top_n: Optional[int] = 10) -> go.Figure:
    _require_columns(df, {"Country Code", "Value"}, "country_bar")
    if df.empty: 
        return go.Figure()
    
    # Sort by value descending
    top = df.sort_values("Value", ascending=False)
    
    # Limit to top_n if provided
    if top_n is not None:
        top = top.head(top_n)
    
    use_cont, palette = _safe_palette(len(top), "country_bar", 20)
    
    if use_cont:
        fig = px.bar(
            top,
            x="Country Code",
            y="Value",
            color="Value",
            color_continuous_scale=palette,
            text_auto=".2s",
            title=f"Top {len(top)} Countries by GDP{title_suffix}"
        )
    else:
        fig = px.bar(
            top,
            x="Country Code",
            y="Value",
            text_auto=".2s",
            title=f"Top {len(top)} Countries by GDP{title_suffix}"
        )
        fig.update_traces(marker_color=palette)
    
    fig.update_layout(**LAYOUT, autosize=True)
    fig.update_xaxes(tickangle=-45)
    return fig

def country_treemap(df: pd.DataFrame, top_n: Optional[int] = 10) -> go.Figure:
    _require_columns(df, {"Country Code", "Value"}, "country_treemap")
    if df.empty: 
        return go.Figure()
    
    top = df.sort_values("Value", ascending=False)
    
    # Limit to top_n if provided
    if top_n is not None:
        top = top.head(top_n)
    
    use_cont, palette = _safe_palette(len(top), "country_treemap", 500)
    
    fig = px.treemap(
        top,
        path=["Country Code"],
        values="Value",
        color="Value" if use_cont else None,
        color_continuous_scale=palette if use_cont else None,
        title=f"Top {len(top)} Countries by GDP"
    )
    
    if not use_cont:
        fig.update_traces(marker_color=palette)
    
    fig.update_layout(**LAYOUT)
    return fig

def year_scatter(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    yearly = _aggregate_by_year(df, interpolate)
    if yearly.empty: return go.Figure()
    use_cont, palette = _safe_palette(len(yearly), "year_scatter", 100)
    
    fig = px.scatter(
        yearly,
        x="Year",
        y="Value",
        size="Value",
        size_max=10,
        color="Value" if use_cont else None,
        color_continuous_scale=palette if use_cont else None,
        trendline="ols",
        title=f"GDP Over Time{title_suffix}"
    )
    if not use_cont:
        fig.update_traces(marker_color=palette)
    fig.update_layout(**LAYOUT)
    return fig

def year_line(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    yearly = _aggregate_by_year(df, interpolate)
    if yearly.empty: return go.Figure()
    
    color = CUSTOM_PALETTE[0]
    fig = px.line(
        yearly,
        x="Year",
        y="Value",
        markers=True,
        title=f"GDP Over Time{title_suffix}"
    )
    fig.update_traces(line=dict(color=color, width=3),
                      marker=dict(size=8, color=color))
    fig.update_layout(**LAYOUT)
    return fig

def year_bar(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> go.Figure:
    yearly = _aggregate_by_year(df, interpolate)
    if yearly.empty: return go.Figure()
    use_cont, palette = _safe_palette(len(yearly), "year_bar", 100)
    
    fig = px.bar(
        yearly,
        x="Year",
        y="Value",
        color="Value" if use_cont else None,
        color_continuous_scale=palette if use_cont else None,
        text_auto=".2s",
        title=f"GDP by Year{title_suffix}"
    )
    if not use_cont:
        fig.update_traces(marker_color=palette)
    fig.update_layout(**LAYOUT)
    return fig

def growth_rate(df: pd.DataFrame, title_suffix: str = "", interpolate: bool = False) -> Optional[go.Figure]:
    yearly = _aggregate_by_year(df, interpolate)
    if len(yearly) < 2: return None
    yearly["Growth"] = yearly["Value"].pct_change() * 100
    yearly = yearly.dropna()
    if yearly.empty: return None
    
    use_cont, palette = _safe_palette(len(yearly), "growth_rate", 100)
    fig = px.bar(
        yearly,
        x="Year",
        y="Growth",
        color="Growth" if use_cont else None,
        color_continuous_scale=palette if use_cont else None,
        text_auto=".1f",
        title=f"Year-over-Year Growth Rate{title_suffix}"
    )
    if not use_cont:
        fig.update_traces(marker_color=palette)
    fig.update_layout(**LAYOUT, yaxis_title="Growth (%)")
    return fig
