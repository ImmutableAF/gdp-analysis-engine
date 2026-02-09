"""
Configuration Management Package
=================================

Provides robust configuration loading, validation, and sanitization for the
GDP Analysis Engine. Supports both system-level configurations and user query
parameters with comprehensive error handling.

Modules
-------
config_models
    Immutable dataclass definitions for configuration objects
config_loader
    Functions to load configurations from JSON files
config_handler
    Validation and sanitization logic for configurations

Classes
-------
BaseConfig
    System configuration (data paths, logging settings)
QueryConfig
    User query parameters (region, years, operations)

Functions
---------
load_base_config
    Load base configuration from JSON file
load_query_config
    Load query configuration from JSON file
load_default_config
    Get default base configuration
validate_base_config
    Validate base configuration integrity
sanatize_query_config
    Sanitize query configuration against valid data

Configuration Hierarchy
-----------------------
The package manages two types of configurations:

**Base Configuration** (System-level, required)
    - Data directory path
    - Default data file name
    - Log directory path
    - Maximum log file size

**Query Configuration** (User-level, optional)
    - Region filter (e.g., "Asia", "Europe")
    - Year range (start and end years)
    - Aggregation operation ("sum", "avg", "average")

Validation Strategy
-------------------
Configurations undergo two-phase validation:

1. **Structural Validation** (config_loader)
   - JSON syntax validation
   - Required key presence
   - Type conversion

2. **Semantic Validation** (config_handler)
   - Path existence checks
   - Value range validation
   - Cross-field consistency

Error Handling
--------------
The package raises specific exceptions:

FileNotFoundError
    Configuration file or referenced paths don't exist
json.JSONDecodeError
    Malformed JSON syntax
ValueError
    Invalid configuration values (negative sizes, empty paths)
KeyError
    Missing required configuration keys

Immutability Guarantee
----------------------
All configuration objects are frozen dataclasses, preventing accidental
modification during runtime. To change a configuration, use dataclasses.replace():

>>> from dataclasses import replace
>>> new_config = replace(old_config, region="Europe")

Examples
--------
Load and validate configurations:

>>> from pathlib import Path
>>> from src.core.config_manager import (
...     load_base_config,
...     load_query_config,
...     validate_base_config,
...     sanatize_query_config
... )
>>>
>>> # Load base configuration
>>> base_config = load_base_config(Path("data/configs/base_config.json"))
>>> validate_base_config(base_config)  # Raises if invalid
>>>
>>> # Load and sanitize query
>>> query = load_query_config(Path("data/configs/query_config.json"))
>>> regions = ["Asia", "Europe", "Africa"]
>>> years = (1960, 2024)
>>> clean_query = sanatize_query_config(query, regions, years)

Use default configuration:

>>> from src.core.config_manager import load_default_config
>>> config = load_default_config()
>>> print(config.data_directory)
data

See Also
--------
config_models.BaseConfig : System configuration data structure
config_models.QueryConfig : Query parameter data structure
config_loader : Configuration loading functions
config_handler : Validation and sanitization logic

Notes
-----
All configuration files must be valid JSON. The package validates configurations
at load time to ensure the system never operates with invalid settings.

Configuration files should be stored in ``data/configs/`` by convention.
"""

from .config_models import BaseConfig, QueryConfig
from .config_loader import load_base_config, load_query_config, load_default_config
from .config_handle import validate_base_config, sanatize_query_config

__all__ = [
    'BaseConfig',
    'QueryConfig',
    'load_base_config',
    'load_query_config',
    'load_default_config',
    'validate_base_config',
    'sanatize_query_config',
]