"""
Analytics Views
===============
Pure rendering layer for the Analytics tab.

Responsibilities
----------------
- Render widgets (continent pickers, year inputs, sliders).
- Detect when widget values differ from the params used to fetch the current data.
- Trigger a lazy per-section re-fetch via the injected fetch_fn when params change.
- Render charts and code-lookup tables from DataFrames held in session state.

Non-responsibilities (handled upstream)
----------------------------------------
- HTTP calls         → AnalyticsAPIClient in outputs.py
- Contract validation → contracts.py + streamlit_entry._fetch_and_validate()
- Upfront data fetch  → streamlit_entry.fetch_analytics_upfront()

Parameters injected by streamlit_entry
---------------------------------------
analytics_data : AnalyticsData
    Pre-fetched DataFrames for all sections, loaded on first render.
fetch_fn : Callable[[str, dict], pd.DataFrame]
    Closure over AnalyticsAPIClient. Called by views when widget values change.
    Signature: fetch_fn(section_key: str, params: dict) -> pd.DataFrame
"""

from __future__ import annotations

import io
import zipfile
from typing import Callable

import pandas as pd
import streamlit as st

from src.plugins.ui import analytics_charts as ac

# Section keys — must match keys in AnalyticsData and _SECTION_MAP in streamlit_entry
_S_TOP = "top_countries"
_S_BOTTOM = "bottom_countries"
_S_GROWTH = "growth_rate"
_S_AVG_CONT = "avg_gdp_continent"
_S_GLOBAL = "global_trend"
_S_FASTEST = "fastest_continent"
_S_DECLINE = "consistent_decline"
_S_SHARE = "continent_share"

# Fallback defaults — only used if analytics_cfg is {} due to API failure
_FB_CONTINENT = ""
_FB_DEFAULT_YEAR = 2020
_FB_START_YEAR = 2015
_FB_END_YEAR = 2020
_FB_TOP_N = 10
_FB_CONSEC_YEARS = 3
_FB_REFERENCE_YEAR = 2020


# ── Config helpers ────────────────────────────────────────────────────────────


def _cfg_year(
    analytics_cfg: dict, key: str, fallback: int, min_y: int, max_y: int
) -> int:
    return max(min_y, min(max_y, int(analytics_cfg.get(key, fallback))))


def _cfg_int(analytics_cfg: dict, key: str, fallback: int) -> int:
    return int(analytics_cfg.get(key, fallback))


def _cfg_str(analytics_cfg: dict, key: str, fallback: str) -> str:
    return str(analytics_cfg.get(key, fallback))


# ── Metadata helpers ──────────────────────────────────────────────────────────


def _continents(metadata: dict) -> list[str]:
    return sorted(metadata.get("regions", []))


def _year_bounds(metadata: dict) -> tuple[int, int]:
    yr = metadata.get("year_range", [1960, 2024])
    return int(yr[0]), int(yr[1])


# ── Session state helpers ─────────────────────────────────────────────────────


def _get_section_df(analytics_data, section: str) -> pd.DataFrame:
    return getattr(analytics_data, section, pd.DataFrame())


def _set_section_df(analytics_data, section: str, df: pd.DataFrame) -> None:
    object.__setattr__(analytics_data, section, df)


def _get_section_params(section: str) -> dict:
    return st.session_state.get(f"_params_{section}", {})


def _set_section_params(section: str, params: dict) -> None:
    st.session_state[f"_params_{section}"] = params


# ── Re-fetch trigger ──────────────────────────────────────────────────────────


def _maybe_refetch(
    section: str,
    params: dict,
    analytics_data,
    fetch_fn: Callable[[str, dict], pd.DataFrame],
) -> pd.DataFrame:
    """
    Compare current widget params against what was last fetched.
    If different, call fetch_fn and update analytics_data + session state.
    Returns the current (possibly just refreshed) DataFrame for the section.
    """
    last_params = _get_section_params(section)

    if params != last_params:
        df = fetch_fn(section, params)
        _set_section_df(analytics_data, section, df)
        _set_section_params(section, params)
        return df

    return _get_section_df(analytics_data, section)


# ── Error display ─────────────────────────────────────────────────────────────


def _show_error(section: str) -> None:
    errors = st.session_state.get("analytics_errors", {})
    if section in errors:
        st.error(errors[section])


# ── Code-lookup table ─────────────────────────────────────────────────────────


def _code_table(
    df: pd.DataFrame, value_col: str, value_label: str, ascending: bool = False
) -> None:
    if df.empty or "country_name" not in df.columns:
        return
    table = (
        df[["country", "country_name", value_col]]
        .rename(
            columns={
                "country": "Code",
                "country_name": "Country",
                value_col: value_label,
            }
        )
        .sort_values(value_label, ascending=ascending)
        .reset_index(drop=True)
    )
    table.index += 1
    st.dataframe(table, width="stretch", height=400)


# ── Shared widgets ────────────────────────────────────────────────────────────


def _continent_picker(key: str, metadata: dict, default: str) -> str:
    options = _continents(metadata)
    idx = options.index(default) if default in options else 0
    return st.selectbox("Continent", options, index=idx, key=key)


def _year_range_inputs(
    key_prefix: str, metadata: dict, default_start: int, default_end: int
) -> tuple[int, int]:
    min_y, max_y = _year_bounds(metadata)
    col1, col2 = st.columns(2)
    with col1:
        start = st.number_input(
            "Start Year",
            min_value=min_y,
            max_value=max_y,
            value=default_start,
            key=f"{key_prefix}_start",
        )
    with col2:
        end = st.number_input(
            "End Year",
            min_value=min_y,
            max_value=max_y,
            value=default_end,
            key=f"{key_prefix}_end",
        )
    return int(start), int(end)


# ── PNG export ────────────────────────────────────────────────────────────────


def _register(name: str, fig) -> None:
    st.session_state.setdefault("analytics_figures", [])
    st.session_state["analytics_figures"].append((name, fig))


def render_analytics_export() -> None:
    figures = st.session_state.get("analytics_figures", [])
    st.session_state.setdefault("analytics_zip", None)
    st.session_state.setdefault("analytics_ready", False)

    has_figures = len(figures) > 0
    st.markdown("#### Export Charts")
    col1, col2 = st.columns(2)

    with col1:
        generate = st.button(
            "Generate PNGs", disabled=not has_figures, key="analytics_generate_btn"
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
                st.session_state["analytics_ready"] = False
                st.error(f"Export failed: {e}")

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
            key="analytics_download_btn",
        )


# ── Section renderers ─────────────────────────────────────────────────────────


def render_top_bottom(
    metadata: dict,
    code_map: dict[str, str],
    analytics_cfg: dict,
    analytics_data,
    fetch_fn: Callable,
) -> None:
    st.markdown("### Top / Bottom Countries by GDP")
    min_y, max_y = _year_bounds(metadata)

    col1, col2, col3 = st.columns(3)
    with col1:
        continent = _continent_picker(
            "tb_continent",
            metadata,
            default=_cfg_str(analytics_cfg, "continent", _FB_CONTINENT),
        )
    with col2:
        year = st.number_input(
            "Year",
            min_value=min_y,
            max_value=max_y,
            value=_cfg_year(
                analytics_cfg, "defaultYear", _FB_DEFAULT_YEAR, min_y, max_y
            ),
            key="tb_year",
        )
    with col3:
        n = st.slider(
            "Top / Bottom N",
            5,
            30,
            value=_cfg_int(analytics_cfg, "topN", _FB_TOP_N),
            key="tb_n",
        )

    top_params = {"continent": continent, "year": int(year), "n": n}
    bottom_params = {"continent": continent, "year": int(year), "n": n}

    df_top = _maybe_refetch(_S_TOP, top_params, analytics_data, fetch_fn)
    df_bot = _maybe_refetch(_S_BOTTOM, bottom_params, analytics_data, fetch_fn)

    st.markdown("#### Top Countries")
    if df_top.empty:
        _show_error(_S_TOP)
    else:
        df_top = ac.apply_country_codes(df_top, code_map)
        col_chart, col_table = st.columns([2, 1])
        with col_chart:
            fig = ac.top_bottom_bar(df_top, f"Top {n} — {continent} {year}")
            st.plotly_chart(fig, width="stretch")
            _register(f"top_{n}_{continent}_{year}", fig)
        with col_table:
            st.caption("Code → Country")
            _code_table(df_top, "gdp", "GDP")

    st.markdown("#### Bottom Countries")
    if df_bot.empty:
        _show_error(_S_BOTTOM)
    else:
        df_bot = ac.apply_country_codes(df_bot, code_map)
        col_chart, col_table = st.columns([2, 1])
        with col_chart:
            fig = ac.top_bottom_bar(df_bot, f"Bottom {n} — {continent} {year}")
            st.plotly_chart(fig, width="stretch")
            _register(f"bottom_{n}_{continent}_{year}", fig)
        with col_table:
            st.caption("Code → Country")
            _code_table(df_bot, "gdp", "GDP", ascending=True)


def render_growth_rate(
    metadata: dict,
    code_map: dict[str, str],
    analytics_cfg: dict,
    analytics_data,
    fetch_fn: Callable,
) -> None:
    st.markdown("### GDP Growth Rate by Country")
    min_y, max_y = _year_bounds(metadata)

    col1, col2, col3 = st.columns(3)
    with col1:
        continent = _continent_picker(
            "gr_continent",
            metadata,
            default=_cfg_str(analytics_cfg, "continent", _FB_CONTINENT),
        )
    with col2:
        start = st.number_input(
            "Start Year",
            min_value=min_y,
            max_value=max_y,
            value=_cfg_year(analytics_cfg, "startYear", _FB_START_YEAR, min_y, max_y),
            key="gr_start",
        )
    with col3:
        end = st.number_input(
            "End Year",
            min_value=min_y,
            max_value=max_y,
            value=_cfg_year(analytics_cfg, "endYear", _FB_END_YEAR, min_y, max_y),
            key="gr_end",
        )

    params = {"continent": continent, "startYear": int(start), "endYear": int(end)}
    df = _maybe_refetch(_S_GROWTH, params, analytics_data, fetch_fn)

    if df.empty:
        _show_error(_S_GROWTH)
        return

    title = f"GDP Growth Rate — {continent} ({start}–{end})"

    fig_line = ac.growth_rate_line(df, f"Avg Growth Rate — {continent}")
    st.plotly_chart(fig_line, width="stretch")
    _register(f"growth_rate_line_{continent}", fig_line)

    df_coded = ac.apply_country_codes(df, code_map)
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        fig_heat = ac.growth_rate_heatmap(df_coded, title)
        st.plotly_chart(fig_heat, width="stretch")
        _register(f"growth_rate_heatmap_{continent}", fig_heat)
    with col_table:
        st.caption("Code → Country")
        df_avg = (
            df_coded.groupby(["country", "country_name"], as_index=False)[
                "growth_rate_pct"
            ]
            .mean()
            .rename(columns={"growth_rate_pct": "avg_growth_pct"})
        )
        _code_table(df_avg, "avg_growth_pct", "Avg Growth %")


def render_avg_gdp_continent(
    metadata: dict,
    analytics_cfg: dict,
    analytics_data,
    fetch_fn: Callable,
) -> None:
    st.markdown("### Average GDP by Continent")
    min_y, max_y = _year_bounds(metadata)
    start, end = _year_range_inputs(
        "avg_cont",
        metadata,
        default_start=_cfg_year(
            analytics_cfg, "startYear", _FB_START_YEAR, min_y, max_y
        ),
        default_end=_cfg_year(analytics_cfg, "endYear", _FB_END_YEAR, min_y, max_y),
    )

    params = {"startYear": start, "endYear": end}
    df = _maybe_refetch(_S_AVG_CONT, params, analytics_data, fetch_fn)

    if df.empty:
        _show_error(_S_AVG_CONT)
        return

    fig = ac.avg_gdp_continent_bar(df)
    st.plotly_chart(fig, width="stretch")
    _register(f"avg_gdp_continent_{start}_{end}", fig)


def render_global_trend(
    metadata: dict,
    analytics_cfg: dict,
    analytics_data,
    fetch_fn: Callable,
) -> None:
    st.markdown("### Total Global GDP Trend")
    min_y, max_y = _year_bounds(metadata)
    start, end = _year_range_inputs(
        "global_trend",
        metadata,
        default_start=_cfg_year(
            analytics_cfg, "startYear", _FB_START_YEAR, min_y, max_y
        ),
        default_end=_cfg_year(analytics_cfg, "endYear", _FB_END_YEAR, min_y, max_y),
    )

    params = {"startYear": start, "endYear": end}
    df = _maybe_refetch(_S_GLOBAL, params, analytics_data, fetch_fn)

    if df.empty:
        _show_error(_S_GLOBAL)
        return

    fig = ac.global_gdp_trend_line(df)
    st.plotly_chart(fig, width="stretch")
    _register(f"global_gdp_trend_{start}_{end}", fig)


def render_fastest_continent(
    metadata: dict,
    analytics_cfg: dict,
    analytics_data,
    fetch_fn: Callable,
) -> None:
    st.markdown("### Fastest Growing Continent")
    min_y, max_y = _year_bounds(metadata)
    start, end = _year_range_inputs(
        "fastest_cont",
        metadata,
        default_start=_cfg_year(
            analytics_cfg, "startYear", _FB_START_YEAR, min_y, max_y
        ),
        default_end=_cfg_year(analytics_cfg, "endYear", _FB_END_YEAR, min_y, max_y),
    )

    params = {"startYear": start, "endYear": end}
    df = _maybe_refetch(_S_FASTEST, params, analytics_data, fetch_fn)

    if df.empty:
        _show_error(_S_FASTEST)
        return

    fig = ac.fastest_continent_bar(df)
    st.plotly_chart(fig, width="stretch")
    _register(f"fastest_continent_{start}_{end}", fig)


def render_consistent_decline(
    metadata: dict,
    code_map: dict[str, str],
    analytics_cfg: dict,
    analytics_data,
    fetch_fn: Callable,
) -> None:
    st.markdown("### Countries with Consistent GDP Decline")
    min_y, max_y = _year_bounds(metadata)

    col1, col2 = st.columns(2)
    with col1:
        x_years = st.slider(
            "Consecutive Years",
            2,
            10,
            value=_cfg_int(analytics_cfg, "consecutiveYears", _FB_CONSEC_YEARS),
            key="decline_years",
        )
    with col2:
        ref_year = st.number_input(
            "Reference Year",
            min_value=min_y,
            max_value=max_y,
            value=_cfg_year(
                analytics_cfg, "referenceYear", _FB_REFERENCE_YEAR, min_y, max_y
            ),
            key="decline_ref",
        )

    params = {"consecutiveYears": x_years, "referenceYear": int(ref_year)}
    df = _maybe_refetch(_S_DECLINE, params, analytics_data, fetch_fn)

    if df.empty:
        _show_error(_S_DECLINE)
        return

    st.caption(
        f"{len(df)} countries declined every year "
        f"for {x_years} consecutive years up to {ref_year}"
    )

    df_coded = ac.apply_country_codes(df, code_map)
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        fig = ac.consistent_decline_bar(df_coded)
        st.plotly_chart(fig, width="stretch")
        _register(f"consistent_decline_{x_years}yr_{ref_year}", fig)
    with col_table:
        st.caption("Code → Country")
        _code_table(df_coded, "avg_decline_pct", "Avg Decline %")


def render_continent_share(
    metadata: dict,
    analytics_cfg: dict,
    analytics_data,
    fetch_fn: Callable,
) -> None:
    st.markdown("### Continent Share of Global GDP")
    min_y, max_y = _year_bounds(metadata)
    start, end = _year_range_inputs(
        "share",
        metadata,
        default_start=_cfg_year(
            analytics_cfg, "startYear", _FB_START_YEAR, min_y, max_y
        ),
        default_end=_cfg_year(analytics_cfg, "endYear", _FB_END_YEAR, min_y, max_y),
    )

    params = {"startYear": start, "endYear": end}
    df = _maybe_refetch(_S_SHARE, params, analytics_data, fetch_fn)

    if df.empty:
        _show_error(_S_SHARE)
        return

    fig_pie = ac.continent_share_pie(df)
    st.plotly_chart(fig_pie, width="stretch")
    _register(f"continent_share_pie_{start}_{end}", fig_pie)

    fig_bar = ac.continent_share_bar(df)
    st.plotly_chart(fig_bar, width="stretch")
    _register(f"continent_share_bar_{start}_{end}", fig_bar)


# ── Main entry ────────────────────────────────────────────────────────────────


def render_analytics_tab(
    metadata: dict,
    code_map: dict[str, str],
    analytics_cfg: dict,
    analytics_data,
    fetch_fn: Callable[[str, dict], pd.DataFrame],
) -> None:
    """
    Main entry point for the Analytics tab.

    Parameters
    ----------
    metadata : dict
        Regions, year bounds, countries — from CoreAPIClient.get_metadata().
    code_map : dict[str, str]
        Country name → ISO code mapping built in streamlit_entry.boot().
    analytics_cfg : dict
        Sanitized default values from handle.get_analytics_config().
    analytics_data : AnalyticsData
        Pre-fetched DataFrames for all sections, held in session state.
    fetch_fn : Callable[[str, dict], pd.DataFrame]
        Injected re-fetch callable from streamlit_entry.make_fetch_fn().
        Views call this when widget values change; never import HTTP clients directly.
    """
    st.session_state["analytics_figures"] = []

    st.title("GDP Analytics")
    st.markdown("---")

    render_top_bottom(metadata, code_map, analytics_cfg, analytics_data, fetch_fn)
    st.markdown("---")
    render_growth_rate(metadata, code_map, analytics_cfg, analytics_data, fetch_fn)
    st.markdown("---")
    render_avg_gdp_continent(metadata, analytics_cfg, analytics_data, fetch_fn)
    st.markdown("---")
    render_global_trend(metadata, analytics_cfg, analytics_data, fetch_fn)
    st.markdown("---")
    render_fastest_continent(metadata, analytics_cfg, analytics_data, fetch_fn)
    st.markdown("---")
    render_consistent_decline(
        metadata, code_map, analytics_cfg, analytics_data, fetch_fn
    )
    st.markdown("---")
    render_continent_share(metadata, analytics_cfg, analytics_data, fetch_fn)
    st.markdown("---")
    render_analytics_export()
