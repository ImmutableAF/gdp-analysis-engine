from __future__ import annotations
from enum import StrEnum
from typing import Callable, Any
import json
import tempfile
from pathlib import Path
import pandas as pd

Provider = Callable[[], pd.DataFrame]

_META_PATH = Path(tempfile.gettempdir()) / "gdp_engine_meta.json"


class OutputMode(StrEnum):
    UI = "ui"
    CLI = "cli"


_endpoints: dict[str, Callable[[pd.DataFrame], Any]] = {}


def endpoint(name: str):
    def decorator(fn):
        _endpoints[name] = fn
        return fn

    return decorator


@endpoint("filtered_df")
def _(df: pd.DataFrame) -> pd.DataFrame:
    return df


@endpoint("region_agg")
def _(df: pd.DataFrame) -> pd.DataFrame:
    from src.core.engine import aggregate_by_region

    return aggregate_by_region(df, "sum")


@endpoint("country_agg")
def _(df: pd.DataFrame) -> pd.DataFrame:
    from src.core.engine import aggregate_by_country_code

    return aggregate_by_country_code(df, "sum")


@endpoint("region_agg_avg")
def _(df: pd.DataFrame) -> pd.DataFrame:
    from src.core.engine import aggregate_by_region

    return aggregate_by_region(df, "avg")


class OutputRunner:
    def __init__(self, provider: Provider) -> None:
        self._provider = provider
        self._df: pd.DataFrame | None = None

    def refresh(self) -> None:
        self._df = self._provider()

    def get(self, name: str) -> Any:
        if self._df is None:
            self.refresh()
        if name not in _endpoints:
            raise KeyError(f"No endpoint: '{name}'")
        return _endpoints[name](self._df)


class OutputSink:
    def __init__(self, runner, metadata, original_df=None, query_config=None):
        self.runner = runner
        self.metadata = metadata
        self.original_df = original_df
        self.query_config = query_config

    def start(self) -> None:
        raise NotImplementedError


def write_metadata(metadata: dict) -> None:
    _META_PATH.write_text(json.dumps(metadata))


def read_metadata() -> dict:
    return json.loads(_META_PATH.read_text())


def make_sink(mode, metadata, original_df, query_config, provider):
    write_metadata(metadata)
    runner = OutputRunner(provider)
    match mode:
        case OutputMode.UI:
            from src.plugins.ui.app import UISink

            return UISink(runner, metadata, original_df, query_config)
        case OutputMode.CLI:
            from src.plugins.cli.app import CliSink

            return CliSink(runner, metadata)
