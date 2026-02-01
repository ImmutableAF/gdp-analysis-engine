import argparse
from pathlib import Path
from typing import Optional


def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments and returns a namespace.
    """
    parser = argparse.ArgumentParser(description="GDP Data Pipeline")

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to CSV, XLSX, or other supported file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (writes debug/info to log file)"
    )

    return parser.parse_args()
