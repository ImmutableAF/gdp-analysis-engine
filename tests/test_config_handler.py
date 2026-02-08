# test_config_handler.py
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from src.core.config_manager.config_handler import validate_base_config, sanatize_query_config
from src.core.config_manager.config_models import BaseConfig, QueryConfig


class TestValidateBaseConfig:
    def test_valid_config(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "test.csv").touch()
        
        config = BaseConfig(
            data_directory=data_dir,
            default_file="test.csv",
            log_directory=tmp_path / "logs",
            max_log_size=1000
        )
        validate_base_config(config)
    
    def test_negative_log_size(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "test.csv").touch()
        
        config = BaseConfig(data_dir, "test.csv", tmp_path / "logs", -1)
        with pytest.raises(ValueError, match="max_log_size must be positive"):
            validate_base_config(config)
    
    def test_zero_log_size(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "test.csv").touch()
        
        config = BaseConfig(data_dir, "test.csv", tmp_path / "logs", 0)
        with pytest.raises(ValueError, match="max_log_size must be positive"):
            validate_base_config(config)
    
    def test_empty_default_file(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        config = BaseConfig(data_dir, "", tmp_path / "logs", 1000)
        with pytest.raises(ValueError, match="default_file cannot be empty"):
            validate_base_config(config)
    
    def test_whitespace_default_file(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        config = BaseConfig(data_dir, "   ", tmp_path / "logs", 1000)
        with pytest.raises(ValueError, match="default_file cannot be empty"):
            validate_base_config(config)
    
    def test_nonexistent_data_directory(self, tmp_path):
        config = BaseConfig(
            tmp_path / "nonexistent",
            "test.csv",
            tmp_path / "logs",
            1000
        )
        with pytest.raises(FileNotFoundError, match="data_directory does not exist"):
            validate_base_config(config)
    
    def test_data_directory_is_file(self, tmp_path):
        file_path = tmp_path / "notadir"
        file_path.touch()
        
        config = BaseConfig(file_path, "test.csv", tmp_path / "logs", 1000)
        with pytest.raises(ValueError, match="data_directory is not a directory"):
            validate_base_config(config)
    
    def test_default_file_not_found(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        config = BaseConfig(data_dir, "missing.csv", tmp_path / "logs", 1000)
        with pytest.raises(FileNotFoundError, match="default_file not found"):
            validate_base_config(config)
    
    def test_log_directory_is_file(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "test.csv").touch()
        
        log_file = tmp_path / "logfile"
        log_file.touch()
        
        config = BaseConfig(data_dir, "test.csv", log_file, 1000)
        with pytest.raises(ValueError, match="log_directory is not a directory"):
            validate_base_config(config)
    
    def test_log_directory_not_exists_ok(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "test.csv").touch()
        
        config = BaseConfig(data_dir, "test.csv", tmp_path / "logs", 1000)
        validate_base_config(config)


class TestSanatizeQueryConfig:
    def test_valid_all_fields(self):
        config = QueryConfig("Asia", 2000, 2020, "sum")
        result = sanatize_query_config(config, ["Asia", "Europe"], (1990, 2025))
        
        assert result.region == "Asia"
        assert result.startYear == 2000
        assert result.endYear == 2020
        assert result.operation == "sum"
    
    def test_invalid_region(self):
        config = QueryConfig("Unknown", 2000, 2020, "sum")
        result = sanatize_query_config(config, ["Asia", "Europe"], (1990, 2025))
        
        assert result.region is None
        assert result.startYear == 2000
        assert result.endYear == 2020
        assert result.operation == "sum"
    
    def test_region_case_insensitive(self):
        config = QueryConfig("ASIA", 2000, 2020, "sum")
        result = sanatize_query_config(config, ["Asia", "Europe"], (1990, 2025))
        
        assert result.region == "ASIA"
    
    def test_start_year_below_range(self):
        config = QueryConfig("Asia", 1980, 2020, "sum")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.startYear is None
    
    def test_end_year_above_range(self):
        config = QueryConfig("Asia", 2000, 2030, "sum")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.endYear is None
    
    def test_end_year_before_start_year(self):
        config = QueryConfig("Asia", 2020, 2000, "sum")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.startYear is None
        assert result.endYear is None
    
    def test_valid_operation_sum(self):
        config = QueryConfig("Asia", 2000, 2020, "sum")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.operation == "sum"
    
    def test_valid_operation_avg(self):
        config = QueryConfig("Asia", 2000, 2020, "avg")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.operation == "avg"
    
    def test_valid_operation_average(self):
        config = QueryConfig("Asia", 2000, 2020, "average")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.operation == "average"
    
    def test_invalid_operation(self):
        config = QueryConfig("Asia", 2000, 2020, "multiply")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.operation is None
    
    def test_operation_case_insensitive(self):
        config = QueryConfig("Asia", 2000, 2020, "SUM")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.operation == "SUM"
    
    def test_none_values_preserved(self):
        config = QueryConfig(None, None, None, None)
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.region is None
        assert result.startYear is None
        assert result.endYear is None
        assert result.operation is None
    
    def test_multiple_invalid_fields(self):
        config = QueryConfig("Unknown", 1980, 2030, "invalid")
        result = sanatize_query_config(config, ["Asia"], (1990, 2025))
        
        assert result.region is None
        assert result.startYear is None
        assert result.endYear is None
        assert result.operation is None