"""
View rendering layer
Pure UI composition
No export or IO logic
"""

import streamlit as st
import pandas as pd
from src.core import pipeline
from . import charts
from . import exports


# ---------- internal helpers ----------

def _register_figure(name: str, fig):
    st.session_state.figures.append((name, fig))


def _render_aggregate_metrics(df: pd.DataFrame, scope: str):
    total_gdp = df["Value"].sum()
    avg_gdp = df["Value"].mean()
    rows = len(df)

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Total GDP ({scope})", f"{total_gdp:,.0f}")
    c2.metric("Average GDP", f"{avg_gdp:,.0f}")
    c3.metric("Data Entries", rows)


def _render_filtered_data_preview(df: pd.DataFrame):
    with st.expander("View Filtered Data (Raw CSV-style)"):
        st.dataframe(
            df.sort_values(["Year", "Country Code"]),
            use_container_width=True,
            hide_index=True,
        )


# ---------- views ----------

def render_region_analysis(df, region, start_year, end_year, stat_operation):
    st.markdown("## Region Analysis")

    section_df = pipeline.apply_filters(
        df,
        region=region,
        start_year=start_year,
        end_year=end_year,
    )

    scope = region.title() if region else "All Regions"
    _render_aggregate_metrics(section_df, scope)
    st.markdown("---")

    if region:
        agg = pipeline.aggregate_by_country_code(section_df, stat_operation)

        fig = charts.country_bar(agg, f" — {scope}")
        st.plotly_chart(fig, use_container_width=True)
        _register_figure("country_bar", fig)

        fig = charts.country_treemap(agg)
        st.plotly_chart(fig, use_container_width=True)
        _register_figure("country_treemap", fig)
    else:
        agg = pipeline.aggregate_by_region(section_df, stat_operation)

        fig = charts.region_bar(agg)
        st.plotly_chart(fig, use_container_width=True)
        _register_figure("region_bar", fig)


def render_year_analysis(df, region, start_year, end_year):
    section_df = pipeline.apply_filters(
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
    st.markdown("## Country Analysis")

    section_df = pipeline.apply_filters(
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
    st.markdown("## Export")

    export_df = pipeline.apply_filters(
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