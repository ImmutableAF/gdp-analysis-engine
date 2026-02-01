import logging
from pathlib import Path
from data_loader import DataLoader


def run_pipeline(file_path: Path) -> None:
    logger = logging.getLogger("pipeline")

    logger.info("Pipeline started")

    loader = DataLoader(file_path)
    df = loader.load()

    logger.info("Data loaded successfully")
    logger.debug(f"Shape: {df.shape}")
    logger.debug(f"Columns: {list(df.columns)}")
