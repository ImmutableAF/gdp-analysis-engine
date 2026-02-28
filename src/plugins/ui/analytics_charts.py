"""
Analytics Charts
================
Plotly chart functions for the Analytics tab.
Same palette/layout conventions as charts.py.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
from src.plugins.ui.palette import CUSTOM_PALETTE, LAYOUT


# ── helpers ───────────────────────────────────────────────────────────────────

def _empty() -> go.Figure:
    fig = go.Figure()
    fig.update_layout(**LAYOUT)
    return fig


def _bar(df, x, y, title, color_col=None, text=True):
    fig = px.bar(
        df, x=x, y=y,
        color=color_col or y,
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".2s" if text else False,
        title=title,
    )
    fig.update_layout(**LAYOUT)
    fig.update_xaxes(tickangle=-40)
    return fig


# ── 1 & 2 — Top / Bottom Countries ────────────────────────────────────────────

def top_bottom_bar(df: pd.DataFrame, title: str) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.bar(
        df, x="country", y="gdp",
        color="gdp",
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".2s",
        title=title,
    )
    fig.update_layout(**LAYOUT)
    fig.update_xaxes(tickangle=-40)
    return fig


# ── 3 — GDP Growth Rate ────────────────────────────────────────────────────────

def growth_rate_heatmap(df: pd.DataFrame, title: str) -> go.Figure:
    """Country × Year heatmap of growth rate %."""
    if df.empty:
        return _empty()
    pivot = df.pivot(index="country", columns="year", values="growth_rate_pct")
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=CUSTOM_PALETTE,
        text=pivot.values.round(1),
        texttemplate="%{text}%",
        hovertemplate="Country: %{y}<br>Year: %{x}<br>Growth: %{z:.2f}%<extra></extra>",
    ))
    layout = {**LAYOUT, "title": title, "height": max(480, len(pivot) * 18)}
    fig.update_layout(**layout)
    return fig


def growth_rate_line(df: pd.DataFrame, title: str) -> go.Figure:
    """Line chart — avg growth per year across all countries."""
    if df.empty:
        return _empty()
    avg = df.groupby("year")["growth_rate_pct"].mean().reset_index()
    fig = px.line(avg, x="year", y="growth_rate_pct", markers=True, title=title)
    fig.update_traces(line=dict(color=CUSTOM_PALETTE[0], width=3), marker=dict(size=8))
    fig.update_layout(**LAYOUT, yaxis_title="Avg Growth Rate (%)")
    return fig


# ── 4 — Avg GDP by Continent ──────────────────────────────────────────────────

def avg_gdp_continent_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.bar(
        df.sort_values("avg_gdp", ascending=False),
        x="continent", y="avg_gdp",
        color="avg_gdp",
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".2s",
        title="Average GDP by Continent",
    )
    fig.update_layout(**LAYOUT)
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
    fig.update_layout(**LAYOUT, yaxis_title="Total GDP (USD)")
    return fig


# ── 6 — Fastest Growing Continent ────────────────────────────────────────────

def fastest_continent_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.bar(
        df.sort_values("growth_pct", ascending=True),
        x="growth_pct", y="continent",
        orientation="h",
        color="growth_pct",
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".1f",
        title="GDP Growth % by Continent",
    )
    fig.update_layout(**LAYOUT, xaxis_title="Growth (%)")
    return fig


# ── 7 — Consistent Decline ────────────────────────────────────────────────────

def consistent_decline_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.bar(
        df.sort_values("avg_decline_pct"),
        x="country", y="avg_decline_pct",
        color="avg_decline_pct",
        color_continuous_scale=CUSTOM_PALETTE[::-1],
        text_auto=".1f",
        title="Countries with Consistent GDP Decline (Avg % / Year)",
    )
    fig.update_layout(**LAYOUT, yaxis_title="Avg Decline (%)")
    fig.update_xaxes(tickangle=-40)
    return fig


# ── 8 — Continent Share ───────────────────────────────────────────────────────

def continent_share_pie(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.pie(
        df, names="continent", values="share_pct",
        color_discrete_sequence=CUSTOM_PALETTE,
        title="Continent Share of Global GDP",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(**LAYOUT)
    return fig


def continent_share_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty()
    fig = px.bar(
        df.sort_values("share_pct", ascending=False),
        x="continent", y="share_pct",
        color="share_pct",
        color_continuous_scale=CUSTOM_PALETTE,
        text_auto=".1f",
        title="Continent Share of Global GDP (%)",
    )
    fig.update_layout(**LAYOUT, yaxis_title="Share (%)")
    return fig