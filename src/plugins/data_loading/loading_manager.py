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
    global _loaded
    if _loaded:
        return
    for _, name, _ in iter_modules(data_loaders.__path__):
        try:
            logging.debug(f"Trying to import plugin {data_loaders.__name__}.{name}")
            import_module(f"{data_loaders.__name__}.{name}")
            logging.debug(f"Imported pluggin {name} successfully")
        except Exception as e:
            logging.error(f"Failed to import plugin {name}: {e}", exc_info=True)
            pass
    _loaded = True

def load_data(source: Path) -> DataFrame:
    _import_plugins()
    loader = get_loader(source)
    logger.info(f"Using loader {loader.__class__.__name__} for {source}")
    return loader.load(source)