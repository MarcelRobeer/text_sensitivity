import pytest

from text_sensitivity.perturbation.base import OneToOnePerturbation
from text_sensitivity.perturbation.sentences import repeat_k_times, to_lower, to_upper

TEST_STRING = 'This is a very long string that we use for testing; including some extrasuperlongmegalong words!'
TEST_STRINGS = ['repeat', 'THIS', 'String ']
TEST_GENERATORS = [to_lower, to_upper, repeat_k_times]


@pytest.mark.parametrize('generator', TEST_GENERATORS)
def test_sentences_one_or_multiple(generator):
    assert isinstance(generator(), OneToOnePerturbation)


def test_sentences_to_lower():
    assert list(to_lower().perturb(TEST_STRING))[0][0].data.islower()


def test_sentences_to_upper():
    assert list(to_upper().perturb(TEST_STRING))[0][0].data.isupper()


@pytest.mark.parametrize('string', TEST_STRINGS)
@pytest.mark.parametrize('k', [2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 50])
def test_sentences_repeat_k_times(string, k):
    original_length = len(string)
    assert len(list(repeat_k_times(k=k).perturb(string))[0][0].data) >= original_length * k


@pytest.mark.parametrize('string', TEST_STRINGS)
def test_sentences_repeat_once(string):
    assert len(list(repeat_k_times(k=1).perturb(string))) == 0


@pytest.mark.parametrize('string', TEST_STRINGS)
@pytest.mark.parametrize('connector', ['\n', ' ', '', None])
@pytest.mark.parametrize('k', [2, 4, 15, 23, 25])
def test_sentences_repeat_connector(string, connector, k):
    original_length = len(string)
    assert len(list(repeat_k_times(k=k, connector=connector).perturb(string))[0][0].data) >= original_length * k
