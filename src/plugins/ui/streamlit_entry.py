import os
import time
import streamlit as st
import pandas as pd
from types import SimpleNamespace
from dataclasses import dataclass

from src.plugins.ui import views
from src.plugins.ui import analytics_views
from src.plugins.outputs import CoreAPIClient

_API_URL = os.environ.get("CORE_API_URL", "http://localhost:8010")


# ── contracts ─────────────────────────────────────────────────────────────────

@dataclass
class SidebarFilters:
    region: str | None
    country: str | None
    start_year: int
    end_year: int
    stat_operation: str
    show_country: bool
    show_all: bool

    def api_key(self) -> tuple:
        effective_country = self.country if self.show_country else None
        return (self.region, effective_country, self.start_year,
                self.end_year, self.stat_operation, self.show_country)

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class FetchedData:
    region_df: pd.DataFrame
    country_df: pd.DataFrame | None
    fetched_for: tuple


# ── boot ──────────────────────────────────────────────────────────────────────

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
def boot() -> tuple[CoreAPIClient, dict]:
    client = CoreAPIClient(base_url=_API_URL)
    if not _wait_for_api(client):
        st.error("API server did not start in time. Is main.py running?")
        st.stop()
    metadata = client.get_metadata()
    return client, metadata


# ── fetch ─────────────────────────────────────────────────────────────────────

def _fetch(client: CoreAPIClient, filters: SidebarFilters) -> FetchedData:
    region_df = client.run({
        "region": filters.region,
        "country": None,
        "startYear": filters.start_year,
        "endYear": filters.end_year,
        "operation": filters.stat_operation,
    })

    country_df = None
    if filters.show_country and filters.country:
        country_df = client.run({
            "region": None,
            "country": filters.country,
            "startYear": filters.start_year,
            "endYear": filters.end_year,
            "operation": filters.stat_operation,
        })

    return FetchedData(
        region_df=region_df,
        country_df=country_df,
        fetched_for=filters.api_key(),
    )


def _config_to_filters(config: SimpleNamespace) -> SidebarFilters:
    return SidebarFilters(
        region=config.region,
        country=config.country,
        start_year=config.startYear,
        end_year=config.endYear,
        stat_operation=config.operation,
        show_country=config.country is not None,
        show_all=False,
    )


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="GDP Analytics Dashboard", layout="wide")

    client, metadata = boot()

    regions   = metadata["regions"]
    countries = metadata["countries"]
    min_y, max_y = metadata["year_range"]

    # ── tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📊 Dashboard", "🔬 Analytics"])

    # ── Tab 1: existing dashboard ─────────────────────────────────────────────
    with tab1:
        if "figures" not in st.session_state:
            st.session_state.figures = []
        st.session_state.figures.clear()

        if "active_config" not in st.session_state:
            st.session_state.active_config = SimpleNamespace(**client.get_config())

        if st.session_state.pop("pending_widget_reset", False):
            cfg = st.session_state.active_config
            region_val = cfg.region if cfg.region else "All"
            op_label   = "Average" if (cfg.operation or "avg").lower() in ["avg", "average"] else "Sum"
            st.session_state["sb_region"]       = region_val
            st.session_state["sb_year_range"]   = (cfg.startYear, cfg.endYear)
            st.session_state["sb_operation"]    = op_label
            st.session_state["sb_show_country"] = cfg.country is not None
            if cfg.country:
                st.session_state["sb_country"]  = cfg.country

        raw = views.build_sidebar(regions, countries, min_y, max_y,
                                  st.session_state.active_config)
        filters = SidebarFilters(**raw)

        refreshed = st.sidebar.button("Refresh Data")

        if refreshed:
            new_config = SimpleNamespace(**client.reload_config())
            st.session_state.active_config = new_config
            new_filters = _config_to_filters(new_config)
            st.session_state.data = _fetch(client, new_filters)
            st.session_state.pending_widget_reset = True
            st.rerun()

        data: FetchedData | None = st.session_state.get("data")
        if data is None or data.fetched_for != filters.api_key():
            st.session_state.data = _fetch(client, filters)

        data = st.session_state.data

        st.title("GDP Analytics Dashboard")
        views.render_all_from_df(data.region_df, data.country_df, filters.to_dict())

    # ── Tab 2: analytics ──────────────────────────────────────────────────────
    with tab2:
        analytics_views.render_analytics_tab(metadata)


if __name__ == "__main__":
    main()