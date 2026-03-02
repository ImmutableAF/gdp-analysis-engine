Core
====

The core package contains the engine, data-cleaning pipeline, metadata handling,
contracts (shared type definitions), and the public-facing core API. No plugin
or UI code lives here — this layer is intentionally dependency-free.

.. contents:: Modules
   :local:
   :depth: 1

Core API
--------

The ``core_api`` module is the single entry-point through which all external
callers (CLI, Streamlit UI, REST API) interact with the engine.

.. automodule:: core.core_api
   :members:
   :undoc-members:
   :show-inheritance:

Engine
------

.. automodule:: core.engine
   :members:
   :undoc-members:
   :show-inheritance:

Data Cleaning
-------------

.. automodule:: core.data_cleaning
   :members:
   :undoc-members:
   :show-inheritance:

Metadata
--------

.. automodule:: core.metadata
   :members:
   :undoc-members:
   :show-inheritance:

Contracts
---------

Shared dataclasses, protocols, and type aliases used across the whole codebase.

.. automodule:: core.contracts
   :members:
   :undoc-members:
   :show-inheritance: