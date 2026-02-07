"""
GDP Analytics Dashboard
"""

import streamlit as st
from main import initialize_system
from src.core import pipeline, handle
from src.ui import views

st.set_page_config(
    page_title="GDP Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_resource
def boot():
    """Initialize system and prepare metadata"""
    raw_df, config = initialize_system()
    df = pipeline.transform(raw_df)

    regions = sorted(handle.get_all_regions(df))
    countries = sorted(handle.get_all_countries(df))
    min_year, max_year = handle.get_year_range(df)

    return df, config, regions, countries, min_year, max_year


def build_sidebar(regions, countries, min_year, max_year):
    """Render sidebar and return user selections"""
    st.sidebar.title("Filters")

    region = st.sidebar.selectbox("Region", ["All"] + regions)
    selected_region = None if region == "All" else region

    start_year, end_year = st.sidebar.slider(
        "Year range",
        min_year,
        max_year,
        (min_year, max_year),
    )

    op_label = st.sidebar.selectbox("Aggregation", ["Average", "Sum"])
    stat_operation = "avg" if op_label == "Average" else "sum"

    show_country = st.sidebar.checkbox("Enable Country Analysis")
    selected_country = None

    if show_country:
        country = st.sidebar.selectbox("Country", ["All"] + countries)
        selected_country = None if country == "All" else country

    return {
        "region": selected_region,
        "start_year": start_year,
        "end_year": end_year,
        "stat_operation": stat_operation,
        "show_country": show_country,
        "country": selected_country,
    }


def main():
    df, config, regions, countries, min_year, max_year = boot()
    
    filters = build_sidebar(regions, countries, min_year, max_year)

    st.title("GDP Analytics Dashboard")
    st.markdown("---")

    views.render_region_analysis(
        df=df,
        region=filters["region"],
        start_year=filters["start_year"],
        end_year=filters["end_year"],
        stat_operation=filters["stat_operation"],
    )

    views.render_year_analysis(
        df=df,
        region=filters["region"],
        start_year=filters["start_year"],
        end_year=filters["end_year"],
    )

    if filters["show_country"] and filters["country"]:
        views.render_country_analysis(
            df=df,
            country=filters["country"],
            start_year=filters["start_year"],
            end_year=filters["end_year"],
        )

    views.render_exports(
        df=df,
        region=filters["region"],
        country=filters["country"],
        start_year=filters["start_year"],
        end_year=filters["end_year"],
    )


if __name__ == "__main__":
    main()