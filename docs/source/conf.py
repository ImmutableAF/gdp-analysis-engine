import os
import sys

# Points to src/ so automodule resolves packages directly (core, plugins, utils)
sys.path.insert(0, os.path.abspath("../../src"))

project = "GDP Analysis Engine"
author = "Abdul Rehman Butt, Muhammad Mutahhar Siddique"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
]

autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "private-members": False,
    "special-members": "__init__",
}

autodoc_member_order = "bysource"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
html_logo = "_static/logo.png"

html_theme_options = {
    "repository_url": "https://github.com/ImmutableAF/gdp-analysis-engine",
    "use_repository_button": True,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "show_toc_level": 2,
    "navigation_with_keys": True,
}

html_title = "GDP Analysis Engine"

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_ivar = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

autodoc_mock_imports = ["src"]
suppress_warnings = ["autodoc.duplicate_object"]
