"""
Analytics Data Contracts
========================
Validator classes for Analytics API responses.

Each contract exposes a validate(df) classmethod that checks required column
presence and returns a ValidationResult. Views and entry points use these
instead of Protocol + isinstance(), which does not work on DataFrames.

Design
------
- Contracts are the single source of truth for what each endpoint must return.
- ValidationResult carries ok + error so callers decide how to surface failures.
- No coupling to Streamlit, httpx, or any other layer.

Usage
-----
>>> result = TopBottomDF.validate(df)
>>> if not result.ok:
...     st.error(result.error)
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


# ── Result ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ValidationResult:
    """
    Outcome of a contract validation check.

    Attributes
    ----------
    ok : bool
        True if the DataFrame satisfies the contract.
    error : str
        Human-readable error message. Empty string when ok is True.
    """

    ok: bool
    error: str = ""

    @staticmethod
    def success() -> ValidationResult:
        return ValidationResult(ok=True)

    @staticmethod
    def failure(contract_name: str, missing: list[str]) -> ValidationResult:
        cols = ", ".join(missing)
        return ValidationResult(
            ok=False,
            error=f"Response does not match contract {contract_name}: missing columns [{cols}]",
        )


# ── Base ──────────────────────────────────────────────────────────────────────


class _DFContract:
    """
    Base class for all DataFrame contracts.

    Subclasses declare required_columns as a class-level list. The validate()
    classmethod checks that all required columns are present in the DataFrame.
    """

    required_columns: list[str] = []

    @classmethod
    def validate(cls, df: pd.DataFrame) -> ValidationResult:
        if df.empty:
            return ValidationResult(
                ok=False,
                error=f"{cls.__name__}: received empty DataFrame",
            )
        missing = [c for c in cls.required_columns if c not in df.columns]
        if missing:
            return ValidationResult.failure(cls.__name__, missing)
        return ValidationResult.success()


# ── Contracts ─────────────────────────────────────────────────────────────────


class TopBottomDF(_DFContract):
    """Contract for /top-countries and /bottom-countries responses."""

    required_columns = ["country", "gdp"]


class GrowthRateDF(_DFContract):
    """Contract for /gdp-growth-rate responses."""

    required_columns = ["country", "year", "growth_rate_pct"]


class AvgGDPContinentDF(_DFContract):
    """Contract for /avg-gdp-by-continent responses."""

    required_columns = ["continent", "avg_gdp"]


class GlobalTrendDF(_DFContract):
    """Contract for /global-gdp-trend responses."""

    required_columns = ["year", "total_gdp"]


class FastestContinentDF(_DFContract):
    """Contract for /fastest-growing-continent responses."""

    required_columns = ["continent", "growth_pct"]


class ConsistentDeclineDF(_DFContract):
    """Contract for /consistent-decline responses."""

    required_columns = ["country", "avg_decline_pct"]


class ContinentShareDF(_DFContract):
    """Contract for /continent-gdp-share responses."""

    required_columns = ["continent", "share_pct"]
