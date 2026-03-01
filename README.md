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
│     └─ _static
│        ├─ favicon.ico
│        └─ logo.png
├─ json_validation.py
├─ LICENCE
├─ logs
├─ profile_main.py
├─ README.md
├─ requirements.txt
├─ src
│  ├─ base_config.json
│  ├─ core
│  │  ├─ contracts.py
│  │  ├─ data_cleaning.py
│  │  ├─ engine.py
│  │  ├─ metadata.py
│  │  ├─ test_data_cleaning.py
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
│  │  │  ├─ api_server.py
│  │  │  ├─ app.py
│  │  │  ├─ charts.py
│  │  │  ├─ exports.py
│  │  │  ├─ layout.css
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
├─ .dockerignore
├─ commands.txt
├─ coverage.lcov
├─ data
│  ├─ gdp_with_continent_filled.json
│  └─ gdp_with_continent_filled.xlsx
├─ docker-compose.yml
├─ Dockerfile
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
├─ gdp_report.html
├─ json_validation.py
├─ LICENCE
├─ logs
├─ profile_main.py
├─ pytest.ini
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
│  │  ├─ tests
│  │  │  ├─ test_data_cleaning.py
│  │  │  ├─ test_engine.py
│  │  │  ├─ test_metadata.py
│  │  │  └─ __init__.py
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
│  │  ├─ fileWriter
│  │  │  ├─ app.py
│  │  │  └─ format_picker.py
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
├─ start.py
├─ test.py
└─ vulture_report.txt

```
