# test_loader_registry.py
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.core.data_loader.loader_registry import LoaderRegistry
from src.core.data_loader.loader_interface import DataLoader


class TestLoaderRegistry:
    def test_registry_initialization(self):
        registry = LoaderRegistry()
        assert hasattr(registry, '_loaders')
        assert isinstance(registry._loaders, list)
    
    def test_discover_plugins_called_on_init(self):
        with patch.object(LoaderRegistry, '_discover_plugins') as mock_discover:
            registry = LoaderRegistry()
            mock_discover.assert_called_once()
    
    @patch('loading.loader_registry.pkgutil.iter_modules')
    @patch('loading.loader_registry.importlib.import_module')
    def test_discover_plugins_imports_modules(self, mock_import, mock_iter):
        mock_iter.return_value = [
            MagicMock(name='csv_loader'),
            MagicMock(name='json_loader')
        ]
        mock_import.return_value = MagicMock()
        
        registry = LoaderRegistry()
        assert mock_import.call_count == 2
    
    @patch('loading.loader_registry.pkgutil.iter_modules')
    @patch('loading.loader_registry.importlib.import_module')
    @patch('loading.loader_registry.inspect.getmembers')
    def test_discover_plugins_registers_loaders(self, mock_members, mock_import, mock_iter):
        class TestLoader(DataLoader):
            def supports(self, file_path: Path) -> bool:
                return True
            def load(self, file_path: Path) -> pd.DataFrame:
                return pd.DataFrame()
        
        mock_iter.return_value = [MagicMock(name='test_loader')]
        mock_import.return_value = MagicMock()
        mock_members.return_value = [('TestLoader', TestLoader)]
        
        registry = LoaderRegistry()
        assert len(registry._loaders) == 1
        assert isinstance(registry._loaders[0], TestLoader)
    
    @patch('loading.loader_registry.pkgutil.iter_modules')
    @patch('loading.loader_registry.importlib.import_module')
    @patch('loading.loader_registry.inspect.getmembers')
    def test_discover_plugins_ignores_base_class(self, mock_members, mock_import, mock_iter):
        mock_iter.return_value = [MagicMock(name='test')]
        mock_import.return_value = MagicMock()
        mock_members.return_value = [('DataLoader', DataLoader)]
        
        registry = LoaderRegistry()
        assert len(registry._loaders) == 0
    
    def test_load_with_matching_loader(self):
        registry = LoaderRegistry()
        
        mock_loader = Mock(spec=DataLoader)
        mock_loader.supports.return_value = True
        mock_loader.load.return_value = pd.DataFrame({'a': [1, 2]})
        
        registry._loaders = [mock_loader]
        
        result = registry.load(Path("test.csv"))
        
        mock_loader.supports.assert_called_once_with(Path("test.csv"))
        mock_loader.load.assert_called_once_with(Path("test.csv"))
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
    
    def test_load_with_no_matching_loader(self):
        registry = LoaderRegistry()
        
        mock_loader = Mock(spec=DataLoader)
        mock_loader.supports.return_value = False
        
        registry._loaders = [mock_loader]
        
        with pytest.raises(ValueError, match="No loader found for: .xyz"):
            registry.load(Path("test.xyz"))
    
    def test_load_uses_first_matching_loader(self):
        registry = LoaderRegistry()
        
        loader1 = Mock(spec=DataLoader)
        loader1.supports.return_value = True
        loader1.load.return_value = pd.DataFrame({'first': [1]})
        
        loader2 = Mock(spec=DataLoader)
        loader2.supports.return_value = True
        loader2.load.return_value = pd.DataFrame({'second': [2]})
        
        registry._loaders = [loader1, loader2]
        
        result = registry.load(Path("test.csv"))
        
        loader1.load.assert_called_once()
        loader2.load.assert_not_called()
        assert 'first' in result.columns
    
    def test_load_with_multiple_loaders_different_support(self):
        registry = LoaderRegistry()
        
        csv_loader = Mock(spec=DataLoader)
        csv_loader.supports.side_effect = lambda p: p.suffix == '.csv'
        csv_loader.load.return_value = pd.DataFrame({'csv': [1]})
        
        json_loader = Mock(spec=DataLoader)
        json_loader.supports.side_effect = lambda p: p.suffix == '.json'
        json_loader.load.return_value = pd.DataFrame({'json': [2]})
        
        registry._loaders = [csv_loader, json_loader]
        
        csv_result = registry.load(Path("data.csv"))
        assert 'csv' in csv_result.columns
        
        json_result = registry.load(Path("data.json"))
        assert 'json' in json_result.columns
    
    def test_load_returns_dataframe(self):
        registry = LoaderRegistry()
        
        mock_loader = Mock(spec=DataLoader)
        mock_loader.supports.return_value = True
        expected_df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        mock_loader.load.return_value = expected_df
        
        registry._loaders = [mock_loader]
        
        result = registry.load(Path("test.csv"))
        
        pd.testing.assert_frame_equal(result, expected_df)
    
    def test_empty_registry_raises_error(self):
        registry = LoaderRegistry()
        registry._loaders = []
        
        with pytest.raises(ValueError, match="No loader found for"):
            registry.load(Path("test.csv"))