"""Create character-level perturbations (`text_sensitivity.perturbation.base.Perturbation`)."""


from typing import Callable

import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import numpy as np

from text_sensitivity.perturbation.base import OneToManyPerturbation, OneToOnePerturbation, Perturbation


def __construct(cls_or_fn, constructor_one, constructor_many, **kwargs):
    """Generic constructor, returning `constructor_many` if n > 1 else `constructor_one`."""
    n = 1
    label_from = kwargs.pop('label_from') if 'label_from' in kwargs else 'original'
    label_to = kwargs.pop('label_to') if 'label_to' in kwargs else 'perturbed'

    if 'n' in kwargs and isinstance(kwargs['n'], int):
        n = kwargs.pop('n')
    if not isinstance(cls_or_fn, (str, dict, Callable)) or isinstance(cls_or_fn, type):
        cls_or_fn = cls_or_fn(**kwargs)        
    if n > 1:
        return constructor_many(cls_or_fn, n=n, label_from=label_from, label_to=label_to)
    return constructor_one(cls_or_fn, label_from=label_from, label_to=label_to)


def _function(fn, **kwargs) -> Perturbation:
    """Constructor for `Perturbation.from_function`."""
    return __construct(fn, OneToOnePerturbation.from_function, OneToManyPerturbation.from_function, **kwargs)


def _nlpaug(cls, **kwargs) -> Perturbation:
    """Constructor for `Perturbation.from_nlpaug`."""
    return __construct(cls, OneToOnePerturbation.from_nlpaug, OneToManyPerturbation.from_nlpaug, **kwargs)


def __random_character_fn(string: str, function: Callable) -> str:
    """Apply a function to random characters in a string."""
    if len(string) == 0:
        return string
    random_indices = np.random.choice(range(len(string)),
                                      size=np.random.randint(1, len(string)),
                                      replace=False)
    for c in random_indices:
        string = string[:c] + function(string[c]) + string[c + 1:]
    return string


def random_upper(n: int = 1) -> Perturbation:
    """Create a `Perturbation` object that randomly swaps characters to uppercase.

    Args:
        n (int, optional): Number of perturbed instances required. Defaults to 1.

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.
    """
    return _function(lambda x: __random_character_fn(x, str.upper), label_to='random_upper', n=n)


def random_lower(n: int = 1) -> Perturbation:
    """Create a `Perturbation` object that randomly swaps characters to lowercase.

    Args:
        n (int, optional): Number of perturbed instances required. Defaults to 1.

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.
    """
    return _function(lambda x: __random_character_fn(x, str.lower), label_to='random_lower', n=n)


def random_case_swap(n: int = 1) -> Perturbation:
    """Create a `Perturbation` object that randomly swaps characters case (lower to higher or vice versa).

    Args:
        n (int, optional): Number of perturbed instances required. Defaults to 1.

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.
    """
    return _function(lambda x: __random_character_fn(x, str.swapcase), label_to='random_case_swap', n=n)


def random_spaces(n: int = 1, **kwargs) -> Perturbation:
    """Create a `Perturbation` object that adds random spaces within words (splits them up).

    Args:
        n (int, optional): Number of perturbed instances required. Defaults to 1.
        **kwargs:  See `naw.SplitAug`_ for optional constructor arguments.

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.

    .. _naw.SplitAug:
        https://github.com/makcedward/nlpaug/blob/master/nlpaug/augmenter/word/split.py
    """
    return _nlpaug(naw.SplitAug, label_to='with_spaces', n=n, **kwargs)


def add_typos(n: int = 1, **kwargs) -> Perturbation:
    """Create a `Perturbation` object that adds keyboard typos within words.

    Args:
        n (int, optional): Number of perturbed instances required. Defaults to 1.
        **kwargs:  See `naw.KeyboardAug`_ for optional constructor arguments.

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.

    .. _nac.KeyboardAug:
        https://github.com/makcedward/nlpaug/blob/master/nlpaug/augmenter/char/keyboard.py
    """
    return _nlpaug(nac.KeyboardAug, label_from='without_typos', label_to='with_typos', n=n, **kwargs)


def swap_random(n: int = 1, **kwargs) -> Perturbation:
    """Create a `Perturbation` object that randomly swaps characters within words.

    Args:
        n (int, optional): Number of perturbed instances required. Defaults to 1.
        **kwargs:  See `nac.RandomCharAug`_ for optional constructor arguments 
            (uses `action='swap'` by default).

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.

    .. _nac.RandomCharAug:
        https://github.com/makcedward/nlpaug/blob/master/nlpaug/augmenter/char/random.py
    """
    return _nlpaug(nac.RandomCharAug, action='swap', label_to='characters_swapped', n=n, **kwargs)


def delete_random(n: int = 1, **kwargs) -> Perturbation:
    """Create a `Perturbation` object with random character deletions in words.

    Args:
        n (int, optional): Number of perturbed instances required. Defaults to 1.
        **kwargs:  See `nac.RandomCharAug`_ for optional constructor arguments 
            (uses `action='delete'` by default).

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.

    .. _nac.RandomCharAug:
        https://github.com/makcedward/nlpaug/blob/master/nlpaug/augmenter/char/random.py
    """
    return _nlpaug(nac.RandomCharAug, action='delete', label_to='characters_deleted', n=n, **kwargs)
