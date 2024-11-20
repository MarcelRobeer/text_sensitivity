import pytest
from text_explainability.utils import word_tokenizer

from text_sensitivity.perturbation.base import OneToManyPerturbation, OneToOnePerturbation
from text_sensitivity.perturbation.characters import (add_typos, delete_random, random_case_swap, random_lower,
                                                      random_spaces, random_upper, swap_random)

TEST_STRING = 'This is a very long string that we use for testing; including some extrasuperlongmegalong words!'
TEST_GENERATORS = [random_case_swap, random_lower, random_spaces,
                   random_upper, swap_random, delete_random]


def _n_lower(string):
    return sum(1 for c in string if c.islower())


def _n_upper(string):
    return sum(1 for c in string if c.isupper())


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('n', [1, 5, 10, 20])
def test_characters_one_or_multiple(generator, n):
    assert isinstance(generator(n=n), OneToOnePerturbation if n == 1 else OneToManyPerturbation)


@pytest.mark.parametrize('generator', TEST_GENERATORS)
def test_characters_empty_string(generator):
    assert len(list(generator().perturb(''))) == 0


def test_characters_random_spaces():
    tokenized = len(word_tokenizer(TEST_STRING))
    assert all(len(word_tokenizer(perturbed.data)) >= tokenized for perturbed in swap_random(n=30).perturb(TEST_STRING)[0][0])


def test_characters_random_spaces_count():
    spaces = TEST_STRING.count(' ')
    assert all(perturbed.data.count(' ') >= spaces for perturbed in swap_random(n=30).perturb(TEST_STRING)[0][0])


def test_characters_delete_random():
    assert all(len(perturbed.data) <= len(TEST_STRING) for perturbed in delete_random(n=30).perturb(TEST_STRING)[0][0])


def test_characters_swap_random():
    assert all(len(perturbed.data) == len(TEST_STRING) for perturbed in swap_random(n=30).perturb(TEST_STRING)[0][0])


def test_characters_add_typos():
    assert all(len(perturbed.data) >= len(TEST_STRING) for perturbed in add_typos(n=30).perturb(TEST_STRING)[0][0])


def test_characters_random_lower():
    lower = _n_lower(TEST_STRING)
    assert all(_n_lower(perturbed.data) >= lower for perturbed in random_lower(n=30).perturb(TEST_STRING)[0][0])


def test_characters_random_upper():
    lower = _n_upper(TEST_STRING)
    assert all(_n_upper(perturbed.data) >= lower for perturbed in random_upper(n=30).perturb(TEST_STRING)[0][0])
    
