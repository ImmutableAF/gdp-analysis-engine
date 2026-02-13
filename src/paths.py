from pathlib import Path
from typing import Tuple

def get_config_paths() -> Tuple[Path, Path]:
    """
    Resolve configuration file paths relative to script location.
    
    Returns
    -------
    Tuple[Path, Path]
        (base_config_path, query_config_path)
    
    Notes
    -----
    Paths resolved as: script_dir/data/configs/*.json
    
    Examples
    --------
    >>> base_path, query_path = get_paths()
    >>> print(base_path.name)
    base_config.json
    """
    base_dir = Path(__file__).parent.parent

    base_config_path = base_dir / "data" / "configs" / "base_config.json"
    query_config_path = base_dir / "data" / "configs" / "query_config.json"

    return base_config_path, query_config_path

def get_base_config_path() -> Path:
    return get_config_paths()[0]

def get_query_config_path() -> Path:
    return get_config_paths()[1]