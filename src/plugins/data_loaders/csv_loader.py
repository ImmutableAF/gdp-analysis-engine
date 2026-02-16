from pathlib import Path

import pandas as pd

from ..data_loading import DataLoader, register_plugin

@register_plugin
class CsvLoader(DataLoader):
    def supports(self, source: Path) -> bool:
        return str(source).lower().endswith(".csv")

    def load(self, source: Path) -> pd.DataFrame:
        return pd.read_csv(source)
