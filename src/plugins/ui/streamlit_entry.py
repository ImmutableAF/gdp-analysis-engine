import os
import time
import streamlit as st
import pandas as pd
from types import SimpleNamespace
from dataclasses import dataclass, field
from typing import Callable

from src.plugins.ui.style import load_css
from src.plugins.ui import views
from src.plugins.ui import analytics_views
from src.plugins.ui.contracts import (
    TopBottomDF,
    GrowthRateDF,
    AvgGDPContinentDF,
    GlobalTrendDF,
    FastestContinentDF,
    ConsistentDeclineDF,
    ContinentShareDF,
)
from src.plugins.outputs import CoreAPIClient, AnalyticsAPIClient

_API_URL = os.environ.get("CORE_API_URL", "http://localhost:8010")
_ANALYTICS_URL = os.environ.get("ANALYTICS_API_URL", "http://localhost:8011")


# ── Contracts ─────────────────────────────────────────────────────────────────


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
        return (
            self.region,
            effective_country,
            self.start_year,
            self.end_year,
            self.stat_operation,
            self.show_country,
        )

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class FetchedData:
    region_df: pd.DataFrame
    country_df: pd.DataFrame | None
    fetched_for: tuple


@dataclass
class AnalyticsData:
    """
    Holds all pre-fetched, pre-validated DataFrames for the analytics tab.

    Each field corresponds to one analytics section. Empty DataFrames indicate
    a fetch or validation failure — the section will show an error in the UI.
    fetch_params records the params used so views can detect stale data.
    """

    top_countries: pd.DataFrame = field(default_factory=pd.DataFrame)
    bottom_countries: pd.DataFrame = field(default_factory=pd.DataFrame)
    growth_rate: pd.DataFrame = field(default_factory=pd.DataFrame)
    avg_gdp_continent: pd.DataFrame = field(default_factory=pd.DataFrame)
    global_trend: pd.DataFrame = field(default_factory=pd.DataFrame)
    fastest_continent: pd.DataFrame = field(default_factory=pd.DataFrame)
    consistent_decline: pd.DataFrame = field(default_factory=pd.DataFrame)
    continent_share: pd.DataFrame = field(default_factory=pd.DataFrame)
    fetch_params: dict = field(default_factory=dict)


# ── Boot ──────────────────────────────────────────────────────────────────────


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
def boot() -> tuple[CoreAPIClient, AnalyticsAPIClient, dict, dict[str, str], dict]:
    core = CoreAPIClient(base_url=_API_URL)
    analytics = AnalyticsAPIClient(base_url=_ANALYTICS_URL)

    if not _wait_for_api(core):
        st.error("API server did not start in time. Is main.py running?")
        st.stop()

    metadata = core.get_metadata()

    try:
        df = core.run({"region": "__ALL__", "startYear": 2020, "endYear": 2020})
        code_map: dict[str, str] = dict(zip(df["Country Name"], df["Country Code"]))
    except Exception:
        code_map = {}

    try:
        analytics_cfg: dict = core.get_analytics_config()
    except Exception:
        analytics_cfg = {}

    return core, analytics, metadata, code_map, analytics_cfg


# ── Analytics fetch helpers ───────────────────────────────────────────────────


def _fetch_and_validate(
    label: str,
    contract,
    fetch_callable,
) -> pd.DataFrame:
    """
    Call fetch_callable(), validate against contract, return df or empty df on error.
    Errors are stored in session state so views can surface them.
    """
    try:
        df = fetch_callable()
    except Exception as e:
        st.session_state.setdefault("analytics_errors", {})[
            label
        ] = f"{label}: fetch failed — {e}"
        return pd.DataFrame()

    result = contract.validate(df)
    if not result.ok:
        st.session_state.setdefault("analytics_errors", {})[label] = result.error
        return pd.DataFrame()

    # Clear any previous error for this section
    st.session_state.setdefault("analytics_errors", {}).pop(label, None)
    return df


def _build_fetch_params(analytics_cfg: dict, metadata: dict) -> dict:
    """Derive the default fetch params from analytics config + metadata bounds."""
    yr = metadata.get("year_range", [1960, 2024])
    min_y = int(yr[0])
    max_y = int(yr[1])

    def clamp_year(key, fallback):
        return max(min_y, min(max_y, int(analytics_cfg.get(key, fallback))))

    return {
        "continent": analytics_cfg.get("continent", ""),
        "defaultYear": clamp_year("defaultYear", max_y),
        "startYear": clamp_year("startYear", min_y),
        "endYear": clamp_year("endYear", max_y),
        "topN": int(analytics_cfg.get("topN", 10)),
        "consecutiveYears": int(analytics_cfg.get("consecutiveYears", 3)),
        "referenceYear": clamp_year("referenceYear", max_y),
    }


def fetch_analytics_upfront(
    client: AnalyticsAPIClient,
    analytics_cfg: dict,
    metadata: dict,
) -> AnalyticsData:
    """
    Fetch all analytics sections upfront using default config values.
    Called once on first load; results stored in session state.
    """
    st.session_state["analytics_errors"] = {}
    p = _build_fetch_params(analytics_cfg, metadata)
    continent = p["continent"]

    top = _fetch_and_validate(
        "top_countries",
        TopBottomDF,
        lambda: client.get_top_countries(continent, p["defaultYear"], p["topN"]),
    )
    bottom = _fetch_and_validate(
        "bottom_countries",
        TopBottomDF,
        lambda: client.get_bottom_countries(continent, p["defaultYear"], p["topN"]),
    )
    growth = _fetch_and_validate(
        "growth_rate",
        GrowthRateDF,
        lambda: client.get_gdp_growth_rate(continent, p["startYear"], p["endYear"]),
    )
    avg_cont = _fetch_and_validate(
        "avg_gdp_continent",
        AvgGDPContinentDF,
        lambda: client.get_avg_gdp_by_continent(p["startYear"], p["endYear"]),
    )
    global_t = _fetch_and_validate(
        "global_trend",
        GlobalTrendDF,
        lambda: client.get_global_gdp_trend(p["startYear"], p["endYear"]),
    )
    fastest = _fetch_and_validate(
        "fastest_continent",
        FastestContinentDF,
        lambda: client.get_fastest_growing_continent(p["startYear"], p["endYear"]),
    )
    decline = _fetch_and_validate(
        "consistent_decline",
        ConsistentDeclineDF,
        lambda: client.get_consistent_decline(
            p["consecutiveYears"], p["referenceYear"]
        ),
    )
    share = _fetch_and_validate(
        "continent_share",
        ContinentShareDF,
        lambda: client.get_continent_gdp_share(p["startYear"], p["endYear"]),
    )

    return AnalyticsData(
        top_countries=top,
        bottom_countries=bottom,
        growth_rate=growth,
        avg_gdp_continent=avg_cont,
        global_trend=global_t,
        fastest_continent=fastest,
        consistent_decline=decline,
        continent_share=share,
        fetch_params=p,
    )


def make_fetch_fn(
    client: AnalyticsAPIClient,
) -> Callable[[str, dict], pd.DataFrame]:
    """
    Returns a fetch_fn(section, params) -> pd.DataFrame closure over the client.

    This is injected into analytics_views so views can trigger lazy re-fetches
    per section without importing AnalyticsAPIClient or contracts directly.

    section must be one of:
        top_countries, bottom_countries, growth_rate, avg_gdp_continent,
        global_trend, fastest_continent, consistent_decline, continent_share
    """
    _SECTION_MAP: dict[str, tuple] = {
        "top_countries": (
            TopBottomDF,
            lambda c, p: c.get_top_countries(p["continent"], p["year"], p["n"]),
        ),
        "bottom_countries": (
            TopBottomDF,
            lambda c, p: c.get_bottom_countries(p["continent"], p["year"], p["n"]),
        ),
        "growth_rate": (
            GrowthRateDF,
            lambda c, p: c.get_gdp_growth_rate(
                p["continent"], p["startYear"], p["endYear"]
            ),
        ),
        "avg_gdp_continent": (
            AvgGDPContinentDF,
            lambda c, p: c.get_avg_gdp_by_continent(p["startYear"], p["endYear"]),
        ),
        "global_trend": (
            GlobalTrendDF,
            lambda c, p: c.get_global_gdp_trend(p["startYear"], p["endYear"]),
        ),
        "fastest_continent": (
            FastestContinentDF,
            lambda c, p: c.get_fastest_growing_continent(p["startYear"], p["endYear"]),
        ),
        "consistent_decline": (
            ConsistentDeclineDF,
            lambda c, p: c.get_consistent_decline(
                p["consecutiveYears"], p["referenceYear"]
            ),
        ),
        "continent_share": (
            ContinentShareDF,
            lambda c, p: c.get_continent_gdp_share(p["startYear"], p["endYear"]),
        ),
    }

    def fetch_fn(section: str, params: dict) -> pd.DataFrame:
        if section not in _SECTION_MAP:
            raise ValueError(f"Unknown analytics section: {section!r}")
        contract, caller = _SECTION_MAP[section]
        return _fetch_and_validate(section, contract, lambda: caller(client, params))

    return fetch_fn


# ── Dashboard fetch ───────────────────────────────────────────────────────────


def _fetch(client: CoreAPIClient, filters: SidebarFilters) -> FetchedData:
    region_df = client.run(
        {
            "region": filters.region,
            "country": None,
            "startYear": filters.start_year,
            "endYear": filters.end_year,
            "operation": filters.stat_operation,
        }
    )

    country_df = None
    if filters.show_country and filters.country:
        country_df = client.run(
            {
                "region": None,
                "country": filters.country,
                "startYear": filters.start_year,
                "endYear": filters.end_year,
                "operation": filters.stat_operation,
            }
        )

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


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    st.set_page_config(page_title="GDP Analytics Dashboard")

    core, analytics, metadata, code_map, analytics_cfg = boot()

    if not analytics_cfg:
        st.error(
            "Analytics configuration is missing or empty. Application cannot start."
        )
        st.stop()

    regions = metadata["regions"]
    countries = metadata["countries"]
    min_y, max_y = metadata["year_range"]

    # Fetch analytics data upfront on first load only
    if "analytics_data" not in st.session_state:
        with st.spinner("Loading analytics data…"):
            st.session_state["analytics_data"] = fetch_analytics_upfront(
                analytics, analytics_cfg, metadata
            )

    fetch_fn = make_fetch_fn(analytics)

    tab1, tab2 = st.tabs(["Dashboard", "Analytics"])

    with tab1:
        if "figures" not in st.session_state:
            st.session_state.figures = []
        st.session_state.figures.clear()

        if "active_config" not in st.session_state:
            st.session_state.active_config = SimpleNamespace(**core.get_config())

        if st.session_state.pop("pending_widget_reset", False):
            cfg = st.session_state.active_config
            region_val = cfg.region if cfg.region else "All"
            op_label = (
                "Average"
                if (cfg.operation or "avg").lower() in ["avg", "average"]
                else "Sum"
            )
            st.session_state["sb_region"] = region_val
            st.session_state["sb_year_range"] = (cfg.startYear, cfg.endYear)
            st.session_state["sb_operation"] = op_label
            st.session_state["sb_show_country"] = cfg.country is not None
            if cfg.country:
                st.session_state["sb_country"] = cfg.country

        raw = views.build_sidebar(
            regions, countries, min_y, max_y, st.session_state.active_config
        )
        filters = SidebarFilters(**raw)

        refreshed = st.sidebar.button("Refresh Data")

        if refreshed:
            new_config = SimpleNamespace(**core.reload_config())
            st.session_state.active_config = new_config
            new_filters = _config_to_filters(new_config)
            st.session_state.data = _fetch(core, new_filters)
            st.session_state.pending_widget_reset = True
            st.rerun()

        data: FetchedData | None = st.session_state.get("data")
        if data is None or data.fetched_for != filters.api_key():
            st.session_state.data = _fetch(core, filters)

        data = st.session_state.data

        st.title("GDP Analytics Dashboard")
        views.render_all_from_df(data.region_df, data.country_df, filters.to_dict())

    with tab2:
        analytics_views.render_analytics_tab(
            metadata=metadata,
            code_map=code_map,
            analytics_cfg=analytics_cfg,
            analytics_data=st.session_state["analytics_data"],
            fetch_fn=fetch_fn,
        )


if __name__ == "__main__":
    load_css("layout.css")
    main()
