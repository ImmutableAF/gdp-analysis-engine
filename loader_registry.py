import importlib
import pkgutil
import inspect
from pathlib import Path
from typing import List

from loader_interface import Loader
import loaders  # the package


class LoaderRegistry:
    def __init__(self):
        self._loaders: List[Loader] = []
        self._discover_plugins()

    def _discover_plugins(self) -> None:
        for module_info in pkgutil.iter_modules(loaders.__path__):
            module = importlib.import_module(f"{loaders.__name__}.{module_info.name}")

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Loader) and obj is not Loader:
                    self._loaders.append(obj())

    def load(self, file_path: Path):
        for loader in self._loaders:
            if loader.supports(file_path):
                return loader.load(file_path)

        raise ValueError(f"No loader found for: {file_path.suffix}")
