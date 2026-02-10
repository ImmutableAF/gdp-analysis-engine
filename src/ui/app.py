"""
Streamlit Dashboard Entry Point
================================

Main Streamlit application for interactive GDP data visualization and analysis.
Provides sidebar filters, multiple analysis views, and export capabilities.

Application Structure:
1. Boot: Initialize system, load data, extract metadata (cached)
2. Sidebar: Build interactive filters (region, year range, aggregation, country)
3. Views: Render analysis sections (region, year, country, export)
4. State: Manage figure registry for chart exports

Functions
---------
boot()
    Initialize system and prepare metadata (cached resource)
build_sidebar(regions, countries, min_year, max_year, initial_config)
    Build interactive sidebar with filters
main()
    Main application orchestration

See Also
--------
views : View rendering functions
charts : Chart generation
exports : Export utilities

Notes
-----
Uses st.cache_resource for boot() to prevent reloading on every interaction.
Session state manages figure registry for multi-chart PNG export.
Sidebar width set to 250px via custom CSS.

Page Config:
- Title: "GDP Analytics Dashboard"
- Icon: custom file
- Sidebar: 250px width

Examples
--------
Run application:
$ streamlit run src/ui/app.py

Access at http://localhost:8501
"""

import sys
from pathlib import Path
# Add root directory to sys.path
sys.path.append(str(Path(__file__).parents[2]))

import streamlit as st
from main import initialize_system
from src.core import pipeline, metadata
from src.core.data_cleaning import clean_gdp_data
from src.ui import views

from src.ui.style import load_css
load_css("src/ui/layout.css")

st.set_page_config(
    page_title="GDP Analytics Dashboard",
    page_icon=str(Path(__file__).parent.parent.parent / "assets" / "app.ico"),
)

@st.cache_resource
def boot():
    """
    Initialize system and prepare metadata.
    
    Executes complete initialization workflow: system init → data cleaning →
    transformation → metadata extraction. Cached as resource to prevent
    reloading on UI interactions.
    
    Returns
    -------
    tuple
        (df, config, regions, countries, min_year, max_year)
        - df: Transformed long-format DataFrame
        - config: QueryConfig from initialization
        - regions: Sorted list of region names
        - countries: Sorted list of country names
        - min_year: Minimum year in dataset
        - max_year: Maximum year in dataset
    
    Notes
    -----
    Cached via st.cache_resource - runs once per session. Data loading and
    transformation expensive, so caching critical for performance.
    
    Uses main.initialize_system() for config loading and data ingestion.
    
    Examples
    --------
    >>> df, config, regions, countries, min_yr, max_yr = boot()
    >>> print(len(regions))
    6
    """
    raw_df, config = initialize_system()
    df = clean_gdp_data(raw_df, fill_method="ffill")
    df = pipeline.transform(raw_df)

    regions = sorted(metadata.get_all_regions(df))
    countries = sorted(metadata.get_all_countries(df))
    min_year, max_year = metadata.get_year_range(df)

    return df, config, regions, countries, min_year, max_year


def build_sidebar(regions, countries, min_year, max_year, initial_config):
    """
    Build interactive sidebar with filter controls.
    
    Creates sidebar widgets for region selection, year range, aggregation
    operation, and optional country analysis toggle.
    
    Parameters
    ----------
    regions : list[str]
        Available region names
    countries : list[str]
        Available country names
    min_year : int
        Dataset minimum year
    max_year : int
        Dataset maximum year
    initial_config : QueryConfig
        Initial configuration for default values
    
    Returns
    -------
    dict
        Filter state dictionary with keys:
        - region: Selected region (None for "All")
        - start_year: Start year from slider
        - end_year: End year from slider
        - stat_operation: "avg" or "sum"
        - show_country: Boolean for country analysis
        - country: Selected country (None if not enabled)
    
    Notes
    -----
    Uses initial_config to set default widget values. "All" option maps to None
    for filter functions.
    
    Examples
    --------
    >>> filters = build_sidebar(regions, countries, 1960, 2020, config)
    >>> print(filters["region"])
    'Asia'
    >>> print(filters["stat_operation"])
    'sum'
    """
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
    """
    Main application orchestration.
    
    Workflow:
    1. Boot system (cached)
    2. Initialize figure registry in session state
    3. Build sidebar filters
    4. Render analysis views (region, year, country, export)
    
    Notes
    -----
    Figure registry cleared on each run to prevent accumulation across reruns.
    Top N countries toggle (10 vs all) in sidebar affects region analysis.
    Country analysis view only shown if enabled and country selected.
    
    View rendering order:
    - Region Analysis (always)
    - Year Analysis (always)
    - Country Analysis (conditional)
    - Export (always)
    """
    df, config, regions, countries, min_year, max_year = boot()

    if "query_config" not in st.session_state:
        st.session_state.query_config = config

    # global figure registry
    if "figures" not in st.session_state:
        st.session_state.figures = []

    st.session_state.figures.clear()

    filters = build_sidebar(
        regions,
        countries,
        min_year,
        max_year,
        st.session_state.query_config
    )

    show_all_countries = st.sidebar.checkbox("Show All Countries", value=False)
    top_n_countries = None if show_all_countries else 10

    if st.sidebar.button("Re-run Main Query"):
        _, new_query = initialize_system()
        st.session_state.query_config = new_query
        st.rerun()

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