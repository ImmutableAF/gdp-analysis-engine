"""
Data Loader Package
===================

Implements a dynamic plugin-based system for loading data from various file formats.
New file format support can be added by creating loader classes without modifying
the core registry code.

Modules
-------
loader_interface
    Abstract base class defining the loader contract
loader_registry
    Registry that discovers and manages loader plugins
loaders
    Package containing concrete loader implementations

Classes
-------
DataLoader
    Abstract base class for all data loaders
LoaderRegistry
    Main registry for discovering and using loaders

Architecture
------------
The package uses the **Plugin Pattern** for extensibility:

::

    LoaderRegistry
         ├── discovers loaders via introspection
         ├── CSVLoader (supports .csv files)
         └── ExcelLoader (supports .xlsx, .xls files)

Plugin Discovery
----------------
The registry automatically discovers loader plugins at initialization by:

1. Scanning the ``loaders`` subpackage
2. Importing all modules in that package
3. Inspecting for classes that inherit from ``DataLoader``
4. Instantiating and registering discovered loaders

This allows adding new format support by simply creating a new loader class
in the ``loaders`` package without any registration code.

Loader Contract
---------------
All loaders must implement the ``DataLoader`` interface:

- **supports(file_path)**: Return True if loader can handle the file
- **load(file_path)**: Load file and return pandas DataFrame

The registry queries loaders in registration order and uses the first
matching loader.

Adding New Loaders
------------------
To add support for a new file format:

1. Create a new file in ``loaders/`` (e.g., ``json_loader.py``)
2. Implement a class inheriting from ``DataLoader``
3. Implement ``supports()`` and ``load()`` methods
4. The registry will automatically discover it

Example new loader::

    from pathlib import Path
    import pandas as pd
    from ..loader_interface import DataLoader

    class JSONLoader(DataLoader):
        def supports(self, file_path: Path) -> bool:
            return file_path.suffix.lower() == '.json'
        
        def load(self, file_path: Path) -> pd.DataFrame:
            return pd.read_json(file_path)

Error Handling
--------------
ValueError
    Raised when no loader supports the requested file format
FileNotFoundError
    Raised when the file path doesn't exist (propagated from loaders)
pandas errors
    Various pandas exceptions may be raised during file parsing

Examples
--------
Basic usage:

>>> from pathlib import Path
>>> from src.core.data_loader import LoaderRegistry
>>>
>>> registry = LoaderRegistry()
>>> df = registry.load(Path("data/gdp.csv"))

The registry automatically selects the appropriate loader based on file extension.

Check supported formats:

>>> registry = LoaderRegistry()
>>> # CSV and Excel files are supported by default
>>> csv_df = registry.load(Path("data.csv"))
>>> excel_df = registry.load(Path("data.xlsx"))

See Also
--------
loader_interface.DataLoader : Abstract base class for loaders
loader_registry.LoaderRegistry : Main registry class
loaders : Package containing concrete loader implementations

Notes
-----
The loader registry is initialized once and discovers plugins at that time.
Loaders added to the ``loaders`` package after initialization won't be
available until the registry is recreated.

For performance, the registry could be cached as a singleton, but the
current implementation creates fresh instances to ensure all plugins
are discovered.
"""

from .loader_interface import DataLoader
from .loader_registry import LoaderRegistry

__all__ = [
    'DataLoader',
    'LoaderRegistry',
]