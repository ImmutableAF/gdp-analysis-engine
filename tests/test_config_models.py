# test_config_models.py
import pytest
from pathlib import Path
from src.core.config_manager.config_models import BaseConfig, QueryConfig


def test_base_config_creation():
    config = BaseConfig(
        data_directory=Path("data"),
        default_file="test.csv",
        log_directory=Path("logs"),
        max_log_size=1000
    )
    assert config.data_directory == Path("data")
    assert config.default_file == "test.csv"
    assert config.log_directory == Path("logs")
    assert config.max_log_size == 1000


def test_base_config_immutable():
    config = BaseConfig(Path("data"), "test.csv", Path("logs"), 1000)
    with pytest.raises(Exception):
        config.max_log_size = 2000


def test_query_config_all_fields():
    config = QueryConfig(
        region="Asia",
        startYear=2000,
        endYear=2020,
        operation="sum"
    )
    assert config.region == "Asia"
    assert config.startYear == 2000
    assert config.endYear == 2020
    assert config.operation == "sum"


def test_query_config_optional_fields():
    config = QueryConfig(None, None, None, None)
    assert config.region is None
    assert config.startYear is None
    assert config.endYear is None
    assert config.operation is None


def test_query_config_partial_fields():
    config = QueryConfig(region="Europe", startYear=2010, endYear=None, operation=None)
    assert config.region == "Europe"
    assert config.startYear == 2010
    assert config.endYear is None
    assert config.operation is None


def test_query_config_immutable():
    config = QueryConfig("Asia", 2000, 2020, "avg")
    with pytest.raises(Exception):
        config.region = "Europe"