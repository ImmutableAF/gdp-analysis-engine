# test_config_loader.py
import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from src.core.config_manager.config_loader import load_base_config, load_query_config, load_default_config


def test_load_base_config_valid():
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "data_directory": "data",
            "default_file": "test.csv",
            "log_directory": "logs",
            "max_log_size": 5000
        }, f)
        f.flush()
        
        config = load_base_config(Path(f.name))
        assert config.data_directory == Path("data")
        assert config.default_file == "test.csv"
        assert config.log_directory == Path("logs")
        assert config.max_log_size == 5000
        
        Path(f.name).unlink()


def test_load_base_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_base_config(Path("nonexistent.json"))


def test_load_base_config_invalid_json():
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json")
        f.flush()
        
        with pytest.raises(json.JSONDecodeError):
            load_base_config(Path(f.name))
        
        Path(f.name).unlink()


def test_load_base_config_missing_keys():
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"data_directory": "data"}, f)
        f.flush()
        
        with pytest.raises(KeyError):
            load_base_config(Path(f.name))
        
        Path(f.name).unlink()


def test_load_query_config_all_fields():
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "region": "Asia",
            "startYear": 2000,
            "endYear": 2020,
            "operation": "sum"
        }, f)
        f.flush()
        
        config = load_query_config(Path(f.name))
        assert config.region == "Asia"
        assert config.startYear == 2000
        assert config.endYear == 2020
        assert config.operation == "sum"
        
        Path(f.name).unlink()


def test_load_query_config_partial_fields():
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"region": "Europe", "startYear": 2010}, f)
        f.flush()
        
        config = load_query_config(Path(f.name))
        assert config.region == "Europe"
        assert config.startYear == 2010
        assert config.endYear is None
        assert config.operation is None
        
        Path(f.name).unlink()


def test_load_query_config_empty():
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        f.flush()
        
        config = load_query_config(Path(f.name))
        assert config.region is None
        assert config.startYear is None
        assert config.endYear is None
        assert config.operation is None
        
        Path(f.name).unlink()


def test_load_query_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_query_config(Path("missing.json"))


def test_load_default_config():
    config = load_default_config()
    assert config.data_directory == Path("data")
    assert config.default_file == "gdp_with_continent_filled.csv"
    assert config.log_directory == Path("logs")
    assert config.max_log_size == 1000000