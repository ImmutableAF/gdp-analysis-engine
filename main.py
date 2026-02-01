import logging
from pathlib import Path

from config import load_config
from logging_factory import create_file_logger
from pipeline import run_pipeline
from arg_manager import parse_args


def main() -> None:
    # parses compile time arguments into easily accessable units like .file for path
    args = parse_args()

    # load configs
    base_dir = Path(__file__).parent
    config = load_config(base_dir)

    # create a logger with loaded configs and debug flag bool 
    # AND then give ownership to main as object
    create_file_logger(config, args.debug)
    logger = logging.getLogger("main")

    # use default path if no path is given as argument
    file_path = Path(args.file) if args.file else config.default_data_file
    logger.debug(f"Resolved file path: {file_path}")

    # main processing pipeline
    try:
        run_pipeline(file_path)
    except Exception as e:
        logger.critical(e)


if __name__ == "__main__":
    main()
