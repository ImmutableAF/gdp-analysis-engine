from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass(frozen=True)
class BaseConfig:
    data_dir: Path
    default_file: str
    log_dir: Path
    max_log_size_bytes: int
    default_logging_level: str

@dataclass(frozen=True)
class QueryConfig:
    region: Optional[str]
    year: Optional[int]
    country: Optional[str]
    operation: str
    dashboard_charts: List[str]
