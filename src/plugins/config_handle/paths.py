"""
Purpose:
Resolves absolute paths to the base, query, analytics, and ports JSON config
files relative to the project root.

Description:
Derives all paths from this file's own location on disk, walking three levels up
to reach the project root. This means config files are always found correctly
regardless of where the application is launched from.

Functions
---------
get_config_paths()
    Return base and query config file paths as a tuple.
get_base_config_path()
    Return the path to base_config.json.
get_query_config_path()
    Return the path to query_config.json.
get_analytics_config_path()
    Return the path to analytics_config.json.
get_ports_config_path()
    Return the path to ports_config.json.
"""

from pathlib import Path
from typing import Tuple


def _src_dir() -> Path:
    """Return the absolute path to the src/ directory."""
    return Path(__file__).parent.parent.parent.parent / "src"


def get_config_paths() -> Tuple[Path, Path]:
    """
    Return absolute paths to base and query config files as a tuple.

    Returns
    -------
    Tuple[Path, Path]
        (base_config_path, query_config_path) resolved from the project root.
    """
    src = _src_dir()
    return src / "configs" / "base_config.json", src / "configs" / "query_config.json"


def get_base_config_path() -> Path:
    """Return the absolute path to base_config.json."""
    return get_config_paths()[0]


def get_query_config_path() -> Path:
    """Return the absolute path to query_config.json."""
    return get_config_paths()[1]


def get_analytics_config_path() -> Path:
    """
    Return the absolute path to analytics_config.json.

    Resolved as src/analytics_config.json relative to the project root,
    sitting alongside base_config.json and query_config.json.

    Returns
    -------
    Path
        Absolute path to the analytics configuration file.
    """
    return _src_dir() / "configs" / "analytics_config.json"


def get_ports_config_path() -> Path:
    """
    Return the absolute path to ports_config.json.

    Resolved as src/ports_config.json relative to the project root,
    sitting alongside all other config files.

    Returns
    -------
    Path
        Absolute path to the ports configuration file.
    """
    return _src_dir() / "configs" / "ports_config.json"
