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

from .data_cleaning import clean_gdp_data
from .core_api import create_server
