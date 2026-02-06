import argparse
from pathlib import Path

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for GDP data processing."""

    parser = argparse.ArgumentParser(description="Process GDP data from CSV, XLSX, or other supported file")

    parser.add_argument(
        "file",
        type=Path,
        help="Path to CSV, XLSX, or other supported file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (writes debug/info to log file)"
    )

    return parser.parse_args()