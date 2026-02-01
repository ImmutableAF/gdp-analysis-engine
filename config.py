from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    default_data_file: Path
    log_dir: Path
    debug_log_file: Path
    prod_log_file: Path
    max_log_size_bytes: int
    backup_count: int


def load_config(base_dir: Path) -> AppConfig:
    log_dir = base_dir / "logs"

    return AppConfig(
        default_data_file=base_dir / "gdp_with_continent_filled.csv",
        log_dir=log_dir,
        debug_log_file=log_dir / "debug.log",
        prod_log_file=log_dir / "app.log",
        max_log_size_bytes=5 * 1024 * 1024,  # 5 MB
        backup_count=5,
    )
