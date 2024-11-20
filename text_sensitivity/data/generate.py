"""Generate data from a pattern, e.g. `'{He|She} lives in {city}.'`"""

import itertools
from typing import Dict, List, Tuple

from instancelib.instances.text import MemoryTextInstance, TextInstanceProvider
from instancelib.labels.memory import MemoryLabelProvider
from instancelib.typehints import LT
from text_explainability.utils import word_detokenizer, word_tokenizer

from text_sensitivity.data.random.entity import (RandomAddress, RandomCity, RandomCountry, RandomCryptoCurrency,
                                                 RandomCurrencySymbol, RandomDay, RandomDayOfWeek, RandomEmail,
                                                 RandomFirstName, RandomLastName, RandomLicensePlate, RandomMonth,
                                                 RandomName, RandomPhoneNumber, RandomPriceTag, RandomYear)
from text_sensitivity.data.wordlist import WordList

DEFAULTS = {'address': RandomAddress,
            'city': RandomCity,
            'country': RandomCountry,
            'name': RandomName,
            'first_name': RandomFirstName,
            'last_name': RandomLastName,
            'email': RandomEmail,
            'phone_number': RandomPhoneNumber,
            'year': RandomYear,
            'month': RandomMonth,
            'day': RandomDay,
            'day_of_week': RandomDayOfWeek,
            'price_tag': RandomPriceTag,
            'currency_symbol': RandomCurrencySymbol,
            'crypto_currency': RandomCryptoCurrency,
            'license_plate': RandomLicensePlate}


def options_from_brackets(string: str,
                          n: int = 3,
                          seed: int = 0,
                          **kwargs) -> List[str]:
    """Generate options from string.

    Example:
        Generate random list of houses:

        >>> options_from_brackets('I have {number} houses!', number=[5, 10, 100, 5000])

    Args:
        string (str): String with curly braces.
        n (int, optional): Number of elements to generate for each option. Defaults to 3.
        seed (int, optional): Seed for reproducibility. Defaults to 0.

    Returns:
        List[str]: Strings with elements generated.
    """
    def from_pattern(token: str):
        if token.startswith('{') and token.endswith('}'):
            pattern = token[1:-1]
            if ':' not in pattern:
                pattern = ':' + pattern

            modifiers, pattern = pattern.split(':')
            modifiers = [str(x).strip().lower() for x in modifiers.split(',')]

            def modify(p):
                for modifier in modifiers:
                    if modifier == 'upper':
                        p = p.upper()
                    elif modifier == 'lower':
                        p = p.lower()
                    elif modifier == 'sentence':
                        p = p.sentence()
                    elif modifier == 'title':
                        p = p.title()
                    elif modifier == 'original':
                        p = p.original()
                return p

            if '|' in pattern:
                pattern = pattern.split('|')
            elif pattern in kwargs:
                pattern = kwargs[pattern]
            elif pattern in DEFAULTS:
                pattern = DEFAULTS[pattern]
            else:
                raise ValueError(f'Unknown {pattern=}')

            if isinstance(pattern, list):
                return modify(WordList.from_list(pattern, seed=seed)).generate_list(attributes=True)
            return modify(pattern(seed=seed)).generate_list(n=n, attributes=True)
        else:
            return [token]

    return [from_pattern(s) for s in word_tokenizer(string, exclude_curly_brackets=True)]


def from_pattern(pattern: str,
                 n: int = 3,
                 seed: int = 0,
                 **kwargs) -> Tuple[TextInstanceProvider, Dict[LT, MemoryLabelProvider]]:
    """Generate data from a pattern.

    Examples:
        Generate a list ['This is his house', 'This was his house', 'This is his car', 'This was his car', ...]:

        >>> from_pattern('This {is|was} his {house|car|boat}')

        Generate a list ['His home town is Eindhoven.', 'Her home town is Eindhoven.', 
        'His home town is Meerssen.', ...]. By default uses `RandomCity()` to generate the city name.

        >>> from_pattern('{His|Her} home town is {city}.')

        Override the 'city' default with your own list ['Amsterdam', 'Rotterdam', 'Utrecht']:

        >>> from_pattern('{His|Her} home town is {city}.', city=['Amsterdam', 'Rotterdam', 'Utrecht'])

        Apply lower case to the first argument and uppercase to the last, getting 
        ['Vandaag, donderdag heeft Sanne COLIN gebeld!', ..., 'Vandaag, maandag heeft Nora SEPP gebeld!', ...] for
        five random elements of each:

        >>> from_pattern('Vandaag, {lower:day_of_week}, heeft {first_name} {upper:first_name} gebeld!', n=5)

    Args:
        pattern (str): String containing pattern.
        n (int, optional): Number of elements to generate for each element, when generator is random. Defaults to 3.
        seed (int, optional): Seed for reproducibility. Defaults to 0.

    Returns:
        Tuple[TextInstanceProvider, Dict[LT, MemoryLabelProvider]]: Generated instances and corresponding labels.
    """
    def make_unique_attributes(options):
        """Make attributes unique for each label."""
        return [(o[0], {f'{k}#{i}': v for k, v in o[1].items()}) if isinstance(o, tuple) else o
                for i, o in enumerate(options)]

    def generate_elements(options):
        """Convert options into elements and attributes."""
        def get_ids(options):
            def element_to_id(e):
                return list(range(len(e)))

            return [element_to_id(e) if isinstance(e, list) else element_to_id(e[0]) for e in options]

        def get_attributes(options):
            return dict(itertools.chain.from_iterable([option[1].items()
                                                       for option in options if isinstance(option, tuple)]))

        ids = list(map(list, itertools.product(*get_ids(options))))
        attributes = get_attributes(options)

        res = []
        res_a = {k: [] for k in attributes.keys()}
        for row in ids:
            res1 = []
            for elem, option in zip(row, options):
                if isinstance(option, tuple):
                    res1.append(option[0][elem])
                    for k in option[1].keys():
                        res_a[k].append(frozenset([option[1][k][elem]]))
                else:
                    res1.append(option[elem])
            res.append(res1)

        return res, res_a

    # Generate instances and attributes
    options = options_from_brackets(pattern, n=n, seed=seed, **kwargs)
    instances, attributes = generate_elements(make_unique_attributes(options))

    # Convert them into InstanceProviders (instances) and LabelProviders (attributes)
    ids = [i for i in range(len(instances))]
    instances = TextInstanceProvider([MemoryTextInstance(id, word_detokenizer(instance), None, tokenized=instance)
                                      for id, instance in zip(ids, instances)])
    labels = {k: MemoryLabelProvider.from_tuples(list(zip(ids, v))) for k, v in attributes.items()}

    return instances, labels


def default_patterns() -> List[str]:
    """Overview of all default patterns."""
    return list(DEFAULTS.keys())
