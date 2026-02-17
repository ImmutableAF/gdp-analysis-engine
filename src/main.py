import logging
from pathlib import Path

from .plugins.data_loading import load_data
from .plugins.config_handler import get_base_config, get_query_config
from .core.engine import run_pipeline
from .util.logging_setup import initialize_logging
if __name__ == "__main__":
    base_config = get_base_config()
    initialize_logging(base_config, debug=True)
    logger = logging.getLogger(__name__)
    test_path = Path(base_config.data_dir) / base_config.data_filename
    filepath = test_path if test_path.exists() and test_path.is_file() else Path("data/gdp_with_continent_filled.xlsx")

    try:
        logger.info(f"trying to load data from {filepath}")
        df = load_data(filepath)
    except Exception as e:
        logger.critical(f"Failed to load data: {e}")
        raise
    else:
        logger.info(f"data loaded succesfully without any exception occurrence")
        print(run_pipeline(filters=get_query_config(df), df=df, inLongFormat=True))
        print(run_pipeline(filters=get_query_config(df), df=df))