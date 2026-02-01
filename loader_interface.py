from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

class Loader(ABC):
    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Must return True if this loader handles the file extension."""
        pass

    @abstractmethod
    def load(self, file_path: Path) -> pd.DataFrame:
        """Must load the data and return the result of to_csv_dataframe."""
        pass

    @abstractmethod
    def to_csv_dataframe(self, df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
        """Must save a physical CSV and return its DataFrame representation."""
        pass