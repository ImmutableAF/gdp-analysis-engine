"""
Analytics Views
===============
Streamlit render functions for the Analytics tab.
Fetches from analytics API (:8011) and renders charts.

- All continent/year options are driven by metadata from :8010 — nothing hardcoded.
- PNG export uses the same two-phase strategy as export_utils.py.
"""

import io
import os
import zipfile

import httpx
import pandas as pd
import streamlit as st

from src.plugins.ui import analytics_charts as ac

_ANALYTICS_URL = os.environ.get("ANALYTICS_API_URL", "http://localhost:8011")


# ── API client ────────────────────────────────────────────────────────────────


def _get(path: str, params: dict) -> pd.DataFrame:
    try:
        r = httpx.get(f"{_ANALYTICS_URL}{path}", params=params, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception as e:
        st.error(f"Analytics API error on {path}: {e}")
        return pd.DataFrame()


# ── Metadata helpers ──────────────────────────────────────────────────────────


def _continents(metadata: dict) -> list[str]:
    """Derive continent list from metadata['regions'] — never hardcoded."""
    return sorted(metadata.get("regions", []))


def _year_bounds(metadata: dict) -> tuple[int, int]:
    yr = metadata.get("year_range", [1960, 2024])
    return int(yr[0]), int(yr[1])


# ── Shared controls ───────────────────────────────────────────────────────────


def _year_range_inputs(
    key_prefix: str,
    metadata: dict,
    default_start: int | None = None,
    default_end: int | None = None,
):
    min_y, max_y = _year_bounds(metadata)
    ds = default_start or min_y
    de = default_end or max_y
    col1, col2 = st.columns(2)
    with col1:
        start = st.number_input(
            "Start Year",
            min_value=min_y,
            max_value=max_y,
            value=ds,
            key=f"{key_prefix}_start",
        )
    with col2:
        end = st.number_input(
            "End Year",
            min_value=min_y,
            max_value=max_y,
            value=de,
            key=f"{key_prefix}_end",
        )
    return int(start), int(end)


def _continent_picker(key: str, metadata: dict, default: str = "") -> str:
    options = _continents(metadata)
    idx = options.index(default) if default in options else 0
    return st.selectbox("Continent", options, index=idx, key=key)


# ── PNG export ────────────────────────────────────────────────────────────────


def _register(name: str, fig) -> None:
    """Append a (name, fig) tuple to the analytics figures list in session state."""
    st.session_state.setdefault("analytics_figures", [])
    st.session_state["analytics_figures"].append((name, fig))


def render_analytics_export() -> None:
    """
    Two-phase PNG export for all rendered analytics charts.
    Phase 1 — Generate: render every registered figure to PNG and zip.
    Phase 2 — Download: hand the zip to the user.
    """
    figures = st.session_state.get("analytics_figures", [])

    st.session_state.setdefault("analytics_zip", None)
    st.session_state.setdefault("analytics_ready", False)

    has_figures = len(figures) > 0

    st.markdown("#### Export Charts")
    col1, col2 = st.columns(2)

    with col1:
        generate = st.button(
            "Generate PNGs",
            disabled=not has_figures,
            help=(
                f"Render {len(figures)} chart(s) to PNG and zip"
                if has_figures
                else "No charts loaded yet"
            ),
            key="analytics_generate_btn",
        )

    if generate:
        with st.spinner(f"Rendering {len(figures)} chart(s)…"):
            buf = io.BytesIO()
            try:
                with zipfile.ZipFile(buf, "w") as zf:
                    for name, fig in figures:
                        zf.writestr(f"{name}.png", fig.to_image(format="png", scale=2))
                buf.seek(0)
                st.session_state["analytics_zip"] = buf
                st.session_state["analytics_ready"] = True
            except Exception as e:
                st.session_state["analytics_zip"] = None
                st.session_state["analytics_ready"] = False
                st.error(
                    f"Export failed: {e}\n\n"
                    "Kaleido + Windows tip: try once per session or restart the app."
                )

    with col2:
        st.download_button(
            "Download ZIP",
            data=(
                st.session_state["analytics_zip"]
                if st.session_state["analytics_ready"]
                else b""
            ),
            file_name="analytics_charts.zip",
            mime="application/zip",
            disabled=not st.session_state["analytics_ready"],
            help=(
                "Download charts ZIP"
                if st.session_state["analytics_ready"]
                else "Generate charts first"
            ),
            key="analytics_download_btn",
        )


# ── Section renderers ─────────────────────────────────────────────────────────


def render_top_bottom(metadata: dict) -> None:
    st.markdown("### Top / Bottom Countries by GDP")
    col1, col2, col3 = st.columns(3)
    with col1:
        continent = _continent_picker("tb_continent", metadata)
    with col2:
        min_y, max_y = _year_bounds(metadata)
        year = st.number_input(
            "Year",
            min_value=min_y,
            max_value=max_y,
            value=min(2020, max_y),
            key="tb_year",
        )
    with col3:
        n = st.slider("Top / Bottom N", 5, 30, 10, key="tb_n")

    params = {"continent": continent, "year": int(year), "n": n}

    col_top, col_bot = st.columns(2)
    with col_top:
        df = _get("/top-countries", params)
        fig = ac.top_bottom_bar(df, f"Top {n} — {continent} {int(year)}")
        st.plotly_chart(fig, width="stretch")
        _register(f"top_{n}_{continent}_{int(year)}", fig)
    with col_bot:
        df = _get("/bottom-countries", params)
        fig = ac.top_bottom_bar(df, f"Bottom {n} — {continent} {int(year)}")
        st.plotly_chart(fig, width="stretch")
        _register(f"bottom_{n}_{continent}_{int(year)}", fig)


def render_growth_rate(metadata: dict) -> None:
    st.markdown("### GDP Growth Rate by Country")
    col1, col2, col3 = st.columns(3)
    min_y, max_y = _year_bounds(metadata)
    with col1:
        continent = _continent_picker("gr_continent", metadata)
    with col2:
        start = st.number_input(
            "Start Year",
            min_value=min_y,
            max_value=max_y,
            value=min(2015, max_y),
            key="gr_start",
        )
    with col3:
        end = st.number_input(
            "End Year",
            min_value=min_y,
            max_value=max_y,
            value=min(2020, max_y),
            key="gr_end",
        )

    df = _get(
        "/gdp-growth-rate",
        {"continent": continent, "startYear": int(start), "endYear": int(end)},
    )
    title = f"GDP Growth Rate — {continent} ({int(start)}–{int(end)})"

    fig_line = ac.growth_rate_line(df, f"Avg Growth Rate — {continent}")
    st.plotly_chart(fig_line, width="stretch")
    _register(f"growth_rate_line_{continent}", fig_line)

    fig_heat = ac.growth_rate_heatmap(df, title)
    st.plotly_chart(fig_heat, width="stretch")
    _register(f"growth_rate_heatmap_{continent}", fig_heat)


def render_avg_gdp_continent(metadata: dict) -> None:
    st.markdown("### Average GDP by Continent")
    _, max_y = _year_bounds(metadata)
    start, end = _year_range_inputs("avg_cont", metadata, default_end=min(2020, max_y))
    df = _get("/avg-gdp-by-continent", {"startYear": start, "endYear": end})
    fig = ac.avg_gdp_continent_bar(df)
    st.plotly_chart(fig, width="stretch")
    _register(f"avg_gdp_continent_{start}_{end}", fig)


def render_global_trend(metadata: dict) -> None:
    st.markdown("### Total Global GDP Trend")
    _, max_y = _year_bounds(metadata)
    start, end = _year_range_inputs(
        "global_trend", metadata, default_end=min(2020, max_y)
    )
    df = _get("/global-gdp-trend", {"startYear": start, "endYear": end})
    fig = ac.global_gdp_trend_line(df)
    st.plotly_chart(fig, width="stretch")
    _register(f"global_gdp_trend_{start}_{end}", fig)


def render_fastest_continent(metadata: dict) -> None:
    st.markdown("### Fastest Growing Continent")
    _, max_y = _year_bounds(metadata)
    start, end = _year_range_inputs(
        "fastest_cont", metadata, default_end=min(2020, max_y)
    )
    df = _get("/fastest-growing-continent", {"startYear": start, "endYear": end})
    fig = ac.fastest_continent_bar(df)
    st.plotly_chart(fig, width="stretch")
    _register(f"fastest_continent_{start}_{end}", fig)


def render_consistent_decline(metadata: dict) -> None:
    st.markdown("### Countries with Consistent GDP Decline")
    col1, col2 = st.columns(2)
    with col1:
        x_years = st.slider("Consecutive Years", 2, 10, 3, key="decline_years")
    with col2:
        _, max_y = _year_bounds(metadata)
        ref_year = st.number_input(
            "Reference Year",
            min_value=1960,
            max_value=max_y,
            value=min(2020, max_y),
            key="decline_ref",
        )
    df = _get(
        "/consistent-decline", {"lastXYears": x_years, "referenceYear": int(ref_year)}
    )
    if not df.empty:
        st.caption(
            f"{len(df)} countries declined every year "
            f"for {x_years} consecutive years up to {int(ref_year)}"
        )
    fig = ac.consistent_decline_bar(df)
    st.plotly_chart(fig, width="stretch")
    _register(f"consistent_decline_{x_years}yr_{int(ref_year)}", fig)


def render_continent_share(metadata: dict) -> None:
    st.markdown("### Continent Share of Global GDP")
    _, max_y = _year_bounds(metadata)
    start, end = _year_range_inputs("share", metadata, default_end=min(2020, max_y))
    df = _get("/continent-gdp-share", {"startYear": start, "endYear": end})
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = ac.continent_share_pie(df)
        st.plotly_chart(fig_pie, width="stretch")
        _register(f"continent_share_pie_{start}_{end}", fig_pie)
    with col2:
        fig_bar = ac.continent_share_bar(df)
        st.plotly_chart(fig_bar, width="stretch")
        _register(f"continent_share_bar_{start}_{end}", fig_bar)


# ── Main entry ────────────────────────────────────────────────────────────────


def render_analytics_tab(metadata: dict) -> None:
    # Reset figure registry on every full render so stale charts don't accumulate
    st.session_state["analytics_figures"] = []

    st.title("GDP Analytics")
    st.markdown("---")

    render_top_bottom(metadata)
    st.markdown("---")
    render_growth_rate(metadata)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        render_avg_gdp_continent(metadata)
    with col2:
        render_global_trend(metadata)

    st.markdown("---")
    render_fastest_continent(metadata)
    st.markdown("---")
    render_consistent_decline(metadata)
    st.markdown("---")
    render_continent_share(metadata)

    # Export panel lives at the bottom — all charts are registered by this point
    st.markdown("---")
    render_analytics_export()
