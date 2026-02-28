from __future__ import annotations
from enum import StrEnum
from typing import Optional, Any
import httpx
import pandas as pd
from typing import Callable


class OutputMode(StrEnum):
    UI = "ui"
    CLI = "cli"


class CoreAPIClient:
    """
    Thin HTTP client wrapping the core API server.
    All OutputSink subclasses use this to get live data.
    """

    def __init__(self, base_url: str = "http://localhost:8010"):
        self._base = base_url.rstrip("/")

    def _post(self, path: str, filters: Optional[dict] = None) -> pd.DataFrame:
        body = filters or {}
        # Strip None values so server falls back to its defaults
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


class OutputSink:
    """Base class for all output sinks. Receives a live CoreAPIClient."""

    def __init__(self, client: CoreAPIClient):
        self.client = client

    def start(self) -> None:
        raise NotImplementedError


def make_sink(
    mode: OutputMode,
    api_url: str = "http://localhost:8010",
    analytics_url: str = "http://localhost:8011",
) -> OutputSink:
    client = CoreAPIClient(base_url=api_url)
    match mode:
        case OutputMode.UI:
            from src.plugins.ui.app import UISink

            return UISink(client, analytics_url=analytics_url)
        case OutputMode.CLI:
            from src.plugins.cli.app import CliSink

            return CliSink(client)
