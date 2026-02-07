"""
View rendering layer
Each section creates its own filtered copy
No shared state between sections
"""

import streamlit as st
import pandas as pd
from src.core import pipeline
from . import charts


def render_region_analysis(
    df: pd.DataFrame,
    region: str | None,
    start_year: int,
    end_year: int,
    stat_operation: str,
):
    """
    Region analysis section
    Filters: region (optional), year range
    Ignores: country filter
    """
    st.markdown("## Region Analysis")

    section_df = pipeline.apply_filters(
        df,
        region=region,
        start_year=start_year,
        end_year=end_year,
    )

    if region:
        agg = pipeline.aggregate_by_country(section_df, stat_operation)
        
        st.plotly_chart(
            charts.country_bar(agg, f" — {region.title()}"),
            use_container_width=True,
        )

        st.plotly_chart(
            charts.country_treemap(agg),
            use_container_width=True,
        )
    else:
        agg = pipeline.aggregate_by_region(section_df, stat_operation)
        
        st.plotly_chart(
            charts.region_bar(agg),
            use_container_width=True,
        )


def render_year_analysis(
    df: pd.DataFrame,
    region: str | None,
    start_year: int,
    end_year: int,
):
    """
    Year analysis section
    Filters: region (optional), year range
    Ignores: country filter
    """
    section_df = pipeline.apply_filters(
        df,
        region=region,
        start_year=start_year,
        end_year=end_year,
    )

    if section_df["Year"].nunique() < 2:
        st.info("Select a year range with at least 2 years for temporal analysis.")
        return

    st.markdown("## Year Analysis")

    title = f" — {region.title()}" if region else " — All Regions"

    st.plotly_chart(
        charts.year_scatter(section_df, title, interpolate=True),
        use_container_width=True,
    )

    growth = charts.growth_rate(section_df, title, interpolate=True)
    if growth:
        st.plotly_chart(growth, use_container_width=True)


def render_country_analysis(
    df: pd.DataFrame,
    country: str,
    start_year: int,
    end_year: int,
):
    """
    Country analysis section
    Filters: country (required), year range
    Ignores: region filter
    """
    st.markdown("## Country Analysis")

    section_df = pipeline.apply_filters(
        df,
        country=country,
        start_year=start_year,
        end_year=end_year,
    )

    title = f" — {country.title()}"

    st.plotly_chart(
        charts.year_line(section_df, title, interpolate=True),
        use_container_width=True,
    )

    st.plotly_chart(
        charts.year_bar(section_df, title, interpolate=True),
        use_container_width=True,
    )


def render_exports(
    df: pd.DataFrame,
    region: str | None,
    country: str | None,
    start_year: int,
    end_year: int,
):
    """Export section with all user filters applied"""
    st.markdown("## Export")

    export_df = pipeline.apply_filters(
        df,
        region=region,
        country=country,
        start_year=start_year,
        end_year=end_year,
    )

    csv = export_df.to_csv(index=False)
    
    filename_parts = ["gdp", str(start_year), str(end_year)]
    if region:
        filename_parts.append(region.lower().replace(" ", "_"))
    if country:
        filename_parts.append(country.lower().replace(" ", "_"))
    
    filename = "_".join(filename_parts) + ".csv"

    st.download_button(
        "Download CSV",
        csv,
        file_name=filename,
        mime="text/csv",
    )