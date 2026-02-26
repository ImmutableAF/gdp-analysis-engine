from pathlib import Path
import streamlit as st

from src.plugins.config_handler import get_base_config, get_query_config
from src.plugins.data_loading.loading_manager import load_data
from src.core.data_cleaning import clean_gdp_data
from src.core.engine import run_pipeline
from src.plugins.outputs import OutputRunner, read_metadata
from src.plugins.ui import views


@st.cache_resource
def boot():
    base_config = get_base_config()
    filepath = Path(base_config.data_dir) / base_config.data_filename
    df = clean_gdp_data(load_data(filepath))
    query_config = get_query_config(df)
    meta = read_metadata()  # ← no core.metadata import
    runner = OutputRunner(
        lambda: run_pipeline(df=df, filters=query_config, inLongFormat=True)
    )
    return runner, query_config, meta


def main():
    st.set_page_config(page_title="GDP Analytics Dashboard")

    runner, query_config, meta = boot()

    regions = meta["regions"]
    countries = meta["countries"]
    min_y, max_y = meta["year_range"]

    if "figures" not in st.session_state:
        st.session_state.figures = []
    st.session_state.figures.clear()

    filters = views.build_sidebar(regions, countries, min_y, max_y, query_config)

    if st.sidebar.button("Refresh Data"):
        runner.refresh()
        st.rerun()

    st.title("GDP Analytics Dashboard")
    views.render_all(runner, filters)


if __name__ == "__main__":
    main()
