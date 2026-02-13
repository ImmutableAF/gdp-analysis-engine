import logging
from pathlib import Path

from src.core.data_loading import load_data
from .core.config_loading import get_config


config = get_config()
test_path = Path(config["data_dir"]) / config["data_filename"]
filepath = test_path if test_path.exists() and test_path.is_file() else Path("data/gdp_with_continent_filled.xlsx")

try:
    logging.info(f"trying to load data from {filepath}")
    df = load_data(filepath)
except Exception as e:
    logging.critical(f"Failed to load data: {e}")
    raise
else:
    logging.info(f"data loaded succesfully without any exception occurrence")
    print(df)