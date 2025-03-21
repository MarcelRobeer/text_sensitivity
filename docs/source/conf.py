# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "text_sensitivity"
copyright = "2021, Marcel Robeer"
author = "Marcel Robeer"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_logo = "_static/ts-logo.png"
html_theme_options = {
    "display_version": True,
    "style_external_links": True,
    "logo_only": True,
}
html_context = {
    "display_gitlab": True,
    "github_user": "MarcelRobeer",
    "github_repo": "text_sensitivity",
    "github_version": "main/docs/source/",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Autodoc -----------------------------------------------------------------
autodoc_inherit_docstrings = False
autodoc_typehints = "both"
autoclass_content = "both"

# -- External documentation --------------------------------------------------

intersphinx_mapping = {
    "genbase": ("https://github.com/MarcelRobeer/genbase/", None),
    "instancelib": ("https://instancelib.readthedocs.io/en/latest/", None),
    "text_explainability": ("https://text-explainability.readthedocs.io/en/latest/", None),
    "sklearn": ('http://scikit-learn.org/stable', (None, './_intersphinx/sklearn-objects.inv')),
}


def setup(app):
    app.add_css_file("custom.css")
