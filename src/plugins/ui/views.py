import streamlit as st
import pandas as pd
from . import charts
from . import exports
from .palette import CUSTOM_PALETTE


# ---------- internal helpers ----------


def _register_figure(name: str, fig):
    st.session_state.figures.append((name, fig))


def _render_aggregate_metrics(df: pd.DataFrame, scope: str):
    total_gdp = df["Value"].sum()
    avg_gdp = df["Value"].mean()
    rows = len(df)

    color1 = CUSTOM_PALETTE[0]
    color2 = CUSTOM_PALETTE[-1]

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

    st.markdown(
        f"""
        <div class="gdp-card">
            <div class="subtitle"><h1>{scope}</h1></div>
            <div class="gdp-breakdown">
                <div class="breakdown-item">
                    <div class="breakdown-value">{format_val(total_gdp)}</div>
                    <div class="breakdown-label">Total GDP</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-value">{format_val(avg_gdp)}</div>
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
    with st.expander("View Filtered Data (Raw CSV-style)"):
        st.dataframe(
            df.sort_values(["Year", "Country Code"]),
            width="stretch",
            hide_index=True,
        )


# ---------- views — pure display, receive pre-fetched dfs ----------


def render_region_analysis(region_df: pd.DataFrame, region, stat_operation, top_n):
    st.markdown("## Region Analysis")
    scope = region.title() if region else "All Regions"
    _render_aggregate_metrics(region_df, scope)
    st.markdown("---")

    if region:
        agg = (
            region_df.groupby("Country Code", as_index=False)["Value"].sum()
            if stat_operation == "sum"
            else region_df.groupby("Country Code", as_index=False)["Value"].mean()
        )
        fig = charts.country_bar(agg, f" — {scope}", top_n)
        st.plotly_chart(fig, width="stretch", key="country_bar")
        _register_figure("country_bar", fig)

        fig = charts.country_treemap(agg, top_n)
        st.plotly_chart(fig, width="stretch", key="country_treemap")
        _register_figure("country_treemap", fig)
    else:
        agg = (
            region_df.groupby("Continent", as_index=False)["Value"].sum()
            if stat_operation == "sum"
            else region_df.groupby("Continent", as_index=False)["Value"].mean()
        )
        fig = charts.region_bar(agg)
        st.plotly_chart(fig, width="stretch", key="region_bar")
        _register_figure("region_bar", fig)


def render_year_analysis(region_df: pd.DataFrame, region):
    if region_df["Year"].nunique() < 2:
        st.info("Select at least two years for temporal analysis.")
        return

    st.markdown("## Year Analysis")
    title = f" — {region.title()}" if region else " — All Regions"

    fig = charts.year_scatter(region_df, title, interpolate=True)
    st.plotly_chart(fig, width="stretch", key="year_scatter")
    _register_figure("year_scatter", fig)

    growth = charts.growth_rate(region_df, title, interpolate=True)
    if growth:
        st.plotly_chart(growth, width="stretch", key="growth_rate")
        _register_figure("growth_rate", growth)


def render_country_analysis(country_df: pd.DataFrame, country):
    st.markdown("## Country Analysis")
    _render_aggregate_metrics(country_df, country.title())
    st.markdown("---")

    fig = charts.year_line(country_df, f" — {country.title()}", interpolate=True)
    st.plotly_chart(fig, width="stretch", key="country_year_line")
    _register_figure("country_year_line", fig)

    fig = charts.year_bar(country_df, f" — {country.title()}", interpolate=True)
    st.plotly_chart(fig, width="stretch", key="country_year_bar")
    _register_figure("country_year_bar", fig)


def render_exports(export_df: pd.DataFrame):
    st.markdown("## Export")
    _render_filtered_data_preview(export_df)

    col1, spacer, col2 = st.columns([2, 6, 4])
    with col1:
        exports.export_filtered_csv(export_df)
    with col2:
        exports.export_charts_as_png()


def build_sidebar(regions, countries, min_year, max_year, initial_config=None) -> dict:
    st.sidebar.title("Filters")

    # ── resolve initial values from config ──
    initial_region = initial_config.region if (initial_config and initial_config.region) else "All"
    initial_start  = initial_config.startYear if (initial_config and initial_config.startYear) else min_year
    initial_end    = initial_config.endYear if (initial_config and initial_config.endYear) else max_year
    initial_op     = initial_config.operation if (initial_config and initial_config.operation) else "avg"
    initial_show_country = bool(initial_config and initial_config.country)
    initial_country = initial_config.country if (initial_config and initial_config.country) else None

    op_options = ["Average", "Sum"]
    initial_op_label = "Average" if initial_op.lower() in ["avg", "average"] else "Sum"

    region_options = ["All"] + regions

    # ── widgets with explicit keys so _reset_sidebar_widgets can override them ──
    region = st.sidebar.selectbox(
        "Region", region_options,
        index=region_options.index(initial_region) if initial_region in region_options else 0,
        key="sb_region",
    )
    selected_region = None if region == "All" else region

    start_year, end_year = st.sidebar.slider(
        "Year range", min_year, max_year, (initial_start, initial_end),
        key="sb_year_range",
    )

    op_label = st.sidebar.selectbox(
        "Aggregation", op_options,
        index=op_options.index(initial_op_label),
        key="sb_operation",
    )
    stat_operation = "avg" if op_label == "Average" else "sum"

    show_country = st.sidebar.checkbox(
        "Enable Country Analysis",
        value=initial_show_country,
        key="sb_show_country",
    )

    selected_country = None
    if show_country:
        country_options = ["All"] + countries
        # Default to config country if set, otherwise "All"
        default_country = initial_country if (initial_country and initial_country in countries) else "All"
        country = st.sidebar.selectbox(
            "Country", country_options,
            index=country_options.index(default_country),
            key="sb_country",
        )
        selected_country = None if country == "All" else country

    show_all = st.sidebar.checkbox("Show All Countries", value=False, key="sb_show_all")

    return {
        "region": selected_region,
        "start_year": start_year,
        "end_year": end_year,
        "stat_operation": stat_operation,
        "show_country": show_country,
        "country": selected_country,
        "show_all": show_all,
    }


def render_all_from_df(
    region_df: pd.DataFrame,
    country_df: pd.DataFrame | None,
    filters: dict,
) -> None:
    region = filters["region"]

    render_region_analysis(
        region_df,
        region,
        filters["stat_operation"],
        None if filters["show_all"] else 10,
    )
    render_year_analysis(region_df, region)

    if country_df is not None and filters.get("show_country") and filters.get("country"):
        render_country_analysis(country_df, filters["country"])

    render_exports(region_df)