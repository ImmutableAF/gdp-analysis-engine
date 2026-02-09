"""
Chart Generation Functions
===========================

Plotly chart generation with custom color palette. All charts use CUSTOM_PALETTE
for consistent styling. Safe for large datasets and Streamlit reruns.

Chart Types:
- region_bar: Bar chart of GDP by continent
- country_bar: Top N countries bar chart
- country_treemap: Hierarchical treemap of countries
- year_scatter: GDP scatter plot with trendline
- year_line: Line chart of GDP over time
- year_bar: Bar chart of GDP by year
- growth_rate: Year-over-year growth rate bars

Functions
---------
region_bar(df)
    GDP by region bar chart
country_bar(df, title_suffix, top_n)
    Top countries bar chart
country_treemap(df, top_n)
    Countries hierarchical treemap
year_scatter(df, title_suffix, interpolate)
    GDP scatter plot with trendline
year_line(df, title_suffix, interpolate)
    GDP line chart
year_bar(df, title_suffix, interpolate)
    GDP by year bar chart
growth_rate(df, title_suffix, interpolate)
    Year-over-year growth rate chart

See Also
--------
palette : Color scheme constants
views : Chart rendering in UI

Notes
-----
All charts return empty go.Figure() for empty DataFrames (graceful degradation).
Color strategy switches between continuous and discrete based on data size.
Interpolation available for time-series charts to smooth missing values.

Examples
--------
>>> df = pd.DataFrame({"Continent": ["Asia"], "Value": [1000000]})
>>> fig = region_bar(df)
>>> fig.show()
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
    """
    Validate required columns exist in DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate
    cols : Set[str]
        Required column names
    chart_name : str
        Chart name for error message
    
    Raises
    ------
    ValueError
        If any required columns missing
    """
    missing = cols - set(df.columns)
    if missing:
        raise ValueError(f"{chart_name}: missing columns {missing}")


def _aggregate_by_year(df: pd.DataFrame, interpolate: bool) -> pd.DataFrame:
    """
    Aggregate values by year with optional interpolation.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Year and Value columns
    interpolate : bool
        If True, interpolate missing values
    
    Returns
    -------
    pd.DataFrame
        Aggregated yearly data sorted by year
    """
    yearly = df.groupby("Year", as_index=False)["Value"].sum().sort_values("Year")
    if interpolate:
        yearly["Value"] = yearly["Value"].interpolate()
    return yearly


def _make_continuous(colors: list[str], steps: int = 100) -> list[str]:
    """
    Generate continuous colorscale from discrete colors.
    
    Uses matplotlib LinearSegmentedColormap if available, otherwise repeats colors.
    
    Parameters
    ----------
    colors : list[str]
        Base discrete colors
    steps : int, default=100
        Number of interpolation steps
    
    Returns
    -------
    list[str]
        Continuous color scale
    """
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
    Select color palette strategy based on data size.
    
    Returns continuous scale for small datasets, discrete cycling for large.
    
    Parameters
    ----------
    n : int
        Number of data points
    chart_name : str
        Chart name (for debugging)
    max_cont : int, default=30
        Threshold for continuous vs discrete
    
    Returns
    -------
    tuple[bool, list[str]]
        (use_continuous, color_palette)
    """
    scale = _make_continuous(CUSTOM_PALETTE)
    if n <= max_cont:
        return True, scale.copy()
    return False, [CUSTOM_PALETTE[i % len(CUSTOM_PALETTE)] for i in range(n)]


# ---------- Chart Functions ----------


def region_bar(df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart of GDP by region.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Continent and Value columns
    
    Returns
    -------
    go.Figure
        Plotly bar chart sorted by value descending
    
    Examples
    --------
    >>> df = pd.DataFrame({"Continent": ["Asia", "Europe"], "Value": [1e12, 8e11]})
    >>> fig = region_bar(df)
    """
    _require_columns(df, {"Continent", "Value"}, "region_bar")
    if df.empty:
        return go.Figure()
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
    """
    Create bar chart of top N countries by GDP.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Country Code and Value columns
    title_suffix : str, default=""
        Optional title suffix (e.g., " — Asia")
    top_n : int or None, default=10
        Number of countries to show, None for all
    
    Returns
    -------
    go.Figure
        Plotly bar chart with rotated x-axis labels
    
    Examples
    --------
    >>> df = pd.DataFrame({"Country Code": ["USA", "CHN"], "Value": [2e13, 1.5e13]})
    >>> fig = country_bar(df, " — Top Economies", top_n=5)
    """
    _require_columns(df, {"Country Code", "Value"}, "country_bar")
    if df.empty:
        return go.Figure()
    
    top = df.sort_values("Value", ascending=False)
    
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
    """
    Create hierarchical treemap of countries by GDP.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Country Code and Value columns
    top_n : int or None, default=10
        Number of countries to show, None for all
    
    Returns
    -------
    go.Figure
        Plotly treemap figure
    
    Examples
    --------
    >>> df = pd.DataFrame({"Country Code": ["USA", "CHN"], "Value": [2e13, 1.5e13]})
    >>> fig = country_treemap(df, top_n=20)
    """
    _require_columns(df, {"Country Code", "Value"}, "country_treemap")
    if df.empty:
        return go.Figure()
    
    top = df.sort_values("Value", ascending=False)
    
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
    """
    Create scatter plot of GDP over time with trendline.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Year and Value columns
    title_suffix : str, default=""
        Optional title suffix
    interpolate : bool, default=False
        If True, interpolate missing values
    
    Returns
    -------
    go.Figure
        Plotly scatter with OLS trendline
    
    Examples
    --------
    >>> df = pd.DataFrame({"Year": [2000, 2010], "Value": [1e12, 1.5e12]})
    >>> fig = year_scatter(df, interpolate=True)
    """
    yearly = _aggregate_by_year(df, interpolate)
    if yearly.empty:
        return go.Figure()
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
    """
    Create line chart of GDP over time.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Year and Value columns
    title_suffix : str, default=""
        Optional title suffix
    interpolate : bool, default=False
        If True, interpolate missing values
    
    Returns
    -------
    go.Figure
        Plotly line chart with markers
    
    Examples
    --------
    >>> df = pd.DataFrame({"Year": [2000, 2010, 2020], "Value": [1e12, 1.5e12, 2e12]})
    >>> fig = year_line(df, " — USA")
    """
    yearly = _aggregate_by_year(df, interpolate)
    if yearly.empty:
        return go.Figure()
    
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
    """
    Create bar chart of GDP by year.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Year and Value columns
    title_suffix : str, default=""
        Optional title suffix
    interpolate : bool, default=False
        If True, interpolate missing values
    
    Returns
    -------
    go.Figure
        Plotly bar chart
    
    Examples
    --------
    >>> df = pd.DataFrame({"Year": [2015, 2016, 2017], "Value": [1e12, 1.1e12, 1.2e12]})
    >>> fig = year_bar(df)
    """
    yearly = _aggregate_by_year(df, interpolate)
    if yearly.empty:
        return go.Figure()
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
    """
    Create bar chart of year-over-year GDP growth rate.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Year and Value columns
    title_suffix : str, default=""
        Optional title suffix
    interpolate : bool, default=False
        If True, interpolate missing values before computing growth
    
    Returns
    -------
    go.Figure or None
        Plotly bar chart, None if insufficient data (<2 years)
    
    Notes
    -----
    Growth rate computed as: (Value[t] - Value[t-1]) / Value[t-1] * 100
    
    Examples
    --------
    >>> df = pd.DataFrame({"Year": [2018, 2019, 2020], "Value": [1e12, 1.05e12, 1.1e12]})
    >>> fig = growth_rate(df, interpolate=True)
    """
    yearly = _aggregate_by_year(df, interpolate)
    if len(yearly) < 2:
        return None
    yearly["Growth"] = yearly["Value"].pct_change() * 100
    yearly = yearly.dropna()
    if yearly.empty:
        return None
    
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