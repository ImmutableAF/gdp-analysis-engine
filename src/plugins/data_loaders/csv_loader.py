"""
Purpose:
Loader plugin that reads CSV files into a DataFrame.
"""

from pathlib import Path

import pandas as pd

from ..data_loading import DataLoader, register_plugin


@register_plugin
class CsvLoader(DataLoader):
    """
    Loader plugin for CSV files.
    """

    def supports(self, source: Path) -> bool:
        """
        Parameters
        ----------
        source : Path
            Path to evaluate.

        Returns
        -------
        bool
            True if source ends with .csv, False otherwise.
        """
        return str(source).lower().endswith(".csv")

    def load(self, source: Path) -> pd.DataFrame:
        """
        Parameters
        ----------
        source : Path
            Path to the CSV file to load.

        Returns
        -------
        pd.DataFrame
            Contents of the CSV file as a DataFrame.
        """
        return pd.read_csv(source)