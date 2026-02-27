import json
import time
import requests
import pandas as pd
import streamlit as st
from types import SimpleNamespace

from src.plugins.ui import views

API_BASE = "http://localhost:8000"


def wait_for_api(retries: int = 20, delay: float = 1.0) -> bool:
    for i in range(retries):
        try:
            r = requests.get(f"{API_BASE}/metadata", timeout=2)
            if r.ok:
                return True
        except requests.ConnectionError:
            pass
        print(f"Waiting for API... attempt {i+1}/{retries}")
        time.sleep(delay)
    return False


@st.cache_resource
def boot() -> tuple[pd.DataFrame, dict, SimpleNamespace]:
    if not wait_for_api():
        st.error("API server did not start in time. Is main.py running?")
        st.stop()

    original_df = pd.DataFrame(json.loads(requests.get(f"{API_BASE}/original").text))
    metadata = json.loads(requests.get(f"{API_BASE}/metadata").text)
    config = json.loads(requests.get(f"{API_BASE}/config").text)
    default_config = SimpleNamespace(**config)
    return original_df, metadata, default_config


def fetch_filtered(filters: dict) -> pd.DataFrame:
    payload = {
        "filters": {
            "region": filters["region"],
            "country": filters["country"],
            "startYear": filters["start_year"],
            "endYear": filters["end_year"],
            "operation": filters["stat_operation"],
        }
    }
    resp = requests.post(f"{API_BASE}/run", json=payload, timeout=10)
    if not resp.ok:
        print(f"[fetch_filtered] error={resp.text}")
    resp.raise_for_status()
    return pd.DataFrame(json.loads(resp.text))


def main():
    st.set_page_config(page_title="GDP Analytics Dashboard")

    original_df, meta, default_config = boot()

    regions = meta["regions"]
    countries = meta["countries"]
    min_y, max_y = meta["year_range"]

    if "figures" not in st.session_state:
        st.session_state.figures = []
    st.session_state.figures.clear()

    filters = views.build_sidebar(regions, countries, min_y, max_y, default_config)

    if st.sidebar.button("Refresh Data"):
        st.session_state["filtered_df"] = fetch_filtered(filters)
        st.rerun()

    if "filtered_df" not in st.session_state:
        st.session_state["filtered_df"] = fetch_filtered(filters)

    st.title("GDP Analytics Dashboard")
    views.render_all_from_df(st.session_state["filtered_df"], filters)


if __name__ == "__main__":
    main()
