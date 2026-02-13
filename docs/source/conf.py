import os
import sys
sys.path.insert(0, os.path.abspath('../..'))  # points to project root

project = 'GDP Analysis Engine'
author = 'Abdul Rehman Butt, Muhammad Mutahhar Siddique'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',     # Generate docs from docstrings
    'sphinx.ext.napoleon',    # NumPy / Google style support
    'sphinx.ext.viewcode',    # Add links to source code
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = "sphinx_book_theme"
html_static_path = ['_static']

html_favicon = '_static/favicon.ico'
html_logo = '_static/logo.png'

html_theme_options = {
    "repository_url": "https://github.com/ImmutableAF/gdp-analysis-engine",
    "use_repository_button": True,
}

# Napoleon settings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_ivar = True