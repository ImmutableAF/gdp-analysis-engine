import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import logging
logger = logging.getLogger(__name__)

from plugins.data_loading.loading_manager import load_data
from plugins.config_handler import get_base_config, get_query_config
from plugins.outputs import make_sink, OutputMode
from core.data_cleaning import clean_gdp_data
from core.engine import run_pipeline
from util.logging_setup import initialize_logging
from util.cli_parser import parse_cli_args
from src.core.metadata import get_metadata


def main():
    base_config = get_base_config()
    initialize_logging(base_config, debug=True)

    args = parse_cli_args()
    filepath = (
        args.file_path
        if (args.file_path and args.file_path.is_file())
        else Path(base_config.data_dir) / base_config.data_filename
    )

    try:
        raw_df = load_data(filepath)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Unsupported file type: {filepath.suffix}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        sys.exit(1)
    

    df = clean_gdp_data(raw_df)  # once, here, never again

    query_config = get_query_config(df)  # metadata reads clean df
    metadata = get_metadata(df)

    # provider: callable that re-runs pipeline on demand
    def provider():
        return run_pipeline(df=df, filters=query_config, inLongFormat=True)

    mode = OutputMode(base_config.output_mode)  # "ui" or "cli" from config
    sink = make_sink(mode, metadata, df, query_config, provider)
    sink.start()  # UI → spawns streamlit / CLI → runs directly


if __name__ == "__main__":
    main()
