.. image:: https://raw.githubusercontent.com/MarcelRobeer/text_sensitivity/master/img/ts-logo_large.png
    :alt: Text Sensitivity logo
    :align: center


Sensitivity testing (fairness, robustness & safety) for text machine learning models
------------------------------------------------------------------------------------


.. image:: https://img.shields.io/pypi/v/text_sensitivity
   :target: https://pypi.org/project/text-sensitivity/
   :alt: PyPI


.. image:: https://pepy.tech/badge/text-sensitivity
   :target: https://pepy.tech/project/text-sensitivity
   :alt: Downloads


.. image:: https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue
   :target: https://pypi.org/project/text-sensitivity/
   :alt: Python_version


.. image:: https://github.com/MarcelRobeer/text_sensitivity/actions/workflows/check.yml/badge.svg
   :target: https://github.com/MarcelRobeer/text_sensitivity/actions/workflows/check.yml
   :alt: Build_passing


.. image:: https://img.shields.io/pypi/l/text_sensitivity
   :target: https://www.gnu.org/licenses/lgpl-3.0.en.html
   :alt: License


.. image:: https://img.shields.io/badge/docs-external-blueviolet
   :target: https://marcelrobeer.github.io/text_sensitivity
   :alt: Docs_passing


.. image:: https://img.shields.io/badge/code%20style-flake8-aa0000
   :target: https://github.com/PyCQA/flake8
   :alt: Code style: black


.. image:: https://zenodo.org/badge/891502381.svg
   :target: https://doi.org/10.5281/zenodo.14192940
   :alt: https://doi.org/10.5281/zenodo.14192940


------------

.. note::

   Extension of `text_explainability <https://github.com/MarcelRobeer/text_explainability>`_


Uses the **generic architecture** of ``text_explainability`` to also include tests of **safety** (*how safe it the model in production*, i.e. types of inputs it can handle), **robustness** (*how generalizable the model is in production*, e.g. stability when adding typos, or the effect of adding random unrelated data) and **fairness** (*if equal individuals are treated equally by the model*, e.g. subgroup fairness on sex and nationality).

|copy| Marcel Robeer, 2021

Quick tour
----------

**Safety**: test if your model is able to handle different data types.

.. code-block:: python

   from text_sensitivity import RandomAscii, RandomEmojis, combine_generators

   # Generate 10 strings with random ASCII characters
   RandomAscii().generate_list(n=10)

   # Generate 5 strings with random ASCII characters and emojis
   combine_generators(RandomAscii(), RandomEmojis()).generate_list(n=5)

**Robustness**: if your model performs equally for different entities ...

.. code-block:: python

   from text_sensitivity import RandomAddress, RandomEmail

   # Random address of your current locale (default = 'nl')
   RandomAddress(sep=', ').generate_list(n=5)

   # Random e-mail addresses in Spanish ('es') and Portuguese ('pt'), and include from which country the e-mail is
   RandomEmail(languages=['es', 'pt']).generate_list(n=10, attributes=True)

... and if it is robust under simple perturbations.

.. code-block:: python

   from text_sensitivity import compare_accuracy
   from text_sensitivity.perturbation import to_upper, add_typos

   # Is model accuracy equal when we change all sentences to uppercase?
   compare_accuracy(env, model, to_upper)

   # Is model accuracy equal when we add typos in words?
   compare_accuracy(env, model, add_typos)

**Fairness**: see if performance is equal among subgroups.

.. code-block:: python

   from text_sensitivity import RandomName

   # Generate random Dutch ('nl') and Russian ('ru') names, both 'male' and 'female' (+ return attributes)
   RandomName(languages=['nl', 'ru'], sex=['male', 'female']).generate_list(n=10, attributes=True)


Using text_sensitivity
-------------------------
:doc:`installation`
    Installation guide, directly installing it via `pip`_ or through the `git`_.

:doc:`example-usage`
    An extended usage example.

:doc:`text_sensitivity API reference <api/text_sensitivity>`
    A reference to all classes and functions included in the ``text_sensitivity``.


Development
-----------
`text_sensitivity @ GIT`_
    The `git`_ includes the open-source code and the most recent development version.

:doc:`changelog`
    Changes for each version are recorded in the changelog.

:doc:`contributing`
    Contributors to the open-source project and contribution guidelines.


Citation
--------

.. code-block:: bibtex

   @misc{text_sensitivity,
     title = {Python package text\_sensitivity},
     author = {Marcel Robeer},
     howpublished = {\url{https://github.com/MarcelRobeer/text_sensitivity}},
     doi = {10.5281/zenodo.14192941},
     year = {2021}
   }

Credits
-------


* Edward Ma. `NLP Augmentation <https://github.com/makcedward/nlpaug>`_. 2019.
* Daniele Faraglia and other contributors. `Faker <https://github.com/joke2k/faker>`_. 2012.
* Marco Tulio Ribeiro, Tongshuang Wu, Carlos Guestrin and Sameer Singh. `Beyond Accuracy: Behavioral Testing of NLP models with CheckList <https://paperswithcode.com/paper/beyond-accuracy-behavioral-testing-of-nlp>`_. *Association for Computational Linguistics* (ACL). 2020.


.. |copy|   unicode:: U+000A9 .. COPYRIGHT SIGN
.. _pip: https://pypi.org/project/text_sensitivity/
.. _git: https://github.com/MarcelRobeer/text_sensitivity
.. _`text_sensitivity @ GIT`: https://github.com/MarcelRobeer/text_sensitivity

.. toctree::
   :maxdepth: 1
   :caption: Using text_sensitivity
   :hidden:

   Home <self>
   installation.rst
   example-usage.rst

.. toctree::
   :maxdepth: 4
   :caption: API reference
   :hidden:

   api/text_sensitivity.rst

.. toctree::
   :maxdepth: 1
   :caption: Development
   :hidden:

   changelog.rst
   contributing.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
