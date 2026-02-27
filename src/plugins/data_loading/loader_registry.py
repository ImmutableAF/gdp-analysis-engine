"""
Purpose:
A module-level plugin registry that maps file paths to the correct DataLoader.

Description:
At module level, a single private list (_loaders) is created and stays alive
for the entire interpreter session. When a loader class is decorated with
@register_plugin, one instance of that class is immediately appended to that
list. get_loader() then walks the list in the order loaders were registered
and hands back the first one that supports the given file.

Functions
---------
register_plugin(cls)
    Decorator that instantiates a DataLoader subclass and appends it to _loaders.
get_loader(source)
    Walk _loaders in order and return the first loader that supports the file.

Notes
-----
- _loaders is populated at import time via @register_plugin decorators.
- Loaders are matched in registration order — first match wins.
- get_loader() raises ValueError if no registered loader supports the file.
"""

import logging
from typing import List
from pathlib import Path
from .loader_interface import DataLoader
import logging
logger = logging.getLogger(__name__)

_loaders: List[DataLoader] = []


def register_plugin(cls):
    """
    Decorator that instantiates a DataLoader subclass and appends it to _loaders.

    Silently ignores the class if it is DataLoader itself or not a subclass of it.

    Parameters
    ----------
    cls : type
        The class being decorated. Must be a concrete subclass of DataLoader.

    Returns
    -------
    type
        The original class, unchanged.
    """
    if issubclass(cls, DataLoader) and cls is not DataLoader:
        logger.debug(f"added {cls} to loaders list")
        _loaders.append(cls())
    return cls


def get_loader(source: Path) -> DataLoader:
    """
    Walk _loaders in order and return the first loader that supports the file.

    Parameters
    ----------
    source : Path
        Path to the file that needs to be loaded.

    Returns
    -------
    DataLoader
        First registered loader whose supports() returns True for source.

    Raises
    ------
    ValueError
        If no registered loader supports the given file.
    """
    for loader in _loaders:
        if loader.supports(source):
            logger.info(f"{loader} supports {source}")
            return loader
    raise ValueError(f"no loader supports {source}")