import logging
from typing import List
from pathlib import Path

from .loader_interface import DataLoader

_loaders: List[DataLoader] = []

def register_plugin(cls):
    if issubclass(cls, DataLoader) and cls is not DataLoader:
        logging.debug(f"{cls} added to loaders list")
        _loaders.append(cls())
    return cls

def get_loader(source: Path) -> DataLoader:
    for loader in _loaders:
        if loader.supports(source):
            logging.info(f"{loader} supports {source}")
            return loader
    raise ValueError(f"No loader supports {source}")
