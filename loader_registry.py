import importlib
import pkgutil
import inspect
import pandas as pd
from pathlib import Path
from typing import List

from loader_interface import Loader
import loaders  # the package


class LoaderRegistry:
    def __init__(self):
        self._loaders: List[Loader] = []
        self._discover_plugins()

    def _discover_plugins(self) -> None:
        """Dynamically discovers Loader subclasses in the loaders package."""
        for module_info in pkgutil.iter_modules(loaders.__path__):
            module = importlib.import_module(f"{loaders.__name__}.{module_info.name}")

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Loader) and obj is not Loader:
                    self._loaders.append(obj())

    def load(self, file_path: Path) -> pd.DataFrame:
        """
        Orchestrates loading and enforces the CSV-only output constraint.
        """
        for loader in self._loaders:
            if loader.supports(file_path):
                # 1. Execute the loader's implementation
                df = loader.load(file_path)

                # 2. Strict Constraint Check: Ensure side-effect CSV exists
                csv_path = file_path.with_suffix(".csv")
                if not csv_path.exists():
                    raise RuntimeError(
                        f"Architecture Violation: Loader '{type(loader).__name__}' "
                        f"did not produce the required CSV file at {csv_path}"
                    )

                return df

        raise ValueError(f"No loader found for: {file_path.suffix}")