Data Loading
============

The ``data_loading`` plugin manages loader registration and orchestrates the
loading lifecycle. It is the bridge between the raw file-format loaders and
the core engine.

.. contents:: Modules
   :local:
   :depth: 1

Loader Interface
----------------

Defines the abstract contract that every concrete loader must satisfy.

.. automodule:: plugins.data_loading.loader_interface
   :members:
   :undoc-members:
   :show-inheritance:

Loader Registry
---------------

.. automodule:: plugins.data_loading.loader_registry
   :members:
   :undoc-members:
   :show-inheritance:

Loading Manager
---------------

.. automodule:: plugins.data_loading.loading_manager
   :members:
   :undoc-members:
   :show-inheritance: