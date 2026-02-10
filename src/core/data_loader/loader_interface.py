"""
Data Loader Abstract Interface
===============================

Defines the abstract base class for data loading plugins. All concrete loaders
must implement the supports() and load() methods to participate in the plugin
architecture.

Classes
-------
DataLoader
    Abstract base class for file loading plugins

See Also
--------
loader_registry.LoaderRegistry : Plugin discovery and orchestration
loaders.csv_loader.CSVLoader : CSV file loader implementation
loaders.excel_loader.ExcelLoader : Excel file loader implementation

Notes
-----
Concrete implementations must:
- Inherit from DataLoader
- Implement supports() and load() methods  
- Be placed in loaders/ subpackage for auto-discovery
- Return pandas DataFrames with consistent schemas

Plugin discovery uses Python's abc module for compile-time interface enforcement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd


class DataLoader(ABC):
    """
    Abstract base class for data loading plugins.
    
    Defines the two-method contract (supports/load) that enables automatic
    plugin discovery and delegation via LoaderRegistry.
    
    Methods
    -------
    supports(file_path)
        Check if this loader can handle the given file
    load(file_path)
        Load file and return pandas DataFrame
    
    See Also
    --------
    LoaderRegistry : Manages plugin discovery and selection
    
    Notes
    -----
    Loaders must be in loaders/ subpackage for auto-discovery.
    Use file extensions or metadata in supports() - avoid file I/O.
    
    Examples
    --------
    >>> class JSONLoader(DataLoader):
    ...     def supports(self, file_path: Path) -> bool:
    ...         return file_path.suffix.lower() == '.json'
    ...     
    ...     def load(self, file_path: Path) -> pd.DataFrame:
    ...         return pd.read_json(file_path)
    """
    
    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """
        Determine if this loader can process the specified file.
        
        Used by LoaderRegistry during first-match selection. Should be fast
        and non-invasive (check extension, not file contents).
        
        Parameters
        ----------
        file_path : Path
            File path to evaluate
        
        Returns
        -------
        bool
            True if loader can process file, False otherwise
        
        Examples
        --------
        >>> loader = CSVLoader()
        >>> loader.supports(Path("data.csv"))
        True
        """
        pass

    @abstractmethod
    def load(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from file into pandas DataFrame.
        
        Performs file reading and parsing. Returned DataFrame should have
        consistent schema for pipeline compatibility.
        
        Parameters
        ----------
        file_path : Path
            File path to load
        
        Returns
        -------
        pd.DataFrame
            Loaded data with Country/Region and year columns
        
        Raises
        ------
        FileNotFoundError
            If file does not exist
        ValueError
            If file format is invalid
        PermissionError
            If file is not readable
        
        Examples
        --------
        >>> loader = CSVLoader()
        >>> df = loader.load(Path("gdp_data.csv"))
        >>> print(df.columns[:3])
        Index(['Country', 'Region', '1960'])
        """
        pass