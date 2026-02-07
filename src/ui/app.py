"""
GDP Analytics Dashboard
Main entry point
"""

import streamlit as st
from main import initialize_system
from src.core import pipeline, handle
from src.ui import views

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="GDP Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

# -------------------------
# BOOT SYSTEM
# -------------------------
@st.cache_resource
def boot():
    raw_df, config = initialize_system()
    df = pipeline.transform(raw_df)

    regions = sorted(handle.get_all_regions(df))
    countries = sorted(handle.get_all_countries(df))
    min_year, max_year = handle.get_year_range(df)

    return df, config, regions, countries, min_year, max_year


df, config, regions, countries, min_year, max_year = boot()

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.title("Filters")

# Region
region = st.sidebar.selectbox(
    "Region",
    ["All"] + regions,
)
selected_region = None if region == "All" else region

# Year range
start_year, end_year = st.sidebar.slider(
    "Year range",
    min_year,
    max_year,
    (min_year, max_year),
)

# Aggregation
op_label = st.sidebar.selectbox(
    "Aggregation",
    ["Average", "Sum"],
)
stat_operation = "avg" if op_label == "Average" else "sum"

# Country section toggle
show_country = st.sidebar.checkbox("Enable Country Analysis")

selected_country = None
if show_country:
    country = st.sidebar.selectbox(
        "Country",
        ["All"] + countries,
    )
    selected_country = None if country == "All" else country

# -------------------------
# FILTER BASE DATA (ONLY ROW FILTERS)
# -------------------------
base_df = df.copy()
base_df = pipeline.filter_by_year(base_df, start_year, end_year)

if selected_region:
    base_df = pipeline.filter_by_region(base_df, selected_region)

if selected_country:
    base_df = pipeline.filter_by_country(base_df, selected_country)

# -------------------------
# MAIN VIEW
# -------------------------
st.title("GDP Analytics Dashboard")
st.markdown("---")

views.render_region_analysis(
    df=base_df,
    selected_region=selected_region,
    stat_operation=stat_operation,
)

views.render_year_analysis(
    df=base_df,
    selected_region=selected_region,
)

if show_country and selected_country:
    views.render_country_analysis(
        df=base_df,
        selected_country=selected_country,
    )

views.render_exports(base_df, start_year, end_year)
