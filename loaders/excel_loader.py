import pandas as pd
from pathlib import Path
from loader_interface import Loader


class ExcelLoader(Loader):
    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".xlsx", ".xls")

    def load(self, file_path: Path) -> pd.DataFrame:
        return pd.read_excel(file_path)
