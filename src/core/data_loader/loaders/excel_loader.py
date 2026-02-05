import pandas as pd
from pathlib import Path

from ..loader_interface import DataLoader

class ExcelLoader(DataLoader):
    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".xsl", ".xslx") 

    def load(self, file_path: Path) -> pd.DataFrame:
        return pd.read_excel(file_path)