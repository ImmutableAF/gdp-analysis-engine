"""
Data Loader Plugin Registry
============================

Implements automatic plugin discovery and file loading delegation. Scans the
loaders subpackage at initialization, discovers DataLoader implementations,
and routes load requests to appropriate loaders.

Plugin Discovery Flow:
1. Scan loaders/ subpackage for modules
2. Import modules dynamically
3. Identify DataLoader subclasses via inspection
4. Instantiate and register loaders
5. Use first-match strategy in load()

Classes
-------
LoaderRegistry
    Plugin discovery and loading orchestrator

See Also
--------
loader_interface.DataLoader : Abstract loader interface
loaders : Subpackage with concrete implementations

Notes
-----
Uses pkgutil and inspect for runtime discovery. Follows Open/Closed Principle -
extensible without modification. First-match strategy means loader order matters
if multiple loaders support the same file type.

Examples
--------
>>> registry = LoaderRegistry()
>>> df = registry.load(Path("data/gdp_data.csv"))
>>> print(df.shape)
(266, 65)
"""

import pkgutil
import inspect
import importlib
import pandas as pd
from pathlib import Path
from typing import List

from .loader_interface import DataLoader
from . import loaders


class LoaderRegistry:
    """
    Automatic plugin discovery and file loading manager.
    
    Discovers DataLoader implementations in loaders/ subpackage during
    initialization. Routes load() requests to first matching loader.
    
    Attributes
    ----------
    _loaders : List[DataLoader]
        Registered loader instances
    
    Methods
    -------
    load(file_path)
        Load file using appropriate plugin
    
    Raises
    ------
    ValueError
        If no loader supports the file type
    
    See Also
    --------
    DataLoader : Loader interface
    
    Notes
    -----
    Discovery occurs during __init__(), making it moderately expensive.
    Reuse registry instances when loading multiple files.
    
    Loaders must have parameter-free constructors for instantiation.
    First-match strategy: first discovered loader for a type wins.
    
    Examples
    --------
    >>> registry = LoaderRegistry()
    >>> df = registry.load(Path("gdp_data.csv"))
    >>> print(f"Loaded {len(df)} rows")
    Loaded 266 rows
    """
    
    def __init__(self) -> None:
        """
        Initialize registry and discover loader plugins.
        
        Triggers automatic discovery: scans loaders/ subpackage, identifies
        DataLoader subclasses, and instantiates them.
        
        Raises
        ------
        ImportError
            If loader module cannot be imported
        TypeError
            If loader class cannot be instantiated
        """
        self._loaders: List[DataLoader] = []
        self._discover_plugins()
    
    def _discover_plugins(self) -> None:
        """
        Discover and register DataLoader plugins in loaders/ subpackage.
        
        Discovery algorithm:
        1. Iterate modules in loaders.__path__ (via pkgutil)
        2. Import each module dynamically
        3. Inspect members for DataLoader subclasses
        4. Filter out abstract DataLoader base class
        5. Instantiate and append to _loaders
        
        Raises
        ------
        ImportError
            If module import fails
        TypeError
            If loader instantiation fails
        
        Notes
        -----
        Called automatically by __init__(). Modifies _loaders in place.
        Uses inspect.isclass and issubclass for filtering.
        """
        for module_info in pkgutil.iter_modules(loaders.__path__):
            module = importlib.import_module(f"{loaders.__name__}.{module_info.name}")

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, DataLoader) and obj is not DataLoader:
                    self._loaders.append(obj())

    def load(self, file_path: Path) -> pd.DataFrame:
        """
        Load file using first compatible loader plugin.
        
        Iterates registered loaders, calling supports() until finding a match.
        Delegates to matching loader's load() method.
        
        Parameters
        ----------
        file_path : Path
            File to load (relative or absolute path)
        
        Returns
        -------
        pd.DataFrame
            Loaded data (schema depends on loader implementation)
        
        Raises
        ------
        ValueError
            If no loader supports file type (includes file extension in message)
        FileNotFoundError
            If file does not exist (from delegated loader)
        PermissionError
            If file is not readable (from delegated loader)
        
        See Also
        --------
        DataLoader.supports : File type detection
        DataLoader.load : File loading implementation
        
        Notes
        -----
        First-match strategy: loader order affects selection.
        No caching: each call performs fresh file read.
        
        Examples
        --------
        >>> registry = LoaderRegistry()
        >>> df = registry.load(Path("data.csv"))
        >>> print(df.shape)
        (266, 65)
        
        >>> try:
        ...     df = registry.load(Path("data.pdf"))
        ... except ValueError as e:
        ...     print(e)
        No loader found for: .pdf
        """
        for loader in self._loaders:
            if loader.supports(file_path):
                df = loader.load(file_path)
                return df

        raise ValueError(f"No loader found for: {file_path.suffix}")