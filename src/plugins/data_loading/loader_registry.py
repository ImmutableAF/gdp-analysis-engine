import logging
from typing import List
from pathlib import Path
from .loader_interface import DataLoader
import logging
logger = logging.getLogger(__name__)

_loaders: List[DataLoader] = []

def register_plugin(cls):
    if issubclass(cls, DataLoader) and cls is not DataLoader:
        logger.debug(f"added {cls} to loaders list")
        _loaders.append(cls())
    return cls

def get_loader(source: Path) -> DataLoader:
    for loader in _loaders:
        if loader.supports(source):
            logger.info(f"{loader} supports {source}")
            return loader
    raise ValueError(f"no loader supports {source}")