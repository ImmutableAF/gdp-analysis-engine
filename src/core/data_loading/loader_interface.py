from pathlib import Path
from abc import ABC, abstractmethod

from pandas import DataFrame

class DataLoader(ABC):
    @abstractmethod
    def supports(filepath: Path):
        pass
    @abstractmethod
    def load(filepath: Path) ->  DataFrame:
        pass
