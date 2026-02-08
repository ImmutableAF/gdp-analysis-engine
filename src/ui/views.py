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
    from .palette import CUSTOM_PALETTE
    
    total_gdp = df["Value"].sum()
    avg_gdp = df["Value"].mean()
    rows = len(df)
    
    # Get gradient colors from palette
    color1 = CUSTOM_PALETTE[0]  # #FF5555
    color2 = CUSTOM_PALETTE[-1]  # #A3D78A
    
    # Cleaned CSS with subtle gradient (40 = 25% opacity)
    st.markdown(f"""
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
    """, unsafe_allow_html=True)
    
    # Value Formatting Logic
    def format_val(val):
        if val >= 1e12: return f"${val/1e12:.2f}T"
        if val >= 1e9:  return f"${val/1e9:.2f}B"
        if val >= 1e6:  return f"${val/1e6:.2f}M"
        return f"${val:,.0f}"

    total_display = format_val(total_gdp)
    avg_display = format_val(avg_gdp)
    
    # Rendered HTML
    st.markdown(f"""
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
    """, unsafe_allow_html=True)

def _render_filtered_data_preview(df: pd.DataFrame):
    with st.expander("View Filtered Data (Raw CSV-style)"):
        st.dataframe(
            df.sort_values(["Year", "Country Code"]),
            use_container_width=True,
            hide_index=True,
        )


# ---------- views ----------

def render_region_analysis(df, region, start_year, end_year, stat_operation, top_n):
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

        fig = charts.country_bar(agg, f" — {scope}", top_n)
        st.plotly_chart(fig, use_container_width=True)
        _register_figure("country_bar", fig)

        fig = charts.country_treemap(agg, top_n)
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