import argparse
import logging
from pathlib import Path

from config import load_config
from logging_factory import create_file_logger
from pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="GDP data pipeline")
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to CSV or XLSX file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    base_dir = Path(__file__).parent
    config = load_config(base_dir)

    create_file_logger(config, args.debug)

    logger = logging.getLogger("main")

    file_path = Path(args.file) if args.file else config.default_data_file
    logger.debug(f"Resolved file path: {file_path}")

    try:
        run_pipeline(file_path)

    except Exception as e:
        logger.critical(e)


if __name__ == "__main__":
    main()
