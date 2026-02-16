import logging
from pathlib import Path
from pkgutil import iter_modules
from importlib import import_module

from pandas import DataFrame

from src.plugins import data_loaders
from .loader_registry import get_loader

_loaded = False

def _import_plugins():
    global _loaded
    if _loaded:
        return
    for _, name, _ in iter_modules(data_loaders.__path__):
        try:
            logging.debug(f"trying to import {data_loaders.__name__}.{name}")
            import_module(f"{data_loaders.__name__}.{name}")
            logging.debug(f"imported succesfully")
        except Exception as e:
            logging.error(f"plugin import threw {e}")
            pass
    _loaded = True

def load_data(source: Path) -> DataFrame:
    _import_plugins()
    return get_loader(source).load(source)
