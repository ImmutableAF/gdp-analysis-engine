import json
import pytest
from pathlib import Path
from ..config_load import (
    load_base_config,
    load_query_config,
    load_default_config,
)
from ..config_models import BaseConfig, QueryConfig


# ── Helpers ──────────────────────────────────────────────────────────────────

def write_base_json(tmp_path, overrides=None):
    data = {
        "data_dir": "data",
        "data_filename": "gdp.xlsx",
        "log_dir": "logs",
        "max_log_size": 1000000,
        "output_mode": "ui",
    }
    if overrides:
        data.update(overrides)
    path = tmp_path / "base.json"
    path.write_text(json.dumps(data))
    return path


def write_query_json(tmp_path, overrides=None):
    data = {
        "region": "Europe",
        "country": "Germany",
        "startYear": 1990,
        "endYear": 2020,
        "operation": "mean",
    }
    if overrides:
        data.update(overrides)
    path = tmp_path / "query.json"
    path.write_text(json.dumps(data))
    return path


# ── LoadBaseConfig ────────────────────────────────────────────────────────────

class TestLoadBaseConfig:

    def test_returns_base_config_instance(self, tmp_path):
        path = write_base_json(tmp_path)
        result = load_base_config(path)
        assert isinstance(result, BaseConfig)

    def test_data_dir_is_parsed_as_path(self, tmp_path):
        path = write_base_json(tmp_path)
        result = load_base_config(path)
        assert isinstance(result.data_dir, Path)
        assert result.data_dir == Path("data")

    def test_log_dir_is_parsed_as_path(self, tmp_path):
        path = write_base_json(tmp_path)
        result = load_base_config(path)
        assert isinstance(result.log_dir, Path)
        assert result.log_dir == Path("logs")

    def test_data_filename_is_correct(self, tmp_path):
        path = write_base_json(tmp_path)
        result = load_base_config(path)
        assert result.data_filename == "gdp.xlsx"

    def test_max_log_size_is_correct(self, tmp_path):
        path = write_base_json(tmp_path)
        result = load_base_config(path)
        assert result.max_log_size == 1000000

    def test_output_mode_is_correct(self, tmp_path):
        path = write_base_json(tmp_path)
        result = load_base_config(path)
        assert result.output_mode == "ui"

    def test_custom_values_are_loaded(self, tmp_path):
        path = write_base_json(tmp_path, overrides={"output_mode": "api", "max_log_size": 500000})
        result = load_base_config(path)
        assert result.output_mode == "api"
        assert result.max_log_size == 500000

    def test_missing_key_raises_key_error(self, tmp_path):
        incomplete = {"data_dir": "data", "data_filename": "gdp.xlsx"}
        path = tmp_path / "base.json"
        path.write_text(json.dumps(incomplete))
        with pytest.raises(KeyError):
            load_base_config(path)

    def test_missing_file_raises_error(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            load_base_config(path)


# ── LoadQueryConfig ───────────────────────────────────────────────────────────

class TestLoadQueryConfig:

    def test_returns_query_config_instance(self, tmp_path):
        path = write_query_json(tmp_path)
        result = load_query_config(path)
        assert isinstance(result, QueryConfig)

    def test_region_is_correct(self, tmp_path):
        path = write_query_json(tmp_path)
        result = load_query_config(path)
        assert result.region == "Europe"

    def test_country_is_correct(self, tmp_path):
        path = write_query_json(tmp_path)
        result = load_query_config(path)
        assert result.country == "Germany"

    def test_start_year_is_correct(self, tmp_path):
        path = write_query_json(tmp_path)
        result = load_query_config(path)
        assert result.startYear == 1990

    def test_end_year_is_correct(self, tmp_path):
        path = write_query_json(tmp_path)
        result = load_query_config(path)
        assert result.endYear == 2020

    def test_operation_is_correct(self, tmp_path):
        path = write_query_json(tmp_path)
        result = load_query_config(path)
        assert result.operation == "mean"

    def test_missing_region_defaults_to_none(self, tmp_path):
        path = write_query_json(tmp_path, overrides={"region": None})
        result = load_query_config(path)
        assert result.region is None

    def test_missing_country_defaults_to_none(self, tmp_path):
        path = write_query_json(tmp_path, overrides={"country": None})
        result = load_query_config(path)
        assert result.country is None

    def test_all_fields_missing_defaults_to_none(self, tmp_path):
        path = tmp_path / "query.json"
        path.write_text(json.dumps({}))
        result = load_query_config(path)
        assert result.region is None
        assert result.country is None
        assert result.startYear is None
        assert result.endYear is None
        assert result.operation is None

    def test_missing_file_raises_error(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            load_query_config(path)


# ── LoadDefaultConfig ─────────────────────────────────────────────────────────

class TestLoadDefaultConfig:

    def test_returns_base_config_instance(self):
        result = load_default_config()
        assert isinstance(result, BaseConfig)

    def test_data_dir_is_correct(self):
        result = load_default_config()
        assert result.data_dir == Path("data")

    def test_data_filename_is_correct(self):
        result = load_default_config()
        assert result.data_filename == "gdp_with_continent_filled.xlsx"

    def test_log_dir_is_correct(self):
        result = load_default_config()
        assert result.log_dir == Path("logs")

    def test_max_log_size_is_correct(self):
        result = load_default_config()
        assert result.max_log_size == 1000000

    def test_output_mode_is_correct(self):
        result = load_default_config()
        assert result.output_mode == "ui"

    def test_requires_no_file_on_disk(self):
        result = load_default_config()
        assert result is not None