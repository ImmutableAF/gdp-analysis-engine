import logging
from pathlib import Path

from .plugins.data_loading.loading_manager import load_data
from .plugins.config_handler import get_base_config, get_query_config
from .core.engine import run_pipeline
from .util.logging_setup import initialize_logging
from .util.cli_parser import parse_cli_args
if __name__ == "__main__":
    base_config = get_base_config()
    initialize_logging(base_config, debug=True)
    logger = logging.getLogger(__name__)

    test_path = Path(base_config.data_dir) / base_config.data_filename
    filepath = test_path if test_path.exists() and test_path.is_file() else Path("data/gdp_with_continent_filled.xlsx")

    logger.info(f"Selected data file: {filepath}")
    args = parse_cli_args()
    print(args)
    try:
        logger.info(f"trying to load data from {filepath}")
        df = load_data(filepath)
    except Exception as e:
        logger.critical(f"failed to load data: {e}")
        raise
    else:
        logger.info(f"data loaded succesfully")
        print(run_pipeline(filters=get_query_config(df), df=df, inLongFormat=True))
        print(run_pipeline(filters=get_query_config(df), df=df))