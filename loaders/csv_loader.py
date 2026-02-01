import pandas as pd
from pathlib import Path
from loader_interface import Loader


class CsvLoader(Loader):
    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".csv"

    def load(self, file_path: Path) -> pd.DataFrame:
        return pd.read_csv(file_path)

    def to_csv_dataframe(self, df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
        return df