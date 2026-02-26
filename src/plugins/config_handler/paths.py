"""
Purpose:
Resolves absolute paths to the base and query JSON config files relative to the project root.

Description:
Derives all paths from this file's own location on disk, walking three levels up
to reach the project root. This means config files are always found correctly
regardless of where the application is launched from.

Functions
---------
get_config_paths()
    Return both config file paths as a tuple.
get_base_config_path()
    Return the path to base_config.json.
get_query_config_path()
    Return the path to query_config.json.

Notes
-----
- Project root is resolved as three levels up from this file's location.
- All functions derive their result from get_config_paths() — no paths are hardcoded twice.
"""

from pathlib import Path
from typing import Tuple


def get_config_paths() -> Tuple[Path, Path]:
    """
    Return absolute paths to both config files as a tuple.

    Returns
    -------
    Tuple[Path, Path]
        (base_config_path, query_config_path) resolved from the project root.
    """
    base_dir = Path(__file__).parent.parent.parent

    base_config_path = base_dir / "base_config.json"
    query_config_path = base_dir / "query_config.json"

    return base_config_path, query_config_path


def get_base_config_path() -> Path:
    """
    Return the absolute path to base_config.json.

    Returns
    -------
    Path
        Absolute path to the base configuration file.
    """
    return get_config_paths()[0]


def get_query_config_path() -> Path:
    """
    Return the absolute path to query_config.json.

    Returns
    -------
    Path
        Absolute path to the query configuration file.
    """
    return get_config_paths()[1]