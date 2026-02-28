"""
Analytics Views
===============
Streamlit render functions for the Analytics tab.
Fetches from analytics API (:8011) and renders charts.
"""

import os
import httpx
import pandas as pd
import streamlit as st
from src.plugins.ui import analytics_charts as ac

_ANALYTICS_URL = os.environ.get("ANALYTICS_API_URL", "http://localhost:8011")


# ── client ────────────────────────────────────────────────────────────────────

def _get(path: str, params: dict) -> pd.DataFrame:
    try:
        r = httpx.get(f"{_ANALYTICS_URL}{path}", params=params, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception as e:
        st.error(f"Analytics API error on {path}: {e}")
        return pd.DataFrame()


# ── controls ──────────────────────────────────────────────────────────────────

def _year_range(key_prefix: str, default=(2015, 2020)):
    col1, col2 = st.columns(2)
    with col1:
        start = st.number_input("Start Year", min_value=1960, max_value=2024,
                                value=default[0], key=f"{key_prefix}_start")
    with col2:
        end = st.number_input("End Year", min_value=1960, max_value=2024,
                              value=default[1], key=f"{key_prefix}_end")
    return int(start), int(end)


def _continent_picker(key: str, default: str = "Europe") -> str:
    continents = ["Africa", "Asia", "Europe", "North America",
                  "Oceania", "South America", "Global"]
    idx = continents.index(default) if default in continents else 0
    return st.selectbox("Continent", continents, index=idx, key=key)


# ── sections ──────────────────────────────────────────────────────────────────

def render_top_bottom(metadata: dict):
    st.markdown("### 🏆 Top / Bottom Countries by GDP")
    col1, col2, col3 = st.columns(3)
    with col1:
        continent = _continent_picker("tb_continent")
    with col2:
        year = st.number_input("Year", min_value=1960, max_value=2024,
                               value=2020, key="tb_year")
    with col3:
        n = st.slider("Top / Bottom N", 5, 30, 10, key="tb_n")

    params = {"continent": continent, "year": int(year), "n": n}

    col_top, col_bot = st.columns(2)
    with col_top:
        df = _get("/top-countries", params)
        st.plotly_chart(ac.top_bottom_bar(df, f"Top {n} Countries — {continent} {int(year)}"),
                        use_container_width=True)
    with col_bot:
        df = _get("/bottom-countries", params)
        st.plotly_chart(ac.top_bottom_bar(df, f"Bottom {n} Countries — {continent} {int(year)}"),
                        use_container_width=True)


def render_growth_rate():
    st.markdown("### 📈 GDP Growth Rate by Country")
    col1, col2, col3 = st.columns(3)
    with col1:
        continent = _continent_picker("gr_continent")
    with col2:
        start = st.number_input("Start Year", 1960, 2024, 2015, key="gr_start")
    with col3:
        end = st.number_input("End Year", 1960, 2024, 2020, key="gr_end")

    df = _get("/gdp-growth-rate", {"continent": continent,
                                    "startYear": int(start), "endYear": int(end)})
    title = f"GDP Growth Rate — {continent} ({int(start)}–{int(end)})"
    st.plotly_chart(ac.growth_rate_line(df, f"Avg Growth Rate — {continent}"),
                    use_container_width=True)
    st.plotly_chart(ac.growth_rate_heatmap(df, title), use_container_width=True)


def render_avg_gdp_continent():
    st.markdown("### 🌍 Average GDP by Continent")
    start, end = _year_range("avg_cont")
    df = _get("/avg-gdp-by-continent", {"startYear": start, "endYear": end})
    st.plotly_chart(ac.avg_gdp_continent_bar(df), use_container_width=True)


def render_global_trend():
    st.markdown("### 🌐 Total Global GDP Trend")
    start, end = _year_range("global_trend")
    df = _get("/global-gdp-trend", {"startYear": start, "endYear": end})
    st.plotly_chart(ac.global_gdp_trend_line(df), use_container_width=True)


def render_fastest_continent():
    st.markdown("### 🚀 Fastest Growing Continent")
    start, end = _year_range("fastest_cont")
    df = _get("/fastest-growing-continent", {"startYear": start, "endYear": end})
    st.plotly_chart(ac.fastest_continent_bar(df), use_container_width=True)


def render_consistent_decline():
    st.markdown("### 📉 Countries with Consistent GDP Decline")
    col1, col2 = st.columns(2)
    with col1:
        x_years = st.slider("Consecutive Years", 2, 10, 3, key="decline_years")
    with col2:
        ref_year = st.number_input("Reference Year", 1960, 2024, 2020, key="decline_ref")

    df = _get("/consistent-decline", {"lastXYears": x_years, "referenceYear": int(ref_year)})
    if not df.empty:
        st.caption(f"{len(df)} countries declined every year for {x_years} consecutive years up to {int(ref_year)}")
    st.plotly_chart(ac.consistent_decline_bar(df), use_container_width=True)


def render_continent_share():
    st.markdown("### 🥧 Continent Share of Global GDP")
    start, end = _year_range("share")
    df = _get("/continent-gdp-share", {"startYear": start, "endYear": end})
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(ac.continent_share_pie(df), use_container_width=True)
    with col2:
        st.plotly_chart(ac.continent_share_bar(df), use_container_width=True)


# ── main entry ────────────────────────────────────────────────────────────────

def render_analytics_tab(metadata: dict):
    st.title("GDP Analytics")
    st.caption("Powered by Analytics API · All data fetched live from :8011")
    st.markdown("---")

    render_top_bottom(metadata)
    st.markdown("---")
    render_growth_rate()
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        render_avg_gdp_continent()
    with col2:
        render_global_trend()

    st.markdown("---")
    render_fastest_continent()
    st.markdown("---")
    render_consistent_decline()
    st.markdown("---")
    render_continent_share()