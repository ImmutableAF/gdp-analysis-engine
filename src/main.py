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

    args = parse_cli_args()
    print(args)
    test_path = args.filePath
    filepath = test_path if test_path.exists() and test_path.is_file() else Path(base_config.data_dir) / base_config.data_filename

    logger.info(f"Selected data file: {filepath}")
    try:
        logger.info(f"trying to load data from {filepath}")
        df = load_data(filepath)
    except Exception as e:
        logger.critical(f"failed to load data: {e}")
        raise
    else:
        logger.info(f"data loaded succesfully")
        logger.info(f"trying to load query config")
        query_config = get_query_config(df)
        logger.info(f"query config loaded")
        logger.info(f"running first pipeline")
        print(run_pipeline(filters=query_config, df=df, inLongFormat=True))
        logger.info(f"running second pipeline")
        print(run_pipeline(filters=query_config, df=df))