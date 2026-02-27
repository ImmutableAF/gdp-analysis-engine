"""
Purpose:
Abstract base class that every data loader plugin must implement.

Description:
Defines the policies (supports / load) that all concrete loaders must satisfy. 
Any new file format is supported by simply subclassing DataLoader and implementing
both methods.

Classes
-------
DataLoader
    Abstract base class for all data loader plugins.

Notes
-----
- Concrete loaders must implement both supports() and load().
- supports() should check file extension only — no file I/O.
- load() is only called if supports() returns True.
"""

from pathlib import Path
from abc import ABC, abstractmethod

from pandas import DataFrame


class DataLoader(ABC):
    """
    Abstract base class for all data loader plugins.

    Subclass this and implement supports() and load() to add
    support for a new file format.

    Methods
    -------
    supports(filepath)
        Return True if this loader can handle the given file.
    load(filepath)
        Read the file and return its contents as a DataFrame.

    Examples
    --------
    >>> class CSVLoader(DataLoader):
    ...     def supports(self, filepath: Path) -> bool:
    ...         return filepath.suffix.lower() == ".csv"
    ...
    ...     def load(self, filepath: Path) -> DataFrame:
    ...         return pd.read_csv(filepath)
    """

    @abstractmethod
    def supports(filepath: Path):
        """
        Return True if this loader can handle the given file.

        Should be based on file extension or name only — never open
        or read the file inside this method.

        Parameters
        ----------
        filepath : Path
            Path to the file being evaluated.

        Returns
        -------
        bool
            True if this loader can process the file, False otherwise.
        """
        pass

    @abstractmethod
    def load(filepath: Path) -> DataFrame:
        """
        Read the file at filepath and return its contents as a DataFrame.

        Parameters
        ----------
        filepath : Path
            Path to the file to load.

        Returns
        -------
        DataFrame
            Loaded data with consistent column schema expected by the pipeline.

        Raises
        ------
        FileNotFoundError
            If the file does not exist at the given path.
        ValueError
            If the file contents cannot be parsed into a valid DataFrame.
        """
        pass