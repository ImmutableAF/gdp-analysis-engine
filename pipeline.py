from pathlib import Path
import logging
from loader_registry import LoaderRegistry


def run_pipeline(file_path: Path) -> None:
    logger = logging.getLogger("pipeline")

    registry = LoaderRegistry()
    df = registry.load(file_path)

    logger.info("Data loaded successfully")
    logger.debug(f"Shape: {df.shape}")
