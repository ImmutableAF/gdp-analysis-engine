"""
Purpose:
Defines and parses CLI arguments for the application.

Description:
Builds an ArgumentParser with two arguments — a debug flag and a file path —
and returns the parsed result ready to use in the rest of the application.

Functions
---------
parse_cli_args(description, file_path)
    Build and parse the argument parser, returning the parsed namespace.

Notes
-----
- --debug sets a boolean flag for enabling debug mode.
- --fp accepts a file path, falling back to the file_path parameter if not provided.

Examples
--------
>>> args = parse_cli_args(description="GDP Query CLI", file_path=Path("data/gdp_data.xlsx"))
>>> args.debug
False
>>> args.file_path
PosixPath('data/gdp_data.xlsx')
"""

import argparse
from pathlib import Path
from typing import Optional


def parse_cli_args(
        description: str = "CLI",
        file_path: Optional[Path] = None
):
    """
    Build and parse CLI arguments, returning the parsed namespace.

    Parameters
    ----------
    description : str
        Description string shown in the help message. Default is "CLI".
    file_path : Path or None
        Default file path used if --fp is not provided on the command line.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with attributes: debug (bool), file_path (Path or None).

    Examples
    --------
    >>> args = parse_cli_args(description="GDP Query CLI", file_path=Path("data/gdp_data.xlsx"))
    >>> args.debug
    False
    >>> args.file_path
    PosixPath('data/gdp_data.xlsx')    
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "--fp",
        type=Path,
        dest="file_path",
        metavar="PATH",
        default=file_path,
        help="Input file path"
    )

    return parser.parse_args()