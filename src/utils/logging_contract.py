"""
Purpose:
Defines the structural interface that logging configuration objects must satisfy.

Description:
Any object carrying log_dir and max_log_size satisfies this contract —
no inheritance needed. This makes it easy to reuse existing config objects
as logging config without depending on them.

Classes
-------
LogPolicy
    Protocol for any object that carries logging configuration.

Notes
-----
- No inheritance required — any object with log_dir and max_log_size satisfies this contract.
- This interface is a type-checking aid; Python does not enforce it at runtime.

Examples
--------
>>> from dataclasses import dataclass
>>>
>>> @dataclass
... class AppConfig:
...     log_dir: Path = Path("logs")
...     max_log_size: int = 1000000
...
>>> config: LogPolicy = AppConfig()
"""

from pathlib import Path
from typing import Protocol


class LogPolicy(Protocol):
    """
    Protocol for any object that carries logging configuration.

    Any object with log_dir and max_log_size attributes satisfies this
    contract and can be passed wherever a LogPolicy is expected, regardless
    of what it inherits from.

    Attributes
    ----------
    log_dir : Path
        Directory where log files are written.
    max_log_size : int
        Maximum size of a single log file in bytes before rotation.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>>
    >>> @dataclass
    ... class AppConfig:
    ...     log_dir: Path = Path("logs")
    ...     max_log_size: int = 1000000
    ...
    >>> config: LogPolicy = AppConfig()  # satisfies the contract
    """
    log_dir: Path
    max_log_size: int