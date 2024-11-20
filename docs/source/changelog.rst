
Changelog
=========

All notable changes to ``text_sensitivity`` will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_\ ,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

`Unreleased <https://github.com/MarcelRobeer/text_sensitivity>`_
-------------------------------------------------------------------------


`0.3.4 <https://pypi.org/project/text-sensitivity/0.3.4/>`_ - 2024-11-20
----------------------------------------------------------------------------

Changed
^^^^^^^


* Moved to GitHub


Fixed
^^^^^


* Various security fixes


`0.3.3 <https://pypi.org/project/text-sensitivity/0.3.3/>`_ - 2023-01-28
----------------------------------------------------------------------------

Added
^^^^^


* Ensured full documentation

Changed
^^^^^^^


* Moved documentation to ``sphinx``
* Added generation of unique attributes when using ``from_pattern``
* Only show outer ``tqdm`` in ``input_space_robustness``


Fixed
^^^^^


* Bugfix with lazy loading of locales

`0.3.2 <https://pypi.org/project/text-sensitivity/0.3.2/>`_ - 2022-03-21
----------------------------------------------------------------------------

Fixed
^^^^^


* Bugfix when Notebook UI

`0.3.1 <https://pypi.org/project/text-sensitivity/0.3.1/>`_ - 2022-03-16
----------------------------------------------------------------------------

Changed
^^^^^^^


* Custom sorting of metrics in return types
* Requires ``genbase>=0.2.4``
* Requires ``text_explainability>=0.6.1``
* Moved version information

`0.3.0 <https://pypi.org/project/text-sensitivity/0.3.0/>`_ - 2022-03-04
----------------------------------------------------------------------------

Added
^^^^^


* Fairness metrics

Changed
^^^^^^^


* Requires ``genbase>=0.2.2``
* Requires ``text_explainability>=0.6.0``
* Renamed ``pyproject.toml`` to ``.portray`` to avoid build errors
* Do not render ``conf_mat`` for model metrics

Fixed
^^^^^


* Added ``person`` provider to city generation in English

`0.2.6 <https://pypi.org/project/text-sensitivity/0.2.6/>`_ - 2021-12-06
----------------------------------------------------------------------------

Added
^^^^^


* Return type and notebook UI rendering for mean score
* Return type and notebook UI for invariance test

Changed
^^^^^^^


* Requires ``genbase>=0.1.14``
* Requires ``text_explainability>=0.5.8``

`0.2.5 <https://pypi.org/project/text-sensitivity/0.2.5/>`_ - 2021-12-02
----------------------------------------------------------------------------

Added
^^^^^


* Return types for sensitivity tests
* Rendering of sensitivity tests using ``genbase.ui``

Changed
^^^^^^^


* Moved ``SeedMixin`` and ``CaseMixin`` to ``genbase``
* Use ``genbase.internationalization``
* Requires ``genbase>=0.1.13``

`0.2.4 <https://pypi.org/project/text-sensitivity/0.2.4/>`_ - 2021-11-16
----------------------------------------------------------------------------

Fixed
^^^^^


* Bugfix in ``OneToOnePerturbation.from_dictionary``
* Bugfix in ``compare_metric``
* Bugfix in ``one_to_one_dictionary_mapping``

`0.2.3 <https://pypi.org/project/text-sensitivity/0.2.3/>`_ - 2021-11-16
----------------------------------------------------------------------------

Fixed
^^^^^


* Bugfix in ``oneway_dictionary_mapping``

`0.2.2 <https://pypi.org/project/text-sensitivity/0.2.2/>`_ - 2021-11-15
----------------------------------------------------------------------------

Fixed
^^^^^


* Bugfix in ``one_to_one_dictionary_mapping``

`0.2.1 <https://pypi.org/project/text-sensitivity/0.2.1/>`_ - 2021-11-03
----------------------------------------------------------------------------

Added
^^^^^


* Invariance testing
* Comparison of mean scores (labelwise)

`0.2.0 <https://pypi.org/project/text-sensitivity/0.2.0/>`_ - 2021-10-08
----------------------------------------------------------------------------

Added
^^^^^


* Random license plate generation
* Added ``SeedMixin`` to ``WordList``
* Added ``CaseMixin`` to ``WordList``
* Robustness testing for random inputs
* Generate data from patterns
* Example usage for robustness testing and data generation

Changed
^^^^^^^


* Ability to generate items from ``WordList``

`0.1.10 <https://pypi.org/project/text-sensitivity/0.1.10/>`_ - 2021-10-07
------------------------------------------------------------------------------

Added
^^^^^


* Perturbation imports (character, word, sentence) to ``text_sensitivity.perturbation``
* Examples in README.md
* Attribute renaming in ``text_sensitivity.data.random.entity``

Changed
^^^^^^^


* Updated usage with ``text_explainability==0.5.0``
* Updated usage with ``faker==8.16.0``

`0.1.9 <https://pypi.org/project/text-sensitivity/0.1.9/>`_ - 2021-10-02
----------------------------------------------------------------------------

Fixed
^^^^^


* Bugfix in reading .csv files

`0.1.8 <https://pypi.org/project/text-sensitivity/0.1.8/>`_ - 2021-10-02
----------------------------------------------------------------------------

Removed
^^^^^^^


* Removed cities from wordlists

`0.1.7 <https://pypi.org/project/text-sensitivity/0.1.7/>`_ - 2021-10-02
----------------------------------------------------------------------------

Added
^^^^^


* MANIFEST.in
* Security tests with bandit
* Ability to make random entities lowercase, uppercase or sentencecase
* Tests for ``text_sensitivity.data.random.string``
* Tests for ``text_sensitivity.data.random.entity``
* Additional documentation
* Ability to generate addresses/cities in a country with a likelihood based on their population

Removed
^^^^^^^


* Removed countries from wordlists

Fixed
^^^^^


* Bugfixes in ``OneToOnePerturbation`` and ``OneToManyPerturbation``

`0.1.6 <https://pypi.org/project/text-sensitivity/0.1.6/>`_ - 2021-10-02
----------------------------------------------------------------------------

Changed
^^^^^^^


* Moved random string data generation from ``text_sensitivity.data.random`` to ``text_sensitivity.data.random.string``
* Renamed ``RandomData`` to ``RandomString``
* Seed behavior generalized in ``SeedMixin``\ , only requiring a ``self._seed`` and ``self._original_seed`` to work with a class

Added
^^^^^


* Random multilingual entity generation with Python package ``faker``
* Documentation and example usages for random entity generation

`0.1.5 <https://pypi.org/project/text-sensitivity/0.1.5/>`_ - 2021-10-01
----------------------------------------------------------------------------

Added
^^^^^


* Internationalization support
* Name of countries by language word list
* Top 100 most populous cities by country word list

`0.1.4 <https://pypi.org/project/text-sensitivity/0.1.4/>`_ - 2021-09-30
----------------------------------------------------------------------------

Added
^^^^^


* Citation information
* Documentation styling
* Generation of random Cyrillic text

`0.1.3 <https://pypi.org/project/text-sensitivity/0.1.3/>`_ - 2021-09-27
----------------------------------------------------------------------------

Added
^^^^^


* Documentation
* Ability to make ``OneToOnePerturbation`` from unordered list
* Extended one-to-one and one-to-many dictionary mappings

`0.1.2 <https://pypi.org/project/text-sensitivity/0.1.2/>`_ - 2021-09-24
----------------------------------------------------------------------------

Changed
^^^^^^^


* Proper ``n``\ -times application of function with ``OneToManyPerturbation``

Fixed
^^^^^


* Bugfix in character generation

`0.1.1 <https://pypi.org/project/text-sensitivity/0.1.1/>`_ - 2021-09-24
----------------------------------------------------------------------------

Added
^^^^^


* Example usage
* Sensitivity testing wrapper functions (compare accuracy, precision, recall)

`0.1.0 <https://pypi.org/project/text-sensitivity/0.1.0/>`_ - 2021-09-24
----------------------------------------------------------------------------

Added
^^^^^


* Random data generation
* One to one perturbation
* One to many perturbation
* Example perturbation functions
* README.md
* LICENSE
* CI/CD pipeline for flake8 testing
* setup.py

