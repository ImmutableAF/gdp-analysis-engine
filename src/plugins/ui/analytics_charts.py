"""
Analytics Charts
================
Plotly chart functions for the Analytics tab.
Same palette/layout conventions as charts.py.

Chart functions receive DataFrames that have already been processed by
apply_country_codes() in the views layer — they are pure rendering functions
with no networking or data-fetching concerns.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.plugins.ui.palette import CUSTOM_PALETTE, LAYOUT


# ── sizing constants ──────────────────────────────────────────────────────────

CHART_HEIGHT = 520  # side-by-side charts
WIDE_CHART_HEIGHT = 560  # full-width single-column charts
HEATMAP_ROW_HEIGHT = 22  # px per country row in heatmap
HEATMAP_MIN_HEIGHT = 520

_TICK_FONT = dict(size=11)
_COUNTRY_AXIS = dict(tickangle=-40, tickfont=_TICK_FONT)


# ── helpers ───────────────────────────────────────────────────────────────────


def _empty() -> go.Figure:
    fig = go.Figure()
    fig.update_layout(**LAYOUT)
    return fig


def _base_layout(height: int, extra: dict | None = None) -> dict:
    layout = {**LAYOUT, "height": height}
    if extra:
        layout.update(extra)
    return layout


# ── Country-code utility ──────────────────────────────────────────────────────


def apply_country_codes(df: pd.DataFrame, code_map: dict[str, str]) -> pd.DataFrame:
    """
    Replace the 'country' column with ISO country codes where available.
    Preserves the original full name in 'country_name' for hover tooltips and
    the side lookup table.

    Called in analytics_views.py before passing df to any chart function.

    Parameters
    ----------
    df       : DataFrame with a 'country' column (full names from analytics API).
    code_map : {Country Name: Country Code} — built once in streamlit_entry.py
               via CoreAPIClient.run() and passed down. Never fetched here.
    """
    if df.empty or "country" not in df.columns or not code_map:
        return df
    out = df.copy()
    out["country_name"] = out["country"]
    out["country"] = out["country"].map(code_map).fillna(out["country"])
    return out


# ── 1 & 2 — Top / Bottom Countries ────────────────────────────────────────────


def top_bottom_bar(df: pd.DataFrame, title: str) -> go.Figure:
    """
    Bar chart of top/bottom N countries by GDP.

    Expects df pre-processed by ``apply_country_codes()``:

    - ``country`` — ISO code (x-axis)
    - ``country_name`` — full name (hover tooltip)

    Parameters
    ----------
    df : pd.DataFrame
        Pre-processed data with ``country`` and ``gdp`` columns.
    title : str
        Chart title.
    """
    if df.empty:
        return _empty()

    has_names = "country_name" in df.columns
    fig = px.bar(
        df,
        x="country",
        y="gdp",
        color="gdp",
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".2s",
        title=title,
        custom_data=["country_name"] if has_names else None,
    )
    if has_names:
        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>GDP: %{y:.3s}<extra></extra>"
        )
    fig.update_layout(
        **_base_layout(CHART_HEIGHT, {"margin": {"l": 60, "r": 30, "t": 60, "b": 100}})
    )
    fig.update_xaxes(**_COUNTRY_AXIS)
    return fig


# ── 3 — GDP Growth Rate ────────────────────────────────────────────────────────


def growth_rate_heatmap(df: pd.DataFrame, title: str) -> go.Figure:
    """
    Country × Year heatmap of growth rate %.
    Expects df pre-processed by apply_country_codes() so y-axis shows ISO codes.
    """
    if df.empty:
        return _empty()
    pivot = df.pivot(index="country", columns="year", values="growth_rate_pct")
    height = max(HEATMAP_MIN_HEIGHT, len(pivot) * HEATMAP_ROW_HEIGHT)
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=CUSTOM_PALETTE,
            text=pivot.values.round(1),
            texttemplate="%{text}%",
            hovertemplate="Country: %{y}<br>Year: %{x}<br>Growth: %{z:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        **_base_layout(
            height,
            {
                "title": title,
                "margin": {"l": 140, "r": 30, "t": 60, "b": 60},
                "yaxis": {"tickfont": _TICK_FONT},
            },
        )
    )
    return fig


def growth_rate_line(df: pd.DataFrame, title: str) -> go.Figure:
    """Line chart — avg growth per year across all countries (no codes needed)."""
    if df.empty:
        return _empty()
    avg = df.groupby("year")["growth_rate_pct"].mean().reset_index()
    fig = px.line(avg, x="year", y="growth_rate_pct", markers=True, title=title)
    fig.update_traces(line=dict(color=CUSTOM_PALETTE[0], width=3), marker=dict(size=8))
    fig.update_layout(
        **_base_layout(WIDE_CHART_HEIGHT, {"yaxis_title": "Avg Growth Rate (%)"})
    )
    return fig


# ── 4 — Avg GDP by Continent ──────────────────────────────────────────────────


def avg_gdp_continent_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.bar(
        df.sort_values("avg_gdp", ascending=False),
        x="continent",
        y="avg_gdp",
        color="avg_gdp",
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".2s",
        title="Average GDP by Continent",
    )
    fig.update_layout(**_base_layout(CHART_HEIGHT))
    return fig


# ── 5 — Global GDP Trend ──────────────────────────────────────────────────────


def global_gdp_trend_line(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.area(df, x="year", y="total_gdp", title="Total Global GDP Trend")
    fig.update_traces(
        line=dict(color=CUSTOM_PALETTE[0], width=3),
        fillcolor="rgba(255,85,85,0.25)",
    )
    fig.update_layout(**_base_layout(CHART_HEIGHT, {"yaxis_title": "Total GDP (USD)"}))
    return fig


# ── 6 — Fastest Growing Continent ────────────────────────────────────────────


def fastest_continent_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.bar(
        df.sort_values("growth_pct", ascending=True),
        x="growth_pct",
        y="continent",
        orientation="h",
        color="growth_pct",
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".1f",
        title="GDP Growth % by Continent",
    )
    fig.update_layout(
        **_base_layout(
            WIDE_CHART_HEIGHT,
            {
                "xaxis_title": "Growth (%)",
                "margin": {"l": 120, "r": 30, "t": 60, "b": 60},
            },
        )
    )
    return fig


# ── 7 — Consistent Decline ────────────────────────────────────────────────────


def consistent_decline_bar(df: pd.DataFrame) -> go.Figure:
    """
    Bar chart of countries with consistent GDP decline.

    Expects df pre-processed by ``apply_country_codes()``:

    - ``country`` — ISO code (x-axis)
    - ``country_name`` — full name (hover tooltip)

    Parameters
    ----------
    df : pd.DataFrame
        Pre-processed data with ``country`` and ``avg_decline_pct`` columns.
    """
    if df.empty:
        return _empty()

    has_names = "country_name" in df.columns
    fig = px.bar(
        df.sort_values("avg_decline_pct"),
        x="country",
        y="avg_decline_pct",
        color="avg_decline_pct",
        color_continuous_scale=CUSTOM_PALETTE[::-1],
        text_auto=".1f",
        title="Countries with Consistent GDP Decline (Avg % / Year)",
        custom_data=["country_name"] if has_names else None,
    )
    if has_names:
        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Avg Decline: %{y:.1f}%<extra></extra>"
        )
    fig.update_layout(
        **_base_layout(
            WIDE_CHART_HEIGHT,
            {
                "yaxis_title": "Avg Decline (%)",
                "margin": {"l": 60, "r": 30, "t": 60, "b": 100},
            },
        )
    )
    fig.update_xaxes(**_COUNTRY_AXIS)
    return fig


# ── 8 — Continent Share ───────────────────────────────────────────────────────


def continent_share_pie(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.pie(
        df,
        names="continent",
        values="share_pct",
        color_discrete_sequence=CUSTOM_PALETTE,
        title="Continent Share of Global GDP",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(**_base_layout(CHART_HEIGHT))
    return fig


def continent_share_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.bar(
        df.sort_values("share_pct", ascending=False),
        x="continent",
        y="share_pct",
        color="share_pct",
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".1f",
        title="Continent Share of Global GDP (%)",
    )
    fig.update_layout(**_base_layout(CHART_HEIGHT, {"yaxis_title": "Share (%)"}))
    return fig
