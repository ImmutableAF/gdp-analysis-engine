# test_main.py
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, Mock

from main import (
    get_paths,
    get_base_config,
    get_valid_attr,
    load_data,
    get_query_config,
    initialize_system
)
from src.core.config_manager.config_models import BaseConfig, QueryConfig


class TestGetPaths:
    def test_returns_tuple(self):
        result = get_paths()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_returns_path_objects(self):
        base_config_path, query_config_path = get_paths()
        
        assert isinstance(base_config_path, Path)
        assert isinstance(query_config_path, Path)
    
    def test_base_config_path_structure(self):
        base_config_path, _ = get_paths()
        
        assert base_config_path.name == "base_config.json"
        assert "configs" in base_config_path.parts
        assert "data" in base_config_path.parts
    
    def test_query_config_path_structure(self):
        _, query_config_path = get_paths()
        
        assert query_config_path.name == "query_config.json"
        assert "configs" in query_config_path.parts
        assert "data" in query_config_path.parts


class TestGetBaseConfig:
    @patch('main.load_base_config')
    @patch('main.validate_base_config')
    def test_loads_and_validates_config(self, mock_validate, mock_load, tmp_path):
        config = BaseConfig(tmp_path, "test.csv", tmp_path / "logs", 1000)
        mock_load.return_value = config
        
        result = get_base_config(tmp_path / "config.json")
        
        mock_load.assert_called_once()
        mock_validate.assert_called_once_with(config)
        assert result == config
    
    @patch('main.load_base_config')
    @patch('main.load_default_config')
    def test_falls_back_to_default_on_load_error(self, mock_default, mock_load, tmp_path):
        mock_load.side_effect = Exception("Load failed")
        default_config = BaseConfig(Path("data"), "default.csv", Path("logs"), 1000)
        mock_default.return_value = default_config
        
        result = get_base_config(tmp_path / "config.json")
        
        assert result == default_config
        mock_default.assert_called_once()
    
    @patch('main.load_base_config')
    @patch('main.validate_base_config')
    @patch('main.load_default_config')
    def test_falls_back_to_default_on_validation_error(self, mock_default, mock_validate, mock_load, tmp_path):
        config = BaseConfig(tmp_path, "test.csv", tmp_path / "logs", 1000)
        mock_load.return_value = config
        mock_validate.side_effect = ValueError("Invalid config")
        default_config = BaseConfig(Path("data"), "default.csv", Path("logs"), 1000)
        mock_default.return_value = default_config
        
        result = get_base_config(tmp_path / "config.json")
        
        assert result == default_config


class TestGetValidAttr:
    def test_extracts_regions(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Europe', 'Asia', 'Africa'],
            '1960': [100, 200, 300, 400]
        })
        
        regions, _ = get_valid_attr(df)
        
        assert set(regions) == {'Asia', 'Europe', 'Africa'}
    
    def test_extracts_year_range(self):
        df = pd.DataFrame({
            'Continent': ['Asia'],
            '1960': [100],
            '1970': [200],
            '1980': [300]
        })
        
        _, year_range = get_valid_attr(df)
        
        assert year_range == (1960, 1980)
    
    def test_filters_non_digit_columns(self):
        df = pd.DataFrame({
            'Continent': ['Asia'],
            'Country': ['China'],
            '1960': [100],
            '2000': [200]
        })
        
        _, year_range = get_valid_attr(df)
        
        assert year_range == (1960, 2000)
    
    def test_handles_single_year(self):
        df = pd.DataFrame({
            'Continent': ['Asia'],
            '2000': [100]
        })
        
        _, year_range = get_valid_attr(df)
        
        assert year_range == (2000, 2000)


class TestLoadData:
    @patch('main.LoaderRegistry')
    def test_uses_loader_registry(self, mock_registry_class):
        mock_registry = Mock()
        mock_registry.load.return_value = pd.DataFrame({'col': [1, 2, 3]})
        mock_registry_class.return_value = mock_registry
        
        result = load_data(Path("test.csv"))
        
        mock_registry_class.assert_called_once()
        mock_registry.load.assert_called_once_with(Path("test.csv"))
        assert isinstance(result, pd.DataFrame)
    
    @patch('main.LoaderRegistry')
    def test_returns_dataframe(self, mock_registry_class):
        expected_df = pd.DataFrame({'a': [1], 'b': [2]})
        mock_registry = Mock()
        mock_registry.load.return_value = expected_df
        mock_registry_class.return_value = mock_registry
        
        result = load_data(Path("data.csv"))
        
        pd.testing.assert_frame_equal(result, expected_df)


class TestGetQueryConfig:
    @patch('main.get_paths')
    @patch('main.load_query_config')
    @patch('main.sanatize_query_config')
    def test_loads_and_sanitizes_config(self, mock_sanitize, mock_load, mock_paths):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Europe'],
            '1960': [100, 200],
            '2000': [300, 400]
        })
        
        mock_paths.return_value = (Path("base.json"), Path("query.json"))
        raw_config = QueryConfig("Asia", 1970, 1990, "sum")
        mock_load.return_value = raw_config
        sanitized_config = QueryConfig("Asia", 1970, 1990, "sum")
        mock_sanitize.return_value = sanitized_config
        
        result = get_query_config(df)
        
        mock_load.assert_called_once_with(Path("query.json"))
        mock_sanitize.assert_called_once()
        assert result == sanitized_config
    
    @patch('main.get_paths')
    @patch('main.load_query_config')
    @patch('main.sanatize_query_config')
    def test_passes_valid_attributes(self, mock_sanitize, mock_load, mock_paths):
        df = pd.DataFrame({
            'Continent': ['Asia'],
            '1960': [100],
            '2000': [200]
        })
        
        mock_paths.return_value = (Path("base.json"), Path("query.json"))
        mock_load.return_value = QueryConfig(None, None, None, None)
        mock_sanitize.return_value = QueryConfig(None, None, None, None)
        
        get_query_config(df)
        
        call_args = mock_sanitize.call_args[0]
        regions = call_args[1]
        year_range = call_args[2]
        
        assert 'Asia' in regions
        assert year_range == (1960, 2000)


class TestInitializeSystem:
    @patch('main.parse_cli_args')
    @patch('main.get_base_config')
    @patch('main.initialize_logging')
    @patch('main.load_data')
    @patch('main.get_query_config')
    def test_parses_args(self, mock_query, mock_load, mock_logging, mock_base, mock_args):
        mock_args.return_value = Mock(debug=False, fpath=None)
        mock_base.return_value = BaseConfig(Path("data"), "test.csv", Path("logs"), 1000)
        mock_load.return_value = pd.DataFrame({'Continent': ['Asia'], '1960': [100]})
        mock_query.return_value = QueryConfig(None, None, None, None)
        
        initialize_system()
        
        mock_args.assert_called_once()
    
    @patch('main.parse_cli_args')
    @patch('main.get_base_config')
    @patch('main.initialize_logging')
    @patch('main.load_data')
    @patch('main.get_query_config')
    def test_initializes_logging(self, mock_query, mock_load, mock_logging, mock_base, mock_args):
        args = Mock(debug=True, fpath=None)
        mock_args.return_value = args
        config = BaseConfig(Path("data"), "test.csv", Path("logs"), 1000)
        mock_base.return_value = config
        mock_load.return_value = pd.DataFrame({'Continent': ['Asia'], '1960': [100]})
        mock_query.return_value = QueryConfig(None, None, None, None)
        
        initialize_system()
        
        mock_logging.assert_called_once_with(config, True)
    
    @patch('main.parse_cli_args')
    @patch('main.get_base_config')
    @patch('main.initialize_logging')
    @patch('main.load_data')
    @patch('main.get_query_config')
    def test_uses_cli_filepath_when_valid(self, mock_query, mock_load, mock_logging, mock_base, mock_args, tmp_path):
        test_file = tmp_path / "test.csv"
        test_file.touch()
        
        mock_args.return_value = Mock(debug=False, fpath=str(test_file))
        mock_base.return_value = BaseConfig(Path("data"), "default.csv", Path("logs"), 1000)
        mock_load.return_value = pd.DataFrame({'Continent': ['Asia'], '1960': [100]})
        mock_query.return_value = QueryConfig(None, None, None, None)
        
        initialize_system()
        
        mock_load.assert_called_once_with(test_file)
    
    @patch('main.parse_cli_args')
    @patch('main.get_base_config')
    @patch('main.initialize_logging')
    @patch('main.load_data')
    @patch('main.get_query_config')
    def test_uses_default_filepath_when_cli_invalid(self, mock_query, mock_load, mock_logging, mock_base, mock_args):
        mock_args.return_value = Mock(debug=False, fpath="nonexistent.csv")
        config = BaseConfig(Path("data"), "default.csv", Path("logs"), 1000)
        mock_base.return_value = config
        mock_load.return_value = pd.DataFrame({'Continent': ['Asia'], '1960': [100]})
        mock_query.return_value = QueryConfig(None, None, None, None)
        
        initialize_system()
        
        expected_path = Path("data") / "default.csv"
        mock_load.assert_called_once_with(expected_path)
    
    @patch('main.parse_cli_args')
    @patch('main.get_base_config')
    @patch('main.initialize_logging')
    @patch('main.load_data')
    @patch('main.get_query_config')
    def test_returns_dataframe_and_query_config(self, mock_query, mock_load, mock_logging, mock_base, mock_args):
        mock_args.return_value = Mock(debug=False, fpath=None)
        mock_base.return_value = BaseConfig(Path("data"), "test.csv", Path("logs"), 1000)
        expected_df = pd.DataFrame({'Continent': ['Asia'], '1960': [100]})
        expected_query = QueryConfig("Asia", 1960, 2000, "sum")
        mock_load.return_value = expected_df
        mock_query.return_value = expected_query
        
        df, query_config = initialize_system()
        
        pd.testing.assert_frame_equal(df, expected_df)
        assert query_config == expected_query
    
    @patch('main.parse_cli_args')
    @patch('main.get_paths')
    @patch('main.get_base_config')
    @patch('main.initialize_logging')
    @patch('main.load_data')
    @patch('main.get_query_config')
    def test_calls_get_base_config_with_correct_path(self, mock_query, mock_load, mock_logging, mock_base, mock_paths, mock_args):
        mock_args.return_value = Mock(debug=False, fpath=None)
        mock_paths.return_value = (Path("base_config.json"), Path("query_config.json"))
        mock_base.return_value = BaseConfig(Path("data"), "test.csv", Path("logs"), 1000)
        mock_load.return_value = pd.DataFrame({'Continent': ['Asia'], '1960': [100]})
        mock_query.return_value = QueryConfig(None, None, None, None)
        
        initialize_system()
        
        mock_base.assert_called_once_with(Path("base_config.json"))