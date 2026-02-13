from pathlib import Path
import pandas as pd

from .loader_registry import LoaderRegistry

def load_data(file_path: Path) -> pd.DataFrame:
    """
    Load data file via LoaderRegistry plugin system.
    
    Parameters
    ----------
    file_path : Path
        Data file path (CSV, Excel, etc.)
    
    Returns
    -------
    pd.DataFrame
        Loaded data in wide format
    
    Raises
    ------
    ValueError
        If no loader supports file type
    FileNotFoundError
        If file doesn't exist
    
    Examples
    --------
    >>> df = load_data(Path("data/gdp_data.csv"))
    >>> print(df.shape)
    (266, 65)
    """
    registry = LoaderRegistry()
    df = registry.load(file_path)
    return df