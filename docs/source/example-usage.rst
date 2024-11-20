
Example Usage
=============

Dependencies
------------

Like ``text_explainability``\ , ``text_sensitivity`` uses instances and machine learning models wrapped with the `InstanceLib <https://pypi.org/project/instancelib/>`_ library.

Dataset and model
-----------------

We manually create a ``TextEnvironment``\ , that holds both our ground-truth labels (\ ``.labels``\ ) and our instances (\ ``.dataset``\ ). Next, we fit a simple ``sklearn`` model that predicts whether the instances (sentence-length strings) contain punctuation or not.

.. code-block:: python

   # Create a simple dataset (classify whether strings contain punctuation or not)
   from instancelib.environment.text import TextEnvironment

   instances = ['This is his example instance, not HERS!',
                'An example sentence for you?!',
                'She has her own sentence.',
                'Provide him with something without any punctuation',
                'RANDOM UPPERCASESTRING3']
   labels = ['punctuation', 'punctuation', 'punctuation', 'no_punctuation', 'no_punctuation']

   env = TextEnvironment.from_data(indices=list(range(len(instances))),
                                   data=instances,
                                   target_labels=list(set(labels)),
                                   ground_truth=[[label] for label in labels],
                                   vectors=[])

   # Create sklearn model with pipeline
   from sklearn.pipeline import Pipeline
   from sklearn.feature_extraction.text import CountVectorizer
   from sklearn.naive_bayes import MultinomialNB

   p = Pipeline([('vect', CountVectorizer()),
                 ('rf', MultinomialNB())])

   # Wrap sklearn model
   from text_explainability import import_model
   import_model(p, env)

Using Text Sensitivity
----------------------

Text Sensitivity is used for *robustness testing* (verifying if a model can handle all types of string data and whether its predictions are invariant to minor changes) and *fairness testing* (comparing model performance on subgroups).

Robustness
^^^^^^^^^^

A robust text model should be able to handle different types of input strings (e.g. ASCII, emojis) and be invariant to minor changes in inputs (e.g. converting a string to uppercase, adding an unrelated string or users making typos).

Generating random data
~~~~~~~~~~~~~~~~~~~~~~

Random strings can be used for testing if a model is able to handle ass sorts of inputs: 

.. code-block:: python

   from text_sensitivity import (RandomData, RandomDigits, RandomAscii, RandomEmojis,
                                 RandomWhitespace, RandomCyrillic, combine_generators)

   # Generate 10 instances with all printable characters
   RandomData().generate_list(n=10, min_length=5, max_length=50)

   # Generate 5 instances containing only digits
   RandomDigits(seed=1).generate_list(n=5)

   # Generate 15 instances, combining emojis, whitespace characters and ASCII characters
   random_generator = combine_generators(RandomAscii(), RandomEmojis(), RandomWhitespace())
   random_generator.generate_list(n=15)

   # Generate 20 instances with random ASCII characters, whitespace and Russian (Cyrillic) characters
   ascii_cyrillic_generator = combine_generators(RandomAscii(), RandomWhitespace(), RandomCyrillic(languages='ru'))
   ascii_cyrillic_generator.generate_list(n=20)

Invariance testing
~~~~~~~~~~~~~~~~~~

A very simple method for invariance testing, is assessing whether the model performs the same on a metric (e.g. accuracy, precision or recall) before and after applying a perturbation. For example, let us compare whether the model retains the same performance when converting all instances to lowercase:

.. code-block:: python

   from text_sensitivity.test import compare_accuracy
   from text_sensitivity.perturbation.sentences import to_lower

   compare_accuracy(env, model, to_lower)

Similarly, we can check whether precision scores are the same if we add an unrelated string after each sentence:

.. code-block:: python

   from text_sensitivity.test import compare_precision
   from text_sensitivity.perturbation.base import OneToOnePerturbation

   perturbation_fn = OneToOnePerturbation.from_string(suffix='This should not affect scores')
   compare_precision(env, model, perturbation_fn)

Under the hood, ``text_sensitivity.test`` uses ``text_sensitivity.perturbation`` to perturb instances (\ ``instancelib.instances.text.TextInstance`` or ``str``\ ), and generates the new instances and labels for the original instance (e.g. 'not_upper') and the new instance(s) (e.g. 'upper').

.. code-block:: python

   from text_sensitivity.perturbation.sentences import to_upper, repeat_k_times
   from text_sensitivity.perturbation.characters import random_case_swap, random_spaces, swap_random, add_typos

   sample = 'This is his example string, made especially for HER!'

   # Convert the sample string to all upper
   list(to_upper()(sample))

   # Repeat the string 'test' n times
   list(repeat_k_times(n=3)('test'))
   list(repeat_k_times(n=7, connector='\n')('test'))

   # Randomly swap the character case (lower to upper or vice versa) in sample
   list(random_case_swap()(sample))

   # Add random spaces to words within a sentence, or swap characters randomly within a word (excluding stopwords and uppercase words) to sample
   list(random_spaces(n=5)(sample))
   list(swap_random(n=10, stopwords=['the' , 'is', 'of'], include_upper_case=False)(sample))

   # Add typos (based on QWERTY keyboard) to sample
   list(add_typos(n=10, stopwords=['the' , 'is', 'of'], include_numeric=False, include_special_char=False)(sample))

Fairness
^^^^^^^^

*TODO*\ : Write up fairness.

Generating random data
~~~~~~~~~~~~~~~~~~~~~~

Data for entities can be generated in the same manner as random strings:

.. code-block:: python

   from text_sensitivity import (RandomCity, RandomCountry, RandomName)

   # Generates data for the current locale, e.g. if it is 'nl' it generates country names in Dutch and cities in the Netherlands
   RandomCity().generate_list(n=10)

   # If you specify the locale, it can generate the entity (e.g. country) for multiple languages
   RandomCountry(languages=['nl', 'de', 'fr', 'jp']).generate_list(n=15)

Unlike random strings, random entities can also output the corresponding attribute labels for the generated data

.. code-block:: python

   # For example, generated Dutch and Russian male and female names, and output which language and sex they are
   generator = RandomName(languages=['nl', 'ru'], sex=['male', 'female'], seed=5)
   generator.generate_list(n=10, attributes=True)

   # The same data can also be captured in an instancelib.InstanceProvider and instancelib.LabelProviders
   generator.generate(n=10, attributes=True)

Other random entities that can be generated are dates, street addresses, emails, phone numbers, price tags and crypto names:

.. code-block:: python

   # Dates 
   from text_sensitivity import RandomYear, RandomMonth, RandomDay, RandomDayOfWeek

   print(RandomYear().generate_list(n=3))
   print(RandomMonth(languages=['nl', 'en']).upper().generate_list(n=6))  # use .upper() to generate all uppercase or .lower() for all lower
   print(RandomDay().generate_list(n=3))
   print(RandomDayOfWeek().sentence().generate_list(n=3))  # use .sentence() for all sentencecase or .title() for titlecase

   # Street addresses, emails, phone numbers, price tags and crypto names
   from text_sensitivity import RandomAddress, RandomEmail, RandomPhoneNumber, RandomPriceTag, RandomCryptoCurrency

   print(RandomAddress(sep=', ').generate_list(n=5))
   print(RandomEmail(languages=['es', 'pt']).generate_list(n=10, attributes=True))
   print(RandomPhoneNumber().generate_list(n=5))
   print(RandomPriceTag(languages=['ru', 'de', 'it', 'br']).generate_list(n=10))
   print(RandomCryptoCurrency().generate_list(n=3))

Generating data from patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These entities, or your own lists, can be used to generate strings for locally testing model robustness/fairness. Text 
within curly braces (\ ``{}``\ ) is replaced, and attribute are added to each perturbed instance. The text outside of the curly 
braces remains the same. Examples of patterns that can be put between curly braces are:


* ``{a|b|c}`` generates a list with elements ``a``\ , ``b`` and ``c``.
* ``{city}`` uses ``RandomCity()`` (in current locale) to generate ``n`` random cities. For a full list of default patterns see ``from text_sensitivity import default_patterns; default_patterns()``.
* ``{custom_entity_name}`` with keyword argument ``custom_entity_name=['this', 'is', 'cool]`` generates a list with elements ``this``\ , ``is``\ , ``cool``.

.. code-block:: python

   from text_sensitivity import from_pattern

   # Generate a list ['This is his house', 'This was his house', 'This is his car', 'This was his car', ...]:
   from_pattern('This {is|was} his {house|car|boat}')

   # Generate a list ['His home town is Eindhoven.', 'Her home town is Eindhoven.',  'His home town is Meerssen.', ...]. By default uses `RandomCity()` to generate the city name.
   from_pattern('{His|Her} home town is {city}.')

   # Override the 'city' default with your own list ['Amsterdam', 'Rotterdam', 'Utrecht']:
   from_pattern('{His|Her} home town is {city}.', city=['Amsterdam', 'Rotterdam', 'Utrecht'])

In addition, modifiers can be added before a semicolon (\ ``:``\ ) within a curly brace to modify the generated data. Example 
modifiers are:


* ``{lower:address}`` generates addresses (\ ``RandomAddress()`` for current locale) in all-lowercase
* ``{upper:name}`` generates full name (\ ``RandomName()`` for current locale) in all-uppercase
* ``{sentence:day_of_week}`` generates day of week (\ ``RandomDayOfWeek()`` for current locale) in sentencecase.
* ``{title:country}`` generates country names (\ ``RandomCountry()`` in locale language) in titlecase.

.. code-block:: python

   # Apply lower case to the first argument and uppercase to the last, getting ['Vandaag, donderdag heeft Sanne COLIN gebeld op +31612351983!', ..., 'Vandaag, maandag heeft Nora SEPP gebeld op +31612351983!', ...]
   from_pattern('Vandaag, {lower:day_of_week}, heeft {first_name} {upper:first_name} gebeld op {phone_number}!', n=5)

