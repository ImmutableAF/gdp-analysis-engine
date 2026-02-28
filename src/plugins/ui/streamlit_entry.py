import os
import time
import streamlit as st
import pandas as pd
from types import SimpleNamespace

from src.plugins.outputs import CoreAPIClient
from src.plugins.ui import views

_API_URL = os.environ.get("CORE_API_URL", "http://localhost:8010")


def _wait_for_api(client: CoreAPIClient, retries: int = 20, delay: float = 1.0) -> bool:
    for i in range(retries):
        try:
            client.get_metadata()
            return True
        except Exception:
            print(f"Waiting for API... attempt {i + 1}/{retries}")
            time.sleep(delay)
    return False


@st.cache_resource
def boot() -> tuple[CoreAPIClient, pd.DataFrame, dict]:
    client = CoreAPIClient(base_url=_API_URL)

    if not _wait_for_api(client):
        st.error("API server did not start in time. Is main.py running?")
        st.stop()

    original_df = client.get_original()
    metadata = client.get_metadata()

    return client, original_df, metadata


def fetch_filtered(client: CoreAPIClient, filters: dict) -> pd.DataFrame:
    return client.run({
        "region": filters["region"],
        "country": filters["country"],
        "startYear": filters["start_year"],
        "endYear": filters["end_year"],
        "operation": filters["stat_operation"],
    })


def config_to_filters(config: SimpleNamespace) -> dict:
    return {
        "region": config.region,
        "country": config.country,
        "start_year": config.startYear,
        "end_year": config.endYear,
        "stat_operation": config.operation,
    }


def main():
    st.set_page_config(page_title="GDP Analytics Dashboard")

    client, original_df, metadata = boot()

    regions = metadata["regions"]
    countries = metadata["countries"]
    min_y, max_y = metadata["year_range"]

    if "figures" not in st.session_state:
        st.session_state.figures = []
    st.session_state.figures.clear()

    if "active_config" not in st.session_state:
        st.session_state.active_config = SimpleNamespace(**client.get_config())

    # Build sidebar in its natural position — button appears where views.build_sidebar puts it
    filters = views.build_sidebar(regions, countries, min_y, max_y, st.session_state.active_config)
    refreshed = st.sidebar.button("Refresh Data")

    # Handle reload after sidebar is fully rendered
    if refreshed:
        new_config = SimpleNamespace(**client.reload_config())
        st.session_state.active_config = new_config
        st.session_state["filtered_df"] = fetch_filtered(client, config_to_filters(new_config))
        st.rerun()

    if "filtered_df" not in st.session_state:
        st.session_state["filtered_df"] = fetch_filtered(client, filters)

    st.title("GDP Analytics Dashboard")
    views.render_all_from_df(st.session_state["filtered_df"], filters)


if __name__ == "__main__":
    main()