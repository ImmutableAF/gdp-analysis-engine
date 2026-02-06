import argparse

def parse_cli_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "-fpath",
        metavar="PATH",
        help="Input file path"
    )

    return parser.parse_args()