import logging
from pathlib import Path

from .plugins.data_loading import load_data
from .plugins.config_handler import get_base_config, get_query_config
from .core.engine import run_pipeline

if __name__ == "__main__":
    base_config = get_base_config()
    test_path = Path(base_config.data_dir) / base_config.data_filename
    filepath = test_path if test_path.exists() and test_path.is_file() else Path("data/gdp_with_continent_filled.xlsx")

    try:
        logging.info(f"trying to load data from {filepath}")
        df = load_data(filepath)
    except Exception as e:
        logging.critical(f"Failed to load data: {e}")
        raise
    else:
        logging.info(f"data loaded succesfully without any exception occurrence")
        print(run_pipeline(filters=get_query_config(df), df=df, inLongFormat=True))
        print(run_pipeline(filters=get_query_config(df), df=df))