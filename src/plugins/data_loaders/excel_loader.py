"""
Purpose:
Loader plugin that reads Excel files into a DataFrame.
"""

from pathlib import Path

import pandas as pd

from ..data_loading import DataLoader, register_plugin


@register_plugin
class ExcelLoader(DataLoader):
    """
    Loader plugin for Excel files (.xlsx and .xls).
    """

    def supports(self, source: Path) -> bool:
        """
        Return True if source ends with .xlsx or .xls.

        Parameters
        ----------
        source : Path
            Path to evaluate.

        Returns
        -------
        bool
            True if source ends with .xlsx or .xls, False otherwise.
        """
        return str(source).lower().endswith(".xlsx") or str(source).lower().endswith(".xls")

    def load(self, source: Path) -> pd.DataFrame:
        """
        Read the Excel file at source into a DataFrame.

        Parameters
        ----------
        source : Path
            Path to the Excel file to load.

        Returns
        -------
        pd.DataFrame
            Contents of the Excel file as a DataFrame.
        """
        return pd.read_excel(source)