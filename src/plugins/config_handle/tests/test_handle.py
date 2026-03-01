import pytest
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch
import pandas as pd

from ..handle import (
    _validate_base_config,
    _sanitize_region,
    _sanitize_years,
    _sanitize_operation,
    _sanatize_query_config,
    get_base_config,
    get_query_config,
)
from ..config_models import BaseConfig, QueryConfig


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_base_config(tmp_path, filename="gdp.xlsx"):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / filename).write_text("fake")
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return BaseConfig(
        data_dir=data_dir,
        data_filename=filename,
        log_dir=log_dir,
        max_log_size=1000000,
        output_mode="ui",
    )


def make_query_config(**kwargs):
    defaults = dict(
        region="Europe",
        country="Germany",
        startYear=1990,
        endYear=2020,
        operation="sum",
    )
    defaults.update(kwargs)
    return QueryConfig(**defaults)


# ── ValidateBaseConfig ────────────────────────────────────────────────────────


class TestValidateBaseConfig:

    def test_valid_config_does_not_raise(self, tmp_path):
        config = make_base_config(tmp_path)
        _validate_base_config(config)  # should not raise

    def test_zero_max_log_size_raises_value_error(self, tmp_path):
        config = make_base_config(tmp_path)
        bad = replace(config, max_log_size=0)
        with pytest.raises(ValueError, match="max_log_size"):
            _validate_base_config(bad)

    def test_negative_max_log_size_raises_value_error(self, tmp_path):
        config = make_base_config(tmp_path)
        bad = replace(config, max_log_size=-1)
        with pytest.raises(ValueError, match="max_log_size"):
            _validate_base_config(bad)

    def test_empty_data_filename_raises_value_error(self, tmp_path):
        config = make_base_config(tmp_path)
        bad = replace(config, data_filename="")
        with pytest.raises(ValueError, match="data_filename"):
            _validate_base_config(bad)

    def test_whitespace_data_filename_raises_value_error(self, tmp_path):
        config = make_base_config(tmp_path)
        bad = replace(config, data_filename="   ")
        with pytest.raises(ValueError, match="data_filename"):
            _validate_base_config(bad)

    def test_missing_data_dir_raises_file_not_found(self, tmp_path):
        config = make_base_config(tmp_path)
        bad = replace(config, data_dir=tmp_path / "nonexistent")
        with pytest.raises(FileNotFoundError):
            _validate_base_config(bad)

    def test_data_dir_as_file_raises_value_error(self, tmp_path):
        fake_file = tmp_path / "notadir"
        fake_file.write_text("x")
        config = make_base_config(tmp_path)
        bad = replace(config, data_dir=fake_file)
        with pytest.raises((ValueError, FileNotFoundError)):
            _validate_base_config(bad)

    def test_missing_data_file_raises_file_not_found(self, tmp_path):
        config = make_base_config(tmp_path)
        bad = replace(config, data_filename="missing.xlsx")
        with pytest.raises(FileNotFoundError):
            _validate_base_config(bad)

    def test_log_dir_as_file_raises_value_error(self, tmp_path):
        config = make_base_config(tmp_path)
        fake_file = tmp_path / "notadir.txt"
        fake_file.write_text("x")
        bad = replace(config, log_dir=fake_file)
        with pytest.raises(ValueError, match="log_dir"):
            _validate_base_config(bad)

    def test_nonexistent_log_dir_does_not_raise(self, tmp_path):
        config = make_base_config(tmp_path)
        bad = replace(config, log_dir=tmp_path / "new_logs")
        _validate_base_config(bad)  # log_dir not existing is allowed


# ── SanitizeRegion ────────────────────────────────────────────────────────────


class TestSanitizeRegion:

    def test_valid_region_is_returned(self):
        result = _sanitize_region("Europe", ["Europe", "Americas"])
        assert result == "Europe"

    def test_invalid_region_returns_none(self):
        result = _sanitize_region("Mars", ["Europe", "Americas"])
        assert result is None

    def test_none_region_returns_none(self):
        result = _sanitize_region(None, ["Europe", "Americas"])
        assert result is None

    def test_empty_string_returns_none(self):
        result = _sanitize_region("", ["Europe", "Americas"])
        assert result is None

    def test_comparison_is_case_insensitive(self):
        result = _sanitize_region("europe", ["Europe", "Americas"])
        assert result == "europe"

    def test_empty_valid_regions_returns_none(self):
        result = _sanitize_region("Europe", [])
        assert result is None


# ── SanitizeYears ─────────────────────────────────────────────────────────────


class TestSanitizeYears:

    def test_valid_years_are_returned(self):
        result = _sanitize_years(1990, 2020, (1960, 2024))
        assert result == (1990, 2020)

    def test_start_before_min_returns_none_start(self):
        start, end = _sanitize_years(1950, 2020, (1960, 2024))
        assert start is None
        assert end == 2020

    def test_end_after_max_returns_none_end(self):
        start, end = _sanitize_years(1990, 2030, (1960, 2024))
        assert start == 1990
        assert end is None

    def test_end_less_than_start_resets_both_to_none(self):
        start, end = _sanitize_years(2020, 1990, (1960, 2024))
        assert start is None
        assert end is None

    def test_none_start_is_allowed(self):
        start, end = _sanitize_years(None, 2020, (1960, 2024))
        assert start is None
        assert end == 2020

    def test_none_end_is_allowed(self):
        start, end = _sanitize_years(1990, None, (1960, 2024))
        assert start == 1990
        assert end is None

    def test_both_none_returns_none_none(self):
        result = _sanitize_years(None, None, (1960, 2024))
        assert result == (None, None)

    def test_start_equal_to_min_is_valid(self):
        start, _ = _sanitize_years(1960, 2020, (1960, 2024))
        assert start == 1960

    def test_end_equal_to_max_is_valid(self):
        _, end = _sanitize_years(1990, 2024, (1960, 2024))
        assert end == 2024


# ── SanitizeOperation ─────────────────────────────────────────────────────────


class TestSanitizeOperation:

    def test_sum_is_valid(self):
        assert _sanitize_operation("sum") == "sum"

    def test_avg_is_valid(self):
        assert _sanitize_operation("avg") == "avg"

    def test_average_is_valid(self):
        assert _sanitize_operation("average") == "average"

    def test_invalid_operation_returns_none(self):
        assert _sanitize_operation("median") is None

    def test_none_returns_none(self):
        assert _sanitize_operation(None) is None

    def test_empty_string_returns_none(self):
        assert _sanitize_operation("") is None

    def test_comparison_is_case_insensitive(self):
        assert _sanitize_operation("SUM") == "SUM"


# ── SanatizeQueryConfig ───────────────────────────────────────────────────────


class TestSanatizeQueryConfig:

    def test_returns_query_config_instance(self):
        config = make_query_config()
        result = _sanatize_query_config(config, ["Europe"], (1960, 2024))
        assert isinstance(result, QueryConfig)

    def test_valid_config_is_unchanged(self):
        config = make_query_config()
        result = _sanatize_query_config(config, ["Europe"], (1960, 2024))
        assert result.region == "Europe"
        assert result.startYear == 1990
        assert result.endYear == 2020
        assert result.operation == "sum"

    def test_invalid_region_is_reset_to_none(self):
        config = make_query_config(region="Mars")
        result = _sanatize_query_config(config, ["Europe"], (1960, 2024))
        assert result.region is None

    def test_out_of_range_years_are_reset(self):
        config = make_query_config(startYear=1800, endYear=2099)
        result = _sanatize_query_config(config, ["Europe"], (1960, 2024))
        assert result.startYear is None
        assert result.endYear is None

    def test_invalid_operation_is_reset_to_none(self):
        config = make_query_config(operation="median")
        result = _sanatize_query_config(config, ["Europe"], (1960, 2024))
        assert result.operation is None

    def test_country_is_passed_through_unchanged(self):
        config = make_query_config(country="Germany")
        result = _sanatize_query_config(config, ["Europe"], (1960, 2024))
        assert result.country == "Germany"

    def test_original_config_is_not_modified(self):
        config = make_query_config(region="Mars")
        _ = _sanatize_query_config(config, ["Europe"], (1960, 2024))
        assert config.region == "Mars"


# ── GetBaseConfig ─────────────────────────────────────────────────────────────


class TestGetBaseConfig:

    def test_returns_base_config_instance(self, tmp_path):
        config = make_base_config(tmp_path)
        with patch(
            "src.plugins.config_handle.handle.load_base_config", return_value=config
        ), patch("src.plugins.config_handle.handle._validate_base_config"):
            result = get_base_config()
        assert isinstance(result, BaseConfig)

    def test_falls_back_to_default_on_file_not_found(self):
        with patch(
            "src.plugins.config_handle.handle.load_base_config",
            side_effect=FileNotFoundError,
        ):
            result = get_base_config()
        assert isinstance(result, BaseConfig)

    def test_falls_back_to_default_on_validation_failure(self, tmp_path):
        config = make_base_config(tmp_path)
        with patch(
            "src.plugins.config_handle.handle.load_base_config", return_value=config
        ), patch(
            "src.plugins.config_handle.handle._validate_base_config",
            side_effect=ValueError("bad"),
        ):
            result = get_base_config()
        assert isinstance(result, BaseConfig)


class TestGetQueryConfig:

    def test_returns_query_config_instance(self):
        raw = make_query_config()
        df = pd.DataFrame(
            {
                "Continent": ["Europe"],
                "Year": [1990],
            }
        )
        with patch(
            "src.plugins.config_handle.handle.load_query_config", return_value=raw
        ), patch("src.plugins.config_handle.handle.get_query_config_path"):
            result = get_query_config(df)
        assert isinstance(result, QueryConfig)

    def test_invalid_region_is_sanitized(self):
        raw = make_query_config(region="Mars")
        df = pd.DataFrame(
            {
                "Continent": ["Europe"],
                "Year": [1990],
            }
        )
        with patch(
            "src.plugins.config_handle.handle.load_query_config", return_value=raw
        ), patch("src.plugins.config_handle.handle.get_query_config_path"):
            result = get_query_config(df)
        assert result.region is None

    def test_valid_region_is_preserved(self):
        raw = make_query_config(region="Europe")
        df = pd.DataFrame(
            {
                "Continent": ["Europe"],
                "Year": [1990],
            }
        )
        with patch(
            "src.plugins.config_handle.handle.load_query_config", return_value=raw
        ), patch("src.plugins.config_handle.handle.get_query_config_path"):
            result = get_query_config(df)
        assert result.region == "Europe"
