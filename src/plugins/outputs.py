from __future__ import annotations

from enum import StrEnum
from typing import Any, Optional

import httpx
import pandas as pd


class OutputMode(StrEnum):
    UI = "ui"
    CLI = "cli"
    FILE = "file"


# ── Core API ──────────────────────────────────────────────────────────────────


class CoreAPIClient:
    """
    Thin HTTP client wrapping the core API server (:8010).
    All OutputSink subclasses use this to get live data.
    """

    def __init__(self, base_url: str = "http://localhost:8010"):
        self._base = base_url.rstrip("/")

    def _post(self, path: str, filters: Optional[dict] = None) -> pd.DataFrame:
        body = filters or {}
        body = {k: v for k, v in body.items() if v is not None}
        r = httpx.post(f"{self._base}{path}", json=body, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json())

    def _get(self, path: str) -> Any:
        r = httpx.get(f"{self._base}{path}", timeout=30)
        r.raise_for_status()
        return r.json()

    def get_metadata(self) -> dict:
        return self._get("/metadata")

    def get_config(self) -> dict:
        return self._get("/config")

    def get_original(self) -> pd.DataFrame:
        return pd.DataFrame(self._get("/original"))

    def get_analytics_config(self) -> dict:
        """
        Fetch the sanitized analytics chart defaults from the core API.

        Returns a dict with keys: continent, defaultYear, startYear, endYear,
        topN, consecutiveYears, referenceYear — all guaranteed to be valid by
        handle.py sanitization at startup.

        Returns
        -------
        dict
            Analytics config values, or {} if the endpoint is unavailable.
        """
        return self._get("/analytics-config")

    def run(self, filters: Optional[dict] = None) -> pd.DataFrame:
        return self._post("/run", filters)

    def aggregate_by_region(self, filters: Optional[dict] = None) -> pd.DataFrame:
        return self._post("/aggregate/region", filters)

    def aggregate_by_country(self, filters: Optional[dict] = None) -> pd.DataFrame:
        return self._post("/aggregate/country", filters)

    def aggregate_by_country_code(self, filters: Optional[dict] = None) -> pd.DataFrame:
        return self._post("/aggregate/country-code", filters)

    def aggregate_all(self, filters: Optional[dict] = None) -> pd.DataFrame:
        return self._post("/aggregate/all", filters)

    def reload_config(self) -> dict:
        r = httpx.post(f"{self._base}/config/reload", timeout=10)
        r.raise_for_status()
        return r.json()


# ── Analytics API ─────────────────────────────────────────────────────────────


class AnalyticsAPIClient:
    """
    Thin HTTP client wrapping the analytics API server (:8011).

    Each method maps 1:1 to an analytics endpoint and returns a raw DataFrame.
    No validation happens here — callers are responsible for running the
    appropriate contract from contracts.py.

    Parameters
    ----------
    base_url : str
        Base URL of the analytics API server.
    """

    def __init__(self, base_url: str = "http://localhost:8011"):
        self._base = base_url.rstrip("/")

    def _get(self, path: str, params: dict) -> pd.DataFrame:
        params = {k: v for k, v in params.items() if v is not None}
        r = httpx.get(f"{self._base}{path}", params=params, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json())

    def get_top_countries(self, continent: str, year: int, n: int) -> pd.DataFrame:
        return self._get(
            "/top-countries", {"continent": continent, "year": year, "n": n}
        )

    def get_bottom_countries(self, continent: str, year: int, n: int) -> pd.DataFrame:
        return self._get(
            "/bottom-countries", {"continent": continent, "year": year, "n": n}
        )

    def get_gdp_growth_rate(
        self, continent: str, start_year: int, end_year: int
    ) -> pd.DataFrame:
        return self._get(
            "/gdp-growth-rate",
            {"continent": continent, "startYear": start_year, "endYear": end_year},
        )

    def get_avg_gdp_by_continent(self, start_year: int, end_year: int) -> pd.DataFrame:
        return self._get(
            "/avg-gdp-by-continent", {"startYear": start_year, "endYear": end_year}
        )

    def get_global_gdp_trend(self, start_year: int, end_year: int) -> pd.DataFrame:
        return self._get(
            "/global-gdp-trend", {"startYear": start_year, "endYear": end_year}
        )

    def get_fastest_growing_continent(
        self, start_year: int, end_year: int
    ) -> pd.DataFrame:
        return self._get(
            "/fastest-growing-continent", {"startYear": start_year, "endYear": end_year}
        )

    def get_consistent_decline(
        self, last_x_years: int, reference_year: int
    ) -> pd.DataFrame:
        return self._get(
            "/consistent-decline",
            {"lastXYears": last_x_years, "referenceYear": reference_year},
        )

    def get_continent_gdp_share(self, start_year: int, end_year: int) -> pd.DataFrame:
        return self._get(
            "/continent-gdp-share", {"startYear": start_year, "endYear": end_year}
        )


# ── Sinks ─────────────────────────────────────────────────────────────────────


class OutputSink:
    """Base class for all output sinks. Receives a live CoreAPIClient."""

    def __init__(self, client: CoreAPIClient):
        self.client = client

    def start(self) -> None:
        raise NotImplementedError


def make_sink(
    base_config,
    api_url: str = "http://localhost:8010",
    analytics_url: str = "http://localhost:8011",
    mode_override: Optional[OutputMode] = None,
) -> OutputSink:
    """
    Resolve output mode from config, with an optional CLI override.
    Priority: mode_override > base_config.output_mode
    """
    mode = mode_override or OutputMode(base_config.output_mode)
    client = CoreAPIClient(base_url=api_url)

    match mode:
        case OutputMode.UI:
            from src.plugins.ui.app import UISink

            return UISink(client, analytics_url=analytics_url)
        case OutputMode.CLI:
            from src.plugins.cli.app import CliSink

            return CliSink(client, analytics_url=analytics_url)
        case OutputMode.FILE:
            from src.plugins.fileWriter.app import FileOutputSink

            return FileOutputSink(client, analytics_url=analytics_url)
        case _:
            raise ValueError(f"Unknown output mode: {mode!r}")
