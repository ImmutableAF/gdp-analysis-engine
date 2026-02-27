"""
Purpose:
Auto-discovers and imports all loader plugins, then loads the correct one.

Description:
The data_loaders package is scanned and every module in it is dynamically 
imported. Each import triggers a decorator that silently populates the 
loader registry as a side effect. After that the supported loader is loaded.

Functions
---------
_import_plugins()
    Internal — scan and import all modules in data_loaders on first call only.
load_data(source)
    Trigger plugin discovery if needed, then load the file at source.

Notes
-----
- A module-level _loaded flag ensures the discovery runs exactly once per interpreter session.
- Plugins that fail to import are logged and silently skipped.
- load_data() raises ValueError if no registered loader supports the file.
"""

import logging
from pathlib import Path
from pkgutil import iter_modules
from importlib import import_module

from pandas import DataFrame

from .. import data_loaders
from .loader_registry import get_loader

import logging
logger = logging.getLogger(__name__)

_loaded = False


def _import_plugins():
    """
    Scan and import all modules in the data_loaders on first call only.

    Walks the package, builds a fully qualified module path for each
    module found, and imports it dynamically. Flips _loaded to True after
    all modules are processed. Failed imports are logged and silently skipped.
    """
    global _loaded
    if _loaded:
        return
    for _, name, _ in iter_modules(data_loaders.__path__):
        try:
            logger.debug(f"Trying to import plugin {data_loaders.__name__}.{name}")
            import_module(f"{data_loaders.__name__}.{name}")
            logger.debug(f"Imported pluggin {name} successfully")
        except Exception as e:
            logger.error(f"Failed to import plugin {name}: {e}", exc_info=True)
            pass
    _loaded = True


def load_data(source: Path) -> DataFrame:
    """
    Trigger plugin discovery if needed, then load the file at source.

    Parameters
    ----------
    source : Path
        Path to the file to load.

    Returns
    -------
    DataFrame
        Loaded data as a DataFrame.

    Raises
    ------
    ValueError
        If no registered loader supports the given file.

    Examples
    --------
    >>> df = load_data(Path("data/gdp_data.xlsx"))
    """
    _import_plugins()
    loader = get_loader(source)
    logger.info(f"Using loader {loader.__class__.__name__} for {source}")
    return loader.load(source)