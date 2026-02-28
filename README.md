```
gdp-analysis-engine
├─ .dev
│  ├─ dep_graphs
│  │  ├─ data_loading.png
│  │  ├─ manual-scheme.png
│  │  ├─ plugins.png
│  │  ├─ project_deps.png
│  │  └─ simplified-dep.png
│  ├─ dev_notes.txt
│  ├─ flamegraphs
│  │  ├─ consise-flamegraph.svg
│  │  ├─ flamegraph.folded
│  │  ├─ flamegraph.pl
│  │  └─ flamegraph.svg
│  ├─ profile
│  │  ├─ profile.prof
│  │  └─ profile_filtered.prof
│  └─ reports
│     ├─ radon_report.txt
│     └─ vulture_report.txt
├─ commands.txt
├─ data
│  ├─ gdp_with_continent_filled.json
│  └─ gdp_with_continent_filled.xlsx
├─ docs
│  ├─ make.bat
│  ├─ Makefile
│  └─ source
│     ├─ conf.py
│     ├─ core.data_loading.rst
│     ├─ core.rst
│     ├─ index.rst
│     ├─ modules.rst
│     ├─ plugins.data_loaders.rst
│     ├─ plugins.rst
│     ├─ _static
│     │  ├─ favicon.ico
│     │  └─ logo.png
│     └─ _templates
├─ LICENCE
├─ logs
├─ profile_main.py
├─ requirements.txt
└─ src
   ├─ base_config.json
   ├─ core
   │  ├─ contracts.py
   │  ├─ engine.py
   │  ├─ metadata.py
   │  └─ __init__.py
   ├─ main.py
   ├─ plugins
   │  ├─ cli
   │  ├─ config_handler
   │  │  ├─ config_load.py
   │  │  ├─ config_models.py
   │  │  ├─ handle.py
   │  │  ├─ paths.py
   │  │  └─ __init__.py
   │  ├─ data_loaders
   │  │  ├─ csv_loader.py
   │  │  ├─ excel_loader.py
   │  │  ├─ json_loader.py
   │  │  └─ __init__.py
   │  ├─ data_loading
   │  │  ├─ loader_interface.py
   │  │  ├─ loader_registry.py
   │  │  ├─ loading_manager.py
   │  │  └─ __init__.py
   │  ├─ outputs.py
   │  ├─ ui
   │  │  ├─ app.py
   │  │  ├─ charts.py
   │  │  ├─ exports.py
   │  │  ├─ layout.css
   │  │  ├─ palette.py
   │  │  ├─ style.py
   │  │  └─ views.py
   │  └─ __init__.py
   ├─ query_config.json
   ├─ util
   │  ├─ cli_parser.py
   │  ├─ logging_contract.py
   │  └─ logging_setup.py
   └─ __init__.py

```

```
gdp-analysis-engine
├─ .dev
│  ├─ dep_graphs
│  │  ├─ data_loading.png
│  │  ├─ manual-scheme.png
│  │  ├─ plugins.png
│  │  ├─ project_deps.png
│  │  └─ simplified-dep.png
│  ├─ dev_notes.txt
│  ├─ flamegraphs
│  │  ├─ consise-flamegraph.svg
│  │  ├─ flamegraph.folded
│  │  ├─ flamegraph.pl
│  │  └─ flamegraph.svg
│  ├─ profile
│  │  ├─ profile.prof
│  │  └─ profile_filtered.prof
│  └─ reports
│     ├─ radon_report.txt
│     └─ vulture_report.txt
├─ commands.txt
├─ data
│  ├─ gdp_with_continent_filled.json
│  └─ gdp_with_continent_filled.xlsx
├─ docs
│  ├─ make.bat
│  ├─ Makefile
│  └─ source
│     ├─ conf.py
│     ├─ core.data_loading.rst
│     ├─ core.rst
│     ├─ index.rst
│     ├─ modules.rst
│     ├─ plugins.data_loaders.rst
│     ├─ plugins.rst
│     ├─ _static
│     │  ├─ favicon.ico
│     │  └─ logo.png
│     └─ _templates
├─ LICENCE
├─ logs
├─ profile_main.py
├─ README.md
├─ requirements.txt
├─ src
│  ├─ base_config.json
│  ├─ core
│  │  ├─ contracts.py
│  │  ├─ core_api.py
│  │  ├─ data_cleaning.py
│  │  ├─ engine.py
│  │  ├─ metadata.py
│  │  └─ __init__.py
│  ├─ main.py
│  ├─ plugins
│  │  ├─ cli
│  │  │  └─ app.py
│  │  ├─ config_handler
│  │  │  ├─ config_load.py
│  │  │  ├─ config_models.py
│  │  │  ├─ handle.py
│  │  │  ├─ paths.py
│  │  │  └─ __init__.py
│  │  ├─ data_loaders
│  │  │  ├─ csv_loader.py
│  │  │  ├─ excel_loader.py
│  │  │  ├─ json_loader.py
│  │  │  └─ __init__.py
│  │  ├─ data_loading
│  │  │  ├─ loader_interface.py
│  │  │  ├─ loader_registry.py
│  │  │  ├─ loading_manager.py
│  │  │  └─ __init__.py
│  │  ├─ outputs.py
│  │  ├─ ui
│  │  │  ├─ analytics_charts.py
│  │  │  ├─ analytics_views.py
│  │  │  ├─ app.py
│  │  │  ├─ charts.py
│  │  │  ├─ exports.py
│  │  │  ├─ layout.css
│  │  │  ├─ output_api.py
│  │  │  ├─ palette.py
│  │  │  ├─ streamlit_entry.py
│  │  │  ├─ style.py
│  │  │  └─ views.py
│  │  └─ __init__.py
│  ├─ query_config.json
│  ├─ util
│  │  ├─ cli_parser.py
│  │  ├─ logging_contract.py
│  │  └─ logging_setup.py
│  └─ __init__.py
└─ test.py

```
