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
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ docker-usage.md
├─ Dockerfile.dev
├─ Dockerfile.prod
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
├─ project_deps.png
├─ pytest.ini
├─ README.md
├─ requirements.dev.txt
├─ requirements.prod.txt
├─ src
│  ├─ base_config.json
│  ├─ core
│  │  ├─ contracts.py
│  │  ├─ core_api.py
│  │  ├─ data_cleaning.py
│  │  ├─ engine.py
│  │  ├─ metadata.py
│  │  ├─ tests
│  │  │  ├─ test_core_api.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_config_load.py
│  │  │  │  ├─ test_handle.py
│  │  │  │  ├─ test_paths.py
│  │  │  │  └─ __init__.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_loader_registry.py
│  │  │  │  ├─ test_loading_manager.py
│  │  │  │  └─ __init__.py
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
│  │  ├─ logging_setup.py
│  │  └─ tests
│  │     ├─ test_logging_setup.py
│  │     └─ __init__.py
│  └─ __init__.py
├─ start.py
├─ test.py
└─ vulture_report.txt

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
│  ├─ reports
│  │  ├─ radon.txt
│  │  ├─ tests_coverage
│  │  │  └─ custom.css
│  │  └─ vulture.txt
│  └─ run_coverage.ps1
├─ .dockerignore
├─ commands.txt
├─ coverage.lcov
├─ data
│  ├─ gdp_with_continent_filled.json
│  └─ gdp_with_continent_filled.xlsx
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ docker-usage.md
├─ Dockerfile.dev
├─ Dockerfile.prod
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
├─ project_deps.png
├─ pytest.ini
├─ README.md
├─ requirements.dev.txt
├─ requirements.prod.txt
├─ src
│  ├─ base_config.json
│  ├─ core
│  │  ├─ contracts.py
│  │  ├─ core_api.py
│  │  ├─ data_cleaning.py
│  │  ├─ engine.py
│  │  ├─ metadata.py
│  │  ├─ tests
│  │  │  ├─ test_core_api.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_config_load.py
│  │  │  │  ├─ test_handle.py
│  │  │  │  ├─ test_paths.py
│  │  │  │  └─ __init__.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_loader_registry.py
│  │  │  │  ├─ test_loading_manager.py
│  │  │  │  └─ __init__.py
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
│  │  ├─ logging_setup.py
│  │  └─ tests
│  │     ├─ test_logging_setup.py
│  │     └─ __init__.py
│  └─ __init__.py
├─ src.svg
└─ test.py

```
```
gdp-analysis-engine
├─ .dev
│  ├─ conftest.py
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
│  ├─ reports
│  │  ├─ radon.txt
│  │  ├─ tests_coverage
│  │  │  └─ custom.css
│  │  └─ vulture.txt
│  └─ __init__.py
├─ .dockerignore
├─ commands.txt
├─ coverage.lcov
├─ data
│  ├─ gdp_with_continent_filled.json
│  └─ gdp_with_continent_filled.xlsx
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ docker-usage.md
├─ Dockerfile.dev
├─ Dockerfile.prod
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
├─ project_deps.png
├─ pytest.ini
├─ README.md
├─ requirements.dev.txt
├─ requirements.prod.txt
├─ src
│  ├─ base_config.json
│  ├─ core
│  │  ├─ contracts.py
│  │  ├─ core_api.py
│  │  ├─ data_cleaning.py
│  │  ├─ engine.py
│  │  ├─ metadata.py
│  │  ├─ tests
│  │  │  ├─ test_core_api.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_config_load.py
│  │  │  │  ├─ test_handle.py
│  │  │  │  ├─ test_paths.py
│  │  │  │  └─ __init__.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_loader_registry.py
│  │  │  │  ├─ test_loading_manager.py
│  │  │  │  └─ __init__.py
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
│  │  ├─ logging_setup.py
│  │  └─ tests
│  │     ├─ test_logging_setup.py
│  │     └─ __init__.py
│  └─ __init__.py
├─ src.svg
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
│  │  ├─ project_deps.svg
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
│  ├─ reports
│  │  ├─ pytest_log.txt
│  │  ├─ radon.txt
│  │  ├─ tests_coverage
│  │  │  ├─ class_index.html
│  │  │  ├─ coverage_html_cb_188fc9a4.js
│  │  │  ├─ custom.css
│  │  │  ├─ favicon_32_cb_c827f16f.png
│  │  │  ├─ function_index.html
│  │  │  ├─ index.html
│  │  │  ├─ keybd_closed_cb_900cfef5.png
│  │  │  ├─ status.json
│  │  │  ├─ style_cb_5c747636.css
│  │  │  ├─ z_05751383ff71820a_test_loader_registry_py.html
│  │  │  ├─ z_05751383ff71820a_test_loading_manager_py.html
│  │  │  ├─ z_05751383ff71820a___init___py.html
│  │  │  ├─ z_0fd33a2dc922a16c_cli_parser_py.html
│  │  │  ├─ z_0fd33a2dc922a16c_logging_contract_py.html
│  │  │  ├─ z_0fd33a2dc922a16c_logging_setup_py.html
│  │  │  ├─ z_145eef247bfb46b6_main_py.html
│  │  │  ├─ z_145eef247bfb46b6___init___py.html
│  │  │  ├─ z_1707c312aed7f69f_test_core_api_py.html
│  │  │  ├─ z_1707c312aed7f69f_test_data_cleaning_py.html
│  │  │  ├─ z_1707c312aed7f69f_test_engine_py.html
│  │  │  ├─ z_1707c312aed7f69f_test_metadata_py.html
│  │  │  ├─ z_1707c312aed7f69f___init___py.html
│  │  │  ├─ z_23af761437a4409c_loader_interface_py.html
│  │  │  ├─ z_23af761437a4409c_loader_registry_py.html
│  │  │  ├─ z_23af761437a4409c_loading_manager_py.html
│  │  │  ├─ z_23af761437a4409c___init___py.html
│  │  │  ├─ z_5ccd0c9a3cef0944_config_load_py.html
│  │  │  ├─ z_5ccd0c9a3cef0944_config_models_py.html
│  │  │  ├─ z_5ccd0c9a3cef0944_handle_py.html
│  │  │  ├─ z_5ccd0c9a3cef0944_paths_py.html
│  │  │  ├─ z_5ccd0c9a3cef0944___init___py.html
│  │  │  ├─ z_5f7fdbfa4a349163_csv_loader_py.html
│  │  │  ├─ z_5f7fdbfa4a349163_excel_loader_py.html
│  │  │  ├─ z_5f7fdbfa4a349163_json_loader_py.html
│  │  │  ├─ z_5f7fdbfa4a349163___init___py.html
│  │  │  ├─ z_9d40a38ad7b12fde_test_logging_setup_py.html
│  │  │  ├─ z_9d40a38ad7b12fde___init___py.html
│  │  │  ├─ z_b637d62738366886_outputs_py.html
│  │  │  ├─ z_b637d62738366886___init___py.html
│  │  │  ├─ z_ca66e30c3752ad45_test_config_load_py.html
│  │  │  ├─ z_ca66e30c3752ad45_test_handle_py.html
│  │  │  ├─ z_ca66e30c3752ad45_test_paths_py.html
│  │  │  ├─ z_ca66e30c3752ad45___init___py.html
│  │  │  ├─ z_ce21df766c911d41_contracts_py.html
│  │  │  ├─ z_ce21df766c911d41_core_api_py.html
│  │  │  ├─ z_ce21df766c911d41_data_cleaning_py.html
│  │  │  ├─ z_ce21df766c911d41_engine_py.html
│  │  │  ├─ z_ce21df766c911d41_metadata_py.html
│  │  │  └─ z_ce21df766c911d41___init___py.html
│  │  └─ vulture.txt
│  └─ __init__.py
├─ .dockerignore
├─ commands.txt
├─ conftest.py
├─ coverage.lcov
├─ data
│  ├─ gdp_with_continent_filled.json
│  └─ gdp_with_continent_filled.xlsx
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ docker-usage.md
├─ Dockerfile.dev
├─ Dockerfile.prod
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
├─ requirements.dev.txt
├─ requirements.prod.txt
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
│  │  │  ├─ test_core_api.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_config_load.py
│  │  │  │  ├─ test_handle.py
│  │  │  │  ├─ test_paths.py
│  │  │  │  └─ __init__.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_loader_registry.py
│  │  │  │  ├─ test_loading_manager.py
│  │  │  │  └─ __init__.py
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
│  │  ├─ logging_setup.py
│  │  └─ tests
│  │     ├─ test_logging_setup.py
│  │     └─ __init__.py
│  └─ __init__.py
├─ src.svg
└─ test.py

```
```
gdp-analysis-engine
├─ .dev
│  ├─ dep_graphs
│  │  ├─ data_loading.png
│  │  ├─ manual-scheme.png
│  │  ├─ project_deps.svg
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
│  ├─ reports
│  │  ├─ pytest_log.txt
│  │  ├─ radon.txt
│  │  └─ vulture.txt
│  └─ __init__.py
├─ .dockerignore
├─ commands.txt
├─ conftest.py
├─ coverage.lcov
├─ data
│  ├─ gdp_with_continent_filled.json
│  └─ gdp_with_continent_filled.xlsx
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ docker-usage.md
├─ Dockerfile.dev
├─ Dockerfile.prod
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
├─ profile_main.py
├─ pytest.ini
├─ README.md
├─ requirements.dev.txt
├─ requirements.prod.txt
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
│  │  │  ├─ test_core_api.py
│  │  │  ├─ test_data_cleaning.py
│  │  │  ├─ test_engine.py
│  │  │  ├─ test_metadata.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ main.py
│  ├─ plugins
│  │  ├─ cli
│  │  │  └─ app.py
│  │  ├─ config_handle
│  │  │  ├─ config_load.py
│  │  │  ├─ config_models.py
│  │  │  ├─ handle.py
│  │  │  ├─ paths.py
│  │  │  ├─ tests
│  │  │  │  ├─ test_config_load.py
│  │  │  │  ├─ test_handle.py
│  │  │  │  ├─ test_paths.py
│  │  │  │  └─ __init__.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_loader_registry.py
│  │  │  │  ├─ test_loading_manager.py
│  │  │  │  └─ __init__.py
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
│  │  │  ├─ views.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ query_config.json
│  ├─ util
│  │  ├─ cli_parser.py
│  │  ├─ logging_contract.py
│  │  ├─ logging_setup.py
│  │  ├─ tests
│  │  │  ├─ test_logging_setup.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  └─ __init__.py
└─ test.py

```
```
gdp-analysis-engine
├─ .dev
│  ├─ commands.txt
│  ├─ dep_graphs
│  │  ├─ code.puml
│  │  ├─ manual-scheme.png
│  │  ├─ project_deps.svg
│  │  └─ simplified-dep.png
│  ├─ dev_notes.txt
│  ├─ flamegraphs
│  │  ├─ consise-flamegraph.svg
│  │  ├─ flamegraph.folded
│  │  ├─ flamegraph.pl
│  │  └─ flamegraph.svg
│  ├─ json_validation.py
│  ├─ profile
│  │  ├─ profile.prof
│  │  └─ profile_filtered.prof
│  ├─ profile_main.py
│  ├─ proj_diagram.html
│  ├─ reports
│  │  ├─ coverage.lcov
│  │  ├─ pytest_log.txt
│  │  ├─ radon.txt
│  │  └─ vulture.txt
│  ├─ usecase_diagrams
│  │  ├─ analytics-api.png
│  │  ├─ analytics-api.puml
│  │  ├─ core-api.png
│  │  ├─ core-api.puml
│  │  ├─ output-sinks.png
│  │  ├─ output-sinks.puml
│  │  ├─ streamlit-ui.png
│  │  ├─ streamlit-ui.puml
│  │  ├─ system-overview.png
│  │  ├─ system-overview.puml
│  │  └─ uscases.png
│  └─ __init__.py
├─ .dockerignore
├─ conftest.py
├─ data
│  ├─ gdp_with_continent_filled.json
│  └─ gdp_with_continent_filled.xlsx
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ docker-usage.md
├─ Dockerfile.dev
├─ Dockerfile.prod
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
├─ features.txt
├─ LICENCE
├─ pytest.ini
├─ README.md
├─ requirements.dev.txt
├─ requirements.prod.txt
├─ requirements.txt
├─ src
│  ├─ analytics_config.json
│  ├─ base_config.json
│  ├─ core
│  │  ├─ contracts.py
│  │  ├─ core_api.py
│  │  ├─ data_cleaning.py
│  │  ├─ engine.py
│  │  ├─ metadata.py
│  │  ├─ tests
│  │  │  ├─ test_core_api.py
│  │  │  ├─ test_data_cleaning.py
│  │  │  ├─ test_engine.py
│  │  │  ├─ test_metadata.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ main.py
│  ├─ plugins
│  │  ├─ cli
│  │  │  └─ app.py
│  │  ├─ config_handle
│  │  │  ├─ config_load.py
│  │  │  ├─ config_models.py
│  │  │  ├─ handle.py
│  │  │  ├─ paths.py
│  │  │  ├─ tests
│  │  │  │  ├─ test_config_load.py
│  │  │  │  ├─ test_handle.py
│  │  │  │  ├─ test_paths.py
│  │  │  │  └─ __init__.py
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
│  │  │  ├─ tests
│  │  │  │  ├─ test_loader_registry.py
│  │  │  │  ├─ test_loading_manager.py
│  │  │  │  └─ __init__.py
│  │  │  └─ __init__.py
│  │  ├─ fileWriter
│  │  │  ├─ app.py
│  │  │  └─ format_picker.py
│  │  ├─ outputs.py
│  │  ├─ output_api.py
│  │  ├─ ui
│  │  │  ├─ analytics_charts.py
│  │  │  ├─ analytics_views.py
│  │  │  ├─ app.py
│  │  │  ├─ charts.py
│  │  │  ├─ contracts.py
│  │  │  ├─ exports.py
│  │  │  ├─ layout.css
│  │  │  ├─ palette.py
│  │  │  ├─ streamlit_entry.py
│  │  │  ├─ style.py
│  │  │  ├─ views.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ query_config.json
│  ├─ util
│  │  ├─ cli_parser.py
│  │  ├─ logging_contract.py
│  │  ├─ logging_setup.py
│  │  ├─ tests
│  │  │  ├─ test_logging_setup.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  └─ __init__.py
└─ test.py

```