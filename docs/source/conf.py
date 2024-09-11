# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Ultimo'
copyright = '2024, Unital Software'
author = 'Unital Software'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    'micropython': ('https://docs.micropython.org/en/latest', None)
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']


# -- Options for autodoc -----------------------------------------------------
import sys
import os
sys.path.insert(0, os.path.abspath('../../src'))  # add my lib modules

autodoc_mock_imports = [
    'machine',
    'uasyncio',
    'utime',
    'framebuf',
]
autosummary_generate = True
