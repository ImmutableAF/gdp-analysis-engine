"""
Purpose:
A core package that takes raw data, cleans it, and lets callers 
query it by region, country, and year range — returning aggregated
results through a single pipeline call.

See Also
--------
engine.run_pipeline : Executes the full transform → filter → aggregate pipeline.
contracts.Filters   : Filter parameter model passed to run_pipeline.
metadata            : Functions for retrieving available filter options.
"""

from .engine import run_pipeline
from .contracts import Filters
from .metadata import (
    get_valid_attr,
    get_year_range,
    get_all_regions,
    get_all_countries,
)