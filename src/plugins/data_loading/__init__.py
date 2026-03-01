"""
Purpose:
Exposes load_data() as the single entry point for loading any supported file
into a DataFrame.

See Also
--------
loading_manager.load_data    : Primary entry point for loading a file into a DataFrame.
loader_registry.register_plugin : Decorator for registering a new loader plugin.
loader_interface.DataLoader  : Abstract base class all loader plugins must implement.

"""

from .loader_interface import DataLoader
from .loading_manager import load_data
from .loader_registry import register_plugin
