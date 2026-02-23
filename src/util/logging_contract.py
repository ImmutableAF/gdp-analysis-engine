from pathlib import Path
from typing import Protocol

class LogPolicy(Protocol):
    log_dir: Path
    max_log_size: int