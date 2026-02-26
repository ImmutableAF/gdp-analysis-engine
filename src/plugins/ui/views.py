"""
View Rendering Layer
====================

Pure UI composition functions for Streamlit dashboard. Handles view rendering,
metric displays, and figure registration. No export or I/O logic.

View Types:
- Region Analysis: Continental or global GDP analysis with country breakdowns
- Year Analysis: Temporal trends and growth rates
- Country Analysis: Individual country GDP over time
- Export View: Data and chart export controls

Functions
---------
render_region_analysis(df, region, start_year, end_year, stat_operation, top_n)
    Render regional GDP analysis view
render_year_analysis(df, region, start_year, end_year)
    Render temporal analysis view
render_country_analysis(df, country, start_year, end_year)
    Render country-specific view
render_exports(df, region, country, start_year, end_year)
    Render export controls view

See Also
--------
charts : Chart generation functions
exports : Export utility functions
run_pipeline : Data filtering and aggregation

Notes
-----
All render functions are pure UI - they compose charts and metrics but don't
handle file I/O. Figures registered via st.session_state.figures for export.

Metrics display uses custom gradient cards with CUSTOM_PALETTE colors.

Examples
--------
In Streamlit app:
>>> render_region_analysis(df, "Asia", 2000, 2020, "sum", top_n=10)
>>> render_year_analysis(df, "Europe", 1990, 2020)
"""

import streamlit as st
import pandas as pd
from . import charts
from . import exports
from src.core import run_pipeline
from .palette import CUSTOM_PALETTE


# ---------- internal helpers ----------


def _register_figure(name: str, fig):
    """
    Register figure for export.

    Appends (name, figure) tuple to st.session_state.figures list.

    Parameters
    ----------
    name : str
        Figure identifier for export filename
    fig : go.Figure
        Plotly figure object
    """
    st.session_state.figures.append((name, fig))


def _render_aggregate_metrics(df: pd.DataFrame, scope: str):
    """
    Render aggregate metrics card with gradient styling.

    Displays total GDP, average GDP, and data entry count in styled card
    using CUSTOM_PALETTE gradient.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered DataFrame with Value column
    scope : str
        Scope label (region/country name or "All Regions")

    Notes
    -----
    Value formatting:
    - >= 1T: Displays as $X.XXT
    - >= 1B: Displays as $X.XXB
    - >= 1M: Displays as $X.XXM
    - < 1M: Displays with comma separators

    Uses custom CSS with gradient background and glassmorphism effects.
    """

    total_gdp = df["Value"].sum()
    avg_gdp = df["Value"].mean()
    rows = len(df)

    # Get gradient colors from palette
    color1 = CUSTOM_PALETTE[0]  # #FF5555
    color2 = CUSTOM_PALETTE[-1]  # #A3D78A

    # CSS with subtle gradient
    st.markdown(
        f"""
        <style>
        .gdp-card {{
            background: linear-gradient(135deg, {color1}80 0%, {color2}80 100%);
            border-radius: 16px;
            padding: 30px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }}
        .subtitle {{
            font-size: 12px;
            opacity: 0.8;
            margin-bottom: 5px;
            padding-left: 17px;
        }}
        .gdp-breakdown {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .breakdown-item {{
            flex: 1;
            min-width: 140px;
            background: rgba(255, 255, 255, 0.15);
            padding: 15px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .breakdown-value {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .breakdown-label {{
            font-size: 12px;
            opacity: 0.85;
            margin-top: 4px;
        }}
        </style>
    """,
        unsafe_allow_html=True,
    )

    def format_val(val):
        if val >= 1e12:
            return f"${val/1e12:.2f}T"
        if val >= 1e9:
            return f"${val/1e9:.2f}B"
        if val >= 1e6:
            return f"${val/1e6:.2f}M"
        return f"${val:,.0f}"

    total_display = format_val(total_gdp)
    avg_display = format_val(avg_gdp)

    st.markdown(
        f"""
        <div class="gdp-card">
            <div class="subtitle"><h1>{scope}</h1></div>
            <div class="gdp-breakdown">
                <div class="breakdown-item">
                    <div class="breakdown-value">{total_display}</div>
                    <div class="breakdown-label">Total GDP</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-value">{avg_display}</div>
                    <div class="breakdown-label">Average GDP</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-value">{rows:,}</div>
                    <div class="breakdown-label">Data Entries</div>
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


def _render_filtered_data_preview(df: pd.DataFrame):
    """
    Render expandable DataFrame preview.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered data to display

    Notes
    -----
    Data sorted by Year and Country Code before display.
    """
    with st.expander("View Filtered Data (Raw CSV-style)"):
        st.dataframe(
            df.sort_values(["Year", "Country Code"]),
            use_container_width=True,
            hide_index=True,
        )


# ---------- views ----------


def render_region_analysis(df, region, start_year, end_year, stat_operation, top_n):
    """
    Render regional GDP analysis view.

    Shows aggregate metrics and either country breakdown (if region selected)
    or continental comparison (if all regions).

    Parameters
    ----------
    df : pd.DataFrame
        Transformed long-format DataFrame
    region : str or None
        Selected region, None for all regions
    start_year : int or None
        Start year filter
    end_year : int or None
        End year filter
    stat_operation : str
        Aggregation operation ("sum" or "avg")
    top_n : int
        Number of top countries to show

    Notes
    -----
    Renders: Metrics card → Country bar chart → Country treemap (if region)
             OR Metrics card → Region bar chart (if all regions)
    """
    st.markdown("## Region Analysis")

    section_df = run_pipeline.apply_filters(
        df,
        region=region,
        start_year=start_year,
        end_year=end_year,
    )

    scope = region.title() if region else "All Regions"
    _render_aggregate_metrics(section_df, scope)
    st.markdown("---")

    if region:
        agg = run_pipeline.aggregate_by_country_code(section_df, stat_operation)

        fig = charts.country_bar(agg, f" — {scope}", top_n)
        st.plotly_chart(fig, use_container_width=True)
        _register_figure("country_bar", fig)

        fig = charts.country_treemap(agg, top_n)
        st.plotly_chart(fig, use_container_width=True)
        _register_figure("country_treemap", fig)
    else:
        agg = run_pipeline.aggregate_by_region(section_df, stat_operation)

        fig = charts.region_bar(agg)
        st.plotly_chart(fig, use_container_width=True)
        _register_figure("region_bar", fig)


def render_year_analysis(df, region, start_year, end_year):
    """
    Render temporal GDP analysis view.

    Shows GDP trends and growth rates over time.

    Parameters
    ----------
    df : pd.DataFrame
        Transformed long-format DataFrame
    region : str or None
        Region filter
    start_year : int or None
        Start year filter
    end_year : int or None
        End year filter

    Notes
    -----
    Requires at least 2 years of data. Renders: Scatter with trendline →
    Growth rate bar chart (if sufficient data).
    """
    section_df = run_pipeline.apply_filters(
        df,
        region=region,
        start_year=start_year,
        end_year=end_year,
    )

    if section_df["Year"].nunique() < 2:
        st.info("Select at least two years for temporal analysis.")
        return

    st.markdown("## Year Analysis")
    title = f" — {region.title()}" if region else " — All Regions"

    fig = charts.year_scatter(section_df, title, interpolate=True)
    st.plotly_chart(fig, use_container_width=True)
    _register_figure("year_scatter", fig)

    growth = charts.growth_rate(section_df, title, interpolate=True)
    if growth:
        st.plotly_chart(growth, use_container_width=True)
        _register_figure("growth_rate", growth)


def render_country_analysis(df, country, start_year, end_year):
    """
    Render country-specific GDP analysis view.

    Shows metrics and temporal trends for a single country.

    Parameters
    ----------
    df : pd.DataFrame
        Transformed long-format DataFrame
    country : str
        Country name filter
    start_year : int or None
        Start year filter
    end_year : int or None
        End year filter

    Notes
    -----
    Renders: Metrics card → Line chart → Bar chart (both with interpolation).
    """
    st.markdown("## Country Analysis")

    section_df = run_pipeline.apply_filters(
        df,
        country=country,
        start_year=start_year,
        end_year=end_year,
    )

    _render_aggregate_metrics(section_df, country.title())
    st.markdown("---")

    fig = charts.year_line(section_df, f" — {country.title()}", interpolate=True)
    st.plotly_chart(fig, use_container_width=True)
    _register_figure("country_year_line", fig)

    fig = charts.year_bar(section_df, f" — {country.title()}", interpolate=True)
    st.plotly_chart(fig, use_container_width=True)
    _register_figure("country_year_bar", fig)


def render_exports(df, region, country, start_year, end_year):
    """
    Render export controls view.

    Shows filtered data preview and export buttons for CSV and PNG charts.

    Parameters
    ----------
    df : pd.DataFrame
        Transformed long-format DataFrame
    region : str or None
        Region filter
    country : str or None
        Country filter
    start_year : int or None
        Start year filter
    end_year : int or None
        End year filter

    Notes
    -----
    Layout: Data preview expander → CSV download | PNG export buttons (in columns).
    """
    st.markdown("## Export")

    export_df = run_pipeline.apply_filters(
        df,
        region=region,
        country=country,
        start_year=start_year,
        end_year=end_year,
    )

    _render_filtered_data_preview(export_df)

    col1, spacer, col2 = st.columns([2, 6, 4])

    with col1:
        exports.export_filtered_csv(export_df)

    with col2:
        exports.export_charts_as_png()
