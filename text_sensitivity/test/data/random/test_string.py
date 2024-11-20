import pytest
from instancelib.instances.text import TextInstanceProvider

from text_sensitivity.data.random.string import (RandomAscii, RandomCyrillic, RandomDigits, RandomEmojis, RandomLower,
                                                 RandomPunctuation, RandomSpaces, RandomString, RandomUpper,
                                                 RandomWhitespace, combine_generators)

TEST_VALUES = [1, 2, 3, 4, 6, 7, 9, 10, 15, 25, 30, 60, 90, 99, 100]
TEST_GENERATORS = [RandomAscii, RandomString, RandomDigits, RandomSpaces, RandomLower, RandomUpper]
TEST_GENERATORS_SMALL = [RandomCyrillic, RandomEmojis, RandomPunctuation, RandomWhitespace]


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('n', TEST_VALUES)
def test_string_generate_n(generator, n):
    assert len(generator().generate_list(n=n)) == n


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('min_length', TEST_VALUES)
def test_string_generate_length_min(generator, min_length):
    assert all(len(string) >= min_length for string in generator().generate_list(n=25, min_length=min_length, max_length=150))


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('max_length', TEST_VALUES)
def test_string_generate_length_max(generator, max_length):
    assert all(len(string) <= max_length for string in generator().generate_list(n=25, min_length=0, max_length=max_length))


@pytest.mark.parametrize('generator', TEST_GENERATORS)
def test_string_instanceprovider(generator):
    assert isinstance(generator().generate(n=10), TextInstanceProvider)


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('length', TEST_VALUES)
def test_string_generate_wrong_min_max(generator, length):
    with pytest.raises(ValueError):
        generator(seed=0).generate_list(n=10, min_length=length+length, max_length=length)


def test_string_emojis_all_false():
    with pytest.raises(ValueError):
        RandomEmojis(seed=0, base=False, dingbats=False, flags=False, components=False)


def test_string_cyrillic_all_false():
    with pytest.raises(ValueError):
        RandomCyrillic(seed=0, lower=False, upper=False)


def test_string_cyrillic_language_code():
    with pytest.raises(ValueError):
        RandomCyrillic(seed=0, languages=['ru', 'XXX'])


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('seed', TEST_VALUES)
def test_string_seed(generator, seed):
    assert generator(seed=seed).generate_list(n=10) == generator(seed=seed).generate_list(n=10)


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('seed', TEST_VALUES)
def test_string_set_seed(generator, seed):
    generator = generator(seed=seed)
    assert generator.generate_list(n=10) == generator.set_seed(seed=seed).generate_list(n=10)


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('seed', TEST_VALUES)
def test_string_reset_seed(generator, seed):
    generator = generator(seed=seed)
    assert generator.generate_list(n=10) == generator.reset_seed().generate_list(n=10)


@pytest.mark.parametrize('generator', TEST_GENERATORS)
def test_string_reset_call(generator):
    generator = generator(seed=0)
    assert list(generator.generate(n=10).all_data()) == list(generator.reset_seed()(n=10).all_data())


@pytest.mark.parametrize('generator1', TEST_GENERATORS)
@pytest.mark.parametrize('generator2', TEST_GENERATORS_SMALL)
def test_string_combine_generators(generator1, generator2):
    assert isinstance(combine_generators(generator1(), generator2()), RandomString)


@pytest.mark.parametrize('generator1', TEST_GENERATORS)
@pytest.mark.parametrize('generator2', TEST_GENERATORS_SMALL)
@pytest.mark.parametrize('seed', [1, 2, 3])
def test_string_combine_generators_seed(generator1, generator2, seed):
    assert combine_generators(generator1(seed=99999), generator2(seed=333333), seed=seed)._original_seed == seed
