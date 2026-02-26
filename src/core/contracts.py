from typing import Protocol
import pandas as pd

class DataFrameLoadable(Protocol):
    def load(self, source: str) -> pd.DataFrame:
        ...

class DataFrameOutput(Protocol):
    def write(self, df: pd.DataFrame) -> None:
        ...

class Filters(Protocol):
    region: str | None
    country: str | None
    startYear: int | None
    endYear: int | None
    operation: str | None