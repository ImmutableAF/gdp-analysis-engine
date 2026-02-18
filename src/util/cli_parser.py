"""
CLI Argument Parser
===================

Command-line argument parsing for non-UI mode execution.

Functions
---------
parse_cli_args()
    Parse command-line arguments for debug mode and file path

Examples
--------
>>> args = parse_cli_args()
>>> if args.debug:
...     print("Debug mode enabled")
>>> if args.fpath:
...     print(f"Loading file: {args.fpath}")
"""

import argparse
from pathlib import Path
from typing import Optional

def parse_cli_args(
        description: str = "CLI",
        file_path: Optional[Path] = None
):
    """
    Parse command-line arguments.
    
    Returns
    -------
    argparse.Namespace
        Parsed arguments with attributes:
        - debug (bool): Debug mode flag
        - fpath (str or None): Input file path
    
    Notes
    -----
    Arguments:
    - --debug: Enable debug logging (flag, no value needed)
    - -fpath PATH: Override default input file path
    
    Examples
    --------
    Command line usage:
    $ python main.py --debug -fpath data/custom.csv
    
    In code:
    >>> args = parse_cli_args()
    >>> print(args.debug)
    True
    >>> print(args.fpath)
    data/custom.csv
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "--file",
        type=Path,
        metavar="PATH",
        default=file_path,
        help="Input file path"
    )

    return parser.parse_args()