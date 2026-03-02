Configuration Reference
=======================

All configuration is loaded from JSON files under ``src/configs/``.
Schemas are enforced at startup via the Pydantic models in
:mod:`plugins.config_handle.config_models`.

``base_config.json``
--------------------

Controls the core engine: data source path, enabled loaders, and global
runtime flags.

Key fields:

- ``data_path`` — path to the GDP data file (relative to project root)
- ``loader`` — one of ``json``, ``excel``, ``csv``
- ``log_level`` — ``DEBUG``, ``INFO``, ``WARNING``, or ``ERROR``

``query_config.json``
---------------------

Defines the default analytical query executed on startup.

Key fields:

- ``metric`` — the GDP column to analyse
- ``group_by`` — ``continent`` or ``country``
- ``year_range`` — ``[start_year, end_year]``

``analytics_config.json``
-------------------------

Controls which analytics views and chart types are enabled in the dashboard.

``ports_config.json``
---------------------

Specifies the ports used by the Streamlit app and the output REST API.

Key fields:

- ``streamlit_port`` — default ``8501``
- ``api_port`` — default ``8000``