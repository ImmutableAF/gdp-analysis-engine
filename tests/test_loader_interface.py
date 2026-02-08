# test_loader_interface.py
import pytest
from pathlib import Path
import pandas as pd
from src.core.data_loader.loader_interface import DataLoader


class MockCSVLoader(DataLoader):
    def supports(self, file_path: Path) -> bool:
        return file_path.suffix == '.csv'
    
    def load(self, file_path: Path) -> pd.DataFrame:
        return pd.DataFrame({'col': [1, 2, 3]})


class MockJSONLoader(DataLoader):
    def supports(self, file_path: Path) -> bool:
        return file_path.suffix == '.json'
    
    def load(self, file_path: Path) -> pd.DataFrame:
        return pd.DataFrame({'data': ['a', 'b']})


def test_loader_interface_is_abstract():
    with pytest.raises(TypeError):
        DataLoader()


def test_loader_must_implement_supports():
    class IncompleteLoader(DataLoader):
        def load(self, file_path: Path) -> pd.DataFrame:
            return pd.DataFrame()
    
    with pytest.raises(TypeError):
        IncompleteLoader()


def test_loader_must_implement_load():
    class IncompleteLoader(DataLoader):
        def supports(self, file_path: Path) -> bool:
            return True
    
    with pytest.raises(TypeError):
        IncompleteLoader()


def test_concrete_loader_supports():
    loader = MockCSVLoader()
    assert loader.supports(Path("file.csv")) is True
    assert loader.supports(Path("file.json")) is False


def test_concrete_loader_load():
    loader = MockCSVLoader()
    df = loader.load(Path("test.csv"))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert 'col' in df.columns


def test_multiple_loader_implementations():
    csv_loader = MockCSVLoader()
    json_loader = MockJSONLoader()
    
    assert csv_loader.supports(Path("data.csv"))
    assert not csv_loader.supports(Path("data.json"))
    
    assert json_loader.supports(Path("data.json"))
    assert not json_loader.supports(Path("data.csv"))