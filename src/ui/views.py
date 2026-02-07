"""
View rendering layer
NO aggregation logic
NO chart logic
ONLY orchestration
"""

import streamlit as st
import pandas as pd
from src.core import pipeline
from . import charts


# -------------------------
# REGION ANALYSIS
# -------------------------
def render_region_analysis(
    df: pd.DataFrame,
    selected_region: str | None,
    stat_operation: str,
):
    st.markdown("## Region Analysis")

    if selected_region:
        # Countries inside region
        agg = pipeline.aggregate_by_country(df, stat_operation)

        st.plotly_chart(
            charts.country_bar(agg, f" — {selected_region.title()}"),
            use_container_width=True,
        )

        st.plotly_chart(
            charts.country_treemap(agg),
            use_container_width=True,
        )

    else:
        # Compare regions
        agg = pipeline.aggregate_by_region(df, stat_operation)

        st.plotly_chart(
            charts.region_bar(agg),
            use_container_width=True,
        )


# -------------------------
# YEAR ANALYSIS
# -------------------------
def render_year_analysis(
    df: pd.DataFrame,
    selected_region: str | None,
):
    if df["Year"].nunique() < 2:
        st.info("Select a year range for temporal analysis.")
        return

    st.markdown("## Year Analysis")

    title = (
        f" — {selected_region.title()}"
        if selected_region
        else " — All Regions"
    )

    st.plotly_chart(
        charts.year_scatter(df, title, interpolate=True),
        use_container_width=True,
    )

    growth = charts.growth_rate(df, title, interpolate=True)
    if growth:
        st.plotly_chart(growth, use_container_width=True)


# -------------------------
# COUNTRY ANALYSIS
# -------------------------
def render_country_analysis(
    df: pd.DataFrame,
    selected_country: str,
):
    st.markdown("## Country Analysis")

    title = f" — {selected_country.title()}"

    st.plotly_chart(
        charts.year_line(df, title, interpolate=True),
        use_container_width=True,
    )

    st.plotly_chart(
        charts.year_bar(df, title, interpolate=True),
        use_container_width=True,
    )


# -------------------------
# EXPORTS
# -------------------------
def render_exports(df: pd.DataFrame, start: int, end: int):
    st.markdown("## Export")

    csv = df.to_csv(index=False)
    st.download_button(
        "Download CSV",
        csv,
        file_name=f"gdp_{start}_{end}.csv",
        mime="text/csv",
    )
