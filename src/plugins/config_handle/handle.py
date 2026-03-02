"""
Purpose:
Loads, validates, and sanitizes configuration before it reaches the pipeline.

Description:
Acts as the single entry point for obtaining ready-to-use config objects.
BaseConfig is validated against the filesystem to catch bad paths or values
early. QueryConfig is sanitized against the actual data — invalid regions,
out-of-range years, and unrecognized operations are silently reset to None.
AnalyticsConfig is sanitized against the actual data year range and valid
slider bounds — out-of-range values are clamped or reset to safe defaults.
PortsConfig is sanitized against valid TCP port bounds — out-of-range values
are reset to hardcoded defaults.
Falls back to hardcoded defaults if any config file is missing or invalid.
"""

import logging
from dataclasses import replace
from typing import Iterable, Optional, Tuple, List

import pandas as pd

from .config_load import (
    load_analytics_config,
    load_base_config,
    load_default_analytics_config,
    load_default_config,
    load_default_ports_config,
    load_ports_config,
    load_query_config,
)
from .config_models import AnalyticsConfig, BaseConfig, PortsConfig, QueryConfig
from .paths import (
    get_analytics_config_path,
    get_base_config_path,
    get_ports_config_path,
    get_query_config_path,
)
from src.core.metadata import get_valid_attr

logger = logging.getLogger(__name__)

# ── Bounds for analytics slider fields ───────────────────────────────────────

_TOP_N_MIN = 5
_TOP_N_MAX = 30
_TOP_N_DEFAULT = 10

_CONSEC_MIN = 2
_CONSEC_MAX = 10
_CONSEC_DEFAULT = 3

# ── Bounds for port fields ────────────────────────────────────────────────────

_PORT_MIN = 1024
_PORT_MAX = 65535
_PORT_CORE_DEFAULT = 8010
_PORT_ANALYTICS_DEFAULT = 8011


# ── Base config ───────────────────────────────────────────────────────────────


def _validate_base_config(config: BaseConfig) -> None:
    if config.max_log_size <= 0:
        raise ValueError("max_log_size must be positive")
    if not config.data_filename or not config.data_filename.strip():
        raise ValueError("data_filename cannot be empty")
    if not config.data_dir.exists():
        raise FileNotFoundError(f"data_dir does not exist: {config.data_dir}")
    if not config.data_dir.is_dir():
        raise ValueError(f"data_dir is not a directory: {config.data_dir}")
    default_path = config.data_dir / config.data_filename
    if not default_path.is_file():
        raise FileNotFoundError(f"data_filename not found: {default_path}")
    if config.log_dir.exists() and not config.log_dir.is_dir():
        raise ValueError(f"log_dir is not a directory: {config.log_dir}")


# ── Query config sanitization ─────────────────────────────────────────────────


def _sanitize_region(
    region: Optional[str], valid_regions: Iterable[str]
) -> Optional[str]:
    if not region:
        return None
    valid_set = {r.lower() for r in valid_regions}
    if region.lower() not in valid_set:
        logger.debug(f"Invalid region '{region}' → resetting to None")
        return None
    return region


def _sanitize_years(
    start: Optional[int], end: Optional[int], year_range: Tuple[int, int]
) -> Tuple[Optional[int], Optional[int]]:
    min_year, max_year = year_range
    validated_start = start
    validated_end = end

    if validated_start is not None and validated_start < min_year:
        logger.debug(f"startYear {validated_start} out of range → resetting")
        validated_start = None
    if validated_end is not None and validated_end > max_year:
        logger.debug(f"endYear {validated_end} out of range → resetting")
        validated_end = None
    if (
        validated_start is not None
        and validated_end is not None
        and validated_end < validated_start
    ):
        logger.debug("endYear < startYear → resetting both to None")
        return None, None

    return validated_start, validated_end


def _sanitize_operation(operation: Optional[str]) -> Optional[str]:
    if not operation:
        return None
    if operation.lower() not in {"sum", "avg", "average"}:
        logger.debug(f"Invalid operation '{operation}' → resetting to None")
        return None
    return operation


def _sanitize_query_config(config: QueryConfig, regions, year_range) -> QueryConfig:
    region = _sanitize_region(config.region, regions)
    start, end = _sanitize_years(config.startYear, config.endYear, year_range)
    operation = _sanitize_operation(config.operation)
    normalized = replace(
        config, region=region, startYear=start, endYear=end, operation=operation
    )
    logger.debug(f"Normalized query config: {normalized}")
    return normalized


# ── Analytics config sanitization ────────────────────────────────────────────


def _clamp_year(value: Optional[int], min_year: int, max_year: int, field: str) -> int:
    if value is None:
        logger.debug(f"analytics_config: '{field}' is None → defaulting to {max_year}")
        return max_year
    if value < min_year:
        logger.debug(
            f"analytics_config: '{field}'={value} < {min_year} → clamping to {min_year}"
        )
        return min_year
    if value > max_year:
        logger.debug(
            f"analytics_config: '{field}'={value} > {max_year} → clamping to {max_year}"
        )
        return max_year
    return value


def _clamp_int(value: Optional[int], lo: int, hi: int, default: int, field: str) -> int:
    if value is None:
        logger.debug(f"analytics_config: '{field}' is None → defaulting to {default}")
        return default
    if value < lo or value > hi:
        logger.debug(
            f"analytics_config: '{field}'={value} out of [{lo}, {hi}] → defaulting to {default}"
        )
        return default
    return value


def _sanitize_analytics_config(
    config: AnalyticsConfig, regions: List[str], year_range: Tuple[int, int]
) -> AnalyticsConfig:
    min_year, max_year = year_range

    default_year = _clamp_year(config.defaultYear, min_year, max_year, "defaultYear")
    start_year = _clamp_year(config.startYear, min_year, max_year, "startYear")
    end_year = _clamp_year(config.endYear, min_year, max_year, "endYear")
    ref_year = _clamp_year(config.referenceYear, min_year, max_year, "referenceYear")

    if end_year < start_year:
        logger.debug(
            f"analytics_config: endYear({end_year}) < startYear({start_year}) "
            f"after clamping → resetting to ({min_year}, {max_year})"
        )
        start_year = min_year
        end_year = max_year

    top_n = _clamp_int(config.topN, _TOP_N_MIN, _TOP_N_MAX, _TOP_N_DEFAULT, "topN")
    consec_years = _clamp_int(
        config.consecutiveYears,
        _CONSEC_MIN,
        _CONSEC_MAX,
        _CONSEC_DEFAULT,
        "consecutiveYears",
    )

    if config.continent and config.continent in regions:
        continent = config.continent
    elif regions:
        logger.debug(
            f"analytics_config: invalid continent '{config.continent}' "
            f"→ defaulting to first available region '{regions[0]}'"
        )
        continent = regions[0]
    else:
        raise RuntimeError("No valid regions available to assign continent")

    sanitized = AnalyticsConfig(
        continent=continent,
        defaultYear=default_year,
        startYear=start_year,
        endYear=end_year,
        topN=top_n,
        consecutiveYears=consec_years,
        referenceYear=ref_year,
    )
    logger.debug(f"Sanitized analytics config: {sanitized}")
    return sanitized


# ── Ports config sanitization ─────────────────────────────────────────────────


def _sanitize_port(value: Optional[int], default: int, field: str) -> int:
    """
    Resolve a port value to a valid TCP port in [1024, 65535].

    Ports below 1024 are privileged and rejected. None and out-of-range values
    fall back to the provided default.

    Parameters
    ----------
    value : int or None
        Raw port value from the config file.
    default : int
        Fallback port to use if value is None or invalid.
    field : str
        Field name used in log messages.

    Returns
    -------
    int
        A valid port number in [1024, 65535].
    """
    if value is None:
        logger.debug(f"ports_config: '{field}' is None → defaulting to {default}")
        return default
    if value < _PORT_MIN or value > _PORT_MAX:
        logger.debug(
            f"ports_config: '{field}'={value} out of [{_PORT_MIN}, {_PORT_MAX}] "
            f"→ defaulting to {default}"
        )
        return default
    return value


def _sanitize_ports_config(config: PortsConfig) -> PortsConfig:
    core_port = _sanitize_port(config.core_port, _PORT_CORE_DEFAULT, "core_port")
    analytics_port = _sanitize_port(
        config.analytics_port, _PORT_ANALYTICS_DEFAULT, "analytics_port"
    )

    if core_port == analytics_port:
        logger.warning(
            f"ports_config: core_port and analytics_port are both {core_port} — "
            f"resetting to defaults ({_PORT_CORE_DEFAULT}, {_PORT_ANALYTICS_DEFAULT})"
        )
        core_port = _PORT_CORE_DEFAULT
        analytics_port = _PORT_ANALYTICS_DEFAULT

    sanitized = PortsConfig(core_port=core_port, analytics_port=analytics_port)
    logger.debug(f"Sanitized ports config: {sanitized}")
    return sanitized


# ── Public entry points ───────────────────────────────────────────────────────


def get_base_config() -> BaseConfig:
    try:
        base_config = load_base_config(get_base_config_path())
        _validate_base_config(base_config)
    except Exception as e:
        logger.debug(f"Base config failed: {e}, falling back to defaults")
        base_config = load_default_config()
    return base_config


def get_query_config(df: pd.DataFrame) -> QueryConfig:
    raw_config = load_query_config(get_query_config_path())
    regions, year_range = get_valid_attr(df)
    return _sanitize_query_config(raw_config, regions, year_range)


def get_analytics_config(df: pd.DataFrame) -> AnalyticsConfig:
    try:
        raw_config = load_analytics_config(get_analytics_config_path())
        logger.info("analytics_config.json loaded successfully")
    except FileNotFoundError:
        logger.warning("analytics_config.json not found — using hardcoded defaults")
        raw_config = load_default_analytics_config()
    except (ValueError, KeyError, TypeError) as e:
        logger.warning(
            f"analytics_config.json invalid ({e}) — using hardcoded defaults"
        )
        raw_config = load_default_analytics_config()
    except Exception as e:
        logger.warning(
            f"analytics_config.json failed to load ({e}) — using hardcoded defaults"
        )
        raw_config = load_default_analytics_config()

    regions, year_range = get_valid_attr(df)
    return _sanitize_analytics_config(raw_config, regions, year_range)


def get_ports_config() -> PortsConfig:
    """
    Load and sanitize ports configuration from ports_config.json.

    Does not require a DataFrame — port validation is purely numeric.
    Falls back to defaults (8010, 8011) on any failure.

    Returns
    -------
    PortsConfig
        Fully resolved ports config with no None values.
    """
    try:
        raw_config = load_ports_config(get_ports_config_path())
        logger.info("ports_config.json loaded successfully")
    except FileNotFoundError:
        logger.warning("ports_config.json not found — using hardcoded defaults")
        raw_config = load_default_ports_config()
    except (ValueError, KeyError, TypeError) as e:
        logger.warning(f"ports_config.json invalid ({e}) — using hardcoded defaults")
        raw_config = load_default_ports_config()
    except Exception as e:
        logger.warning(
            f"ports_config.json failed to load ({e}) — using hardcoded defaults"
        )
        raw_config = load_default_ports_config()

    return _sanitize_ports_config(raw_config)
