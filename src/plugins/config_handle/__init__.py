"""
Purpose:
The configuration layer — responsible for loading, validating, and sanitizing
config objects before they reach the rest of the application.

See Also
--------
handle.get_base_config  : Primary entry point for application-level configuration.
handle.get_query_config : Primary entry point for query parameter configuration.
"""

from .handle import get_base_config, get_query_config