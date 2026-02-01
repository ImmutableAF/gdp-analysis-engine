from pathlib import Path
import pandas as pd


class DataLoader:
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def load(self) -> pd.DataFrame:
        if not self._file_path.exists():
            raise FileNotFoundError(f"File not found: {self._file_path}")

        suffix = self._file_path.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(self._file_path)

        if suffix in (".xlsx", ".xls"):
            return pd.read_excel(self._file_path)

        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            "Only .csv and .xlsx are supported."
        )
