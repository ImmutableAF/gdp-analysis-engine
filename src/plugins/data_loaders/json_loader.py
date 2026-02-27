"""
Purpose:
Loader plugin that reads JSON files into a DataFrame.
"""

from pathlib import Path

import pandas as pd

from ..data_loading import DataLoader, register_plugin


@register_plugin
class JsonLoader(DataLoader):
    """
    Loader plugin for JSON files.

    Methods
    -------
    supports(source)
        Returns True for any path ending in .json.
    load(source)
        Reads the JSON file at source into a DataFrame.
    """

    def supports(self, source: Path) -> bool:
        """
        Return True if source ends with .json.

        Parameters
        ----------
        source : Path
            Path to evaluate.

        Returns
        -------
        bool
            True if source ends with .json, False otherwise.
        """
        return str(source).lower().endswith(".json")

    def load(self, source: Path) -> pd.DataFrame:
        """
        Read the JSON file at source into a DataFrame.

        Parameters
        ----------
        source : Path
            Path to the JSON file to load.

        Returns
        -------
        pd.DataFrame
            Contents of the JSON file as a DataFrame.
        """
        return pd.read_json(source)