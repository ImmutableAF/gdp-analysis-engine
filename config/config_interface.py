from dataclasses import dataclass
from pathlib import Path
from typing import list, Optional

@dataclass(frozen=True)
class default_config:
    default_dir: Path
    default_file: str
    default_log_dir: Path
    max_log_size: int
    default_log_level: str

@dataclass(frozen=True)
class setting_config:
    region: Optional[str]
    year: Optional[int]
    country: Optional[str]
    operation: str
    dashboard_chart: list[str]