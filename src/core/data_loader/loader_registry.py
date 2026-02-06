import pkgutil
import inspect
import importlib
import pandas as pd
from pathlib import Path
from typing import List

from .loader_interface import DataLoader
from . import loaders

class LoaderRegistry:
    def __init__(self) -> None:
        self._loaders: List[DataLoader] = []
        self._discover_plugins()
    
    def _discover_plugins(self) -> None:
        for module_info in pkgutil.iter_modules(loaders.__path__):
            module = importlib.import_module(f"{loaders.__name__}.{module_info.name}")

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, DataLoader) and obj is not DataLoader:
                    self._loaders.append(obj())

    def load(self, file_path: Path) -> pd.DataFrame:
        for loader in self._loaders:
            if loader.supports(file_path):
                df = loader.load(file_path)
                return df

        raise ValueError(f"No loader found for: {file_path.suffix}")