from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class BaseConfig:
    data_directory: Path
    default_file: str
    log_directory: Path
    max_log_size: int
    logging_level: str

@dataclass(frozen=True)
class QueryConfig:
    region: Optional[str]
    startYear: Optional[int]  
    endYear: Optional[int]    
    country: Optional[str]
    operation: Optional[str]