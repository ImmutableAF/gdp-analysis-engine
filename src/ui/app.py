import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.append(str(Path(__file__).parents[2]))

import streamlit as st
from main import initialize_system
from src.core import pipeline, handle
from src.core.data_cleaning import clean_gdp_data
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
    df = clean_gdp_data(raw_df, fill_method="ffill")
    df = pipeline.transform(raw_df)

    regions = sorted(handle.get_all_regions(df))
    countries = sorted(handle.get_all_countries(df))
    min_year, max_year = handle.get_year_range(df)

    return df, config, regions, countries, min_year, max_year


def build_sidebar(regions, countries, min_year, max_year, initial_config):
    st.sidebar.title("Filters")

    initial_region = initial_config.region if initial_config.region else "All"
    initial_start = initial_config.startYear if initial_config.startYear else min_year
    initial_end = initial_config.endYear if initial_config.endYear else max_year
    initial_op = initial_config.operation if initial_config.operation else "avg"

    op_options = ["Average", "Sum"]
    initial_op_label = "Average" if initial_op.lower() in ["avg", "average"] else "Sum"
    initial_op_index = op_options.index(initial_op_label)

    region_options = ["All"] + regions
    initial_region_index = region_options.index(initial_region) if initial_region in region_options else 0

    region = st.sidebar.selectbox("Region", region_options, index=initial_region_index)
    selected_region = None if region == "All" else region

    start_year, end_year = st.sidebar.slider(
        "Year range",
        min_year,
        max_year,
        (initial_start, initial_end),
    )

    op_label = st.sidebar.selectbox("Aggregation", op_options, index=initial_op_index)
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

    # global figure registry
    if "figures" not in st.session_state:
        st.session_state.figures = []

    st.session_state.figures.clear()

    filters = build_sidebar(regions, countries, min_year, max_year, config)

    # Toggle: Show Top 10 or All Countries
    show_all_countries = st.sidebar.checkbox("Show All Countries", value=False)
    top_n_countries = None if show_all_countries else 10

    st.title("GDP Analytics Dashboard")
    st.markdown("---")

    views.render_region_analysis(
        df=df,
        region=filters["region"],
        start_year=filters["start_year"],
        end_year=filters["end_year"],
        stat_operation=filters["stat_operation"],
        top_n=top_n_countries
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
