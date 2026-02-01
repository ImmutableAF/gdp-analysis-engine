import streamlit as st
import plotly.express as px
import pandas as pd
from main import load_metadata, run_query
from pathlib import Path

# Page Config for a "Futuristic" feel
st.set_page_config(page_title="GDP Analytics Engine", layout="wide", initial_sidebar_state="expanded")

def display_dashboard():
    st.title("🌐 GDP Data Analysis Engine")
    st.markdown("---")

    # 1. Sidebar - Configuration Control
    st.sidebar.header("Control Panel")
    
    # Load current metadata to populate defaults
    base_config, query_config, args = load_metadata()

    # Allow user to "Update Config" via UI
    selected_region = st.sidebar.selectbox("Region", ["Europe", "Asia", "Americas", "Africa", "Oceania"], index=0)
    selected_year = st.sidebar.slider("Year", 1960, 2024, int(query_config.year))
    selected_op = st.sidebar.radio("Operation", ["average", "sum"], index=0)

    # RE-RUN BUTTON
    run_pressed = st.sidebar.button("🚀 Re-run Query")

    if run_pressed:
        # Update the query_config object with UI values before running
        # This simulates updating the config.json dynamically
        updated_query = query_config.__class__(
            region=selected_region,
            year=selected_year,
            country=query_config.country,
            operation=selected_op,
            dashboard_charts=query_config.dashboard_charts
        )

        with st.spinner('Executing Pipeline...'):
            try:
                # Execute Logic via main.py
                result_df = run_query(base_config, updated_query, args)

                if result_df.empty:
                    st.warning("No data matches the selected filters.")
                else:
                    # Layout: 2 Columns for Charts
                    col1, col2 = st.columns(2)
                    
                    val_col = [c for c in result_df.columns if "GDP" in c][0]

                    with col1:
                        st.subheader("📊 Regional Distribution")
                        # Plotly Bar Chart - Futuristic & Labeled
                        fig_bar = px.bar(result_df, x="Region", y=val_col, 
                                       text_auto='.2s', color="Region",
                                       template="plotly_dark", title=f"{selected_op.upper()} GDP - {selected_year}")
                        st.plotly_chart(fig_bar, use_container_width=True)

                    with col2:
                        st.subheader("🥧 Proportional Share")
                        # Plotly Pie Chart
                        fig_pie = px.pie(result_df, values=val_col, names="Region", 
                                       hole=0.4, template="plotly_dark")
                        st.plotly_chart(fig_pie, use_container_width=True)

                    # Data Table at bottom
                    st.subheader("📋 Raw Result Set")
                    st.dataframe(result_df, use_container_width=True)

            except Exception as e:
                st.error(f"Pipeline Error: {e}")
    else:
        st.info("Adjust the settings in the sidebar and click 'Re-run Query' to begin.")

if __name__ == "__main__":
    display_dashboard()