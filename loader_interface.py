from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd


class Loader(ABC):
    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        ...

    @abstractmethod
    def load(self, file_path: Path) -> pd.DataFrame:
        ...
