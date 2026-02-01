import logging
from pathlib import Path
from typing import Tuple, Any

from config_loader import load_base_config, load_query_config
from logging_factory import create_file_logger
from pipeline.pipeline import run_pipeline
from utils.arg_manager import parse_args
from config_models import BaseConfig, QueryConfig

# main.py
def load_metadata() -> Tuple[BaseConfig, QueryConfig, Any]:
    args = parse_args()
    # Resolve the directory where main.py is located
    base_dir = Path(__file__).resolve().parent
    
    # Re-insert the "config" folder into the path
    base_config_path = base_dir / "config" / "base_config.json"
    query_config_path = base_dir / "config" / "query_config.json"

    # Defensive check: provide a clear error if the folder is missing
    if not base_config_path.exists():
        raise FileNotFoundError(f"Expected config file at {base_config_path}. Check your folder structure.")

    base_config = load_base_config(base_config_path)
    query_config = load_query_config(query_config_path)
    
    return base_config, query_config, args

def run_query(base_config: BaseConfig, query_config: QueryConfig, args: Any):
    # Ensure create_file_logger uses settings from base_config
    create_file_logger(base_config, args.debug)
    logger = logging.getLogger("query")
    
    # Correctly resolve the data file path
    file_path = Path(args.file) if args.file else Path(base_config.data_dir) / base_config.default_file
    
    return run_pipeline(file_path, query_config)