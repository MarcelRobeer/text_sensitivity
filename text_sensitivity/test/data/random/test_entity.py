import pytest
from instancelib.instances.text import TextInstanceProvider
from instancelib.labels.base import LabelProvider

from text_sensitivity.data.random.entity import (RandomAddress, RandomCity, RandomCountry, RandomCryptoCurrency,
                                                 RandomCurrencySymbol, RandomDay, RandomDayOfWeek, RandomEmail,
                                                 RandomFirstName, RandomLastName, RandomMonth, RandomName,
                                                 RandomPhoneNumber, RandomPriceTag, RandomYear)

TEST_VALUES = [1, 2, 3, 4, 6, 7, 9, 10, 15, 25, 30, 60, 90, 99, 100]
TEST_GENERATORS = [RandomCity, RandomDayOfWeek, RandomEmail, RandomName, RandomLastName, RandomYear]
TEST_GENERATORS_TEXT = [RandomAddress, RandomCity, RandomCountry, RandomEmail,
                        RandomFirstName, RandomName, RandomMonth, RandomCryptoCurrency]
TEST_GENERATORS_NUMERIC = [RandomDay, RandomYear]
TEST_GENERATORS_CASE_INVARIANT = TEST_GENERATORS_NUMERIC + [RandomCurrencySymbol, RandomPhoneNumber, RandomPriceTag]


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('n', TEST_VALUES)
def test_entity_generate_n(generator, n):
    assert len(generator().generate_list(n=n)) == n


@pytest.mark.parametrize('generator', TEST_GENERATORS_TEXT + TEST_GENERATORS_CASE_INVARIANT)
def test_entity_instanceprovider(generator):
    assert isinstance(generator().generate(n=10, attributes=False), TextInstanceProvider)


@pytest.mark.parametrize('generator', TEST_GENERATORS_TEXT + TEST_GENERATORS_CASE_INVARIANT)
def test_entity_labelprovider(generator):
    assert all(isinstance(label, LabelProvider) for label in generator().generate(n=10, attributes=True)[-1].values())


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('seed', TEST_VALUES)
def test_entity_seed(generator, seed):
    assert generator(seed=seed).generate_list(n=10) == generator(seed=seed).generate_list(n=10)


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('seed', TEST_VALUES)
def test_entity_seed_assign(generator, seed):
    g = generator()
    g.seed = seed
    assert g.seed == seed


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('seed', TEST_VALUES)
def test_entity_set_seed(generator, seed):
    generator = generator(seed=seed)
    assert generator.generate_list(n=10) == generator.set_seed(seed=seed).generate_list(n=10)


@pytest.mark.parametrize('generator', TEST_GENERATORS)
@pytest.mark.parametrize('seed', TEST_VALUES)
def test_entity_reset_seed(generator, seed):
    generator = generator(seed=seed)
    assert generator.generate_list(n=10) == generator.reset_seed().generate_list(n=10)


@pytest.mark.parametrize('generator', TEST_GENERATORS)
def test_entity_random_seed(generator):
    generator = generator(seed=-1)
    assert generator.seed != generator.set_seed(seed=None).seed


@pytest.mark.parametrize('generator', TEST_GENERATORS_TEXT)
def test_entity_upper(generator):
    assert all(entity.isupper() for entity in generator(seed=0).upper().generate_list(n=10))


@pytest.mark.parametrize('generator', TEST_GENERATORS_TEXT)
def test_entity_lower(generator):
    assert all(entity.islower() for entity in generator(seed=0).lower().generate_list(n=10))


@pytest.mark.parametrize('generator', TEST_GENERATORS_TEXT)
def test_entity_title(generator):
    assert all(entity.istitle() for entity in generator(seed=0).title().generate_list(n=10))


@pytest.mark.parametrize('generator', TEST_GENERATORS_TEXT)
def test_entity_sentence(generator):
    assert all(not str(entity)[0].isalpha() or str(entity)[0].isupper()
               for entity in generator(seed=0).sentence().generate_list(n=10))


@pytest.mark.parametrize('generator', TEST_GENERATORS_TEXT)
@pytest.mark.parametrize('case', ['upper', 'lower', 'title', 'sentence'])
def test_entity_generator_original(generator, case):
    assert all(entity1 == entity2 for entity1, entity2 in zip(generator(seed=0).generate_list(n=10),
                                                              eval(f'generator(seed=0).{case}().original().generate_list(n=10)')))


def test_entity_generator_email():
    assert all('@' in str(entity) for entity in RandomEmail(seed=0).generate_list(n=100))


@pytest.mark.parametrize('generator', TEST_GENERATORS_NUMERIC)
def test_entity_generator_numeric(generator):
    assert all(str(entity).isnumeric() for entity in generator(seed=0).generate_list(n=100))


@pytest.mark.parametrize('generator,expected_attributes', zip(TEST_GENERATORS, [1, 1, 1, 2, 1, 1]))
def test_attributes(generator, expected_attributes):
    _, attributes = generator(seed=0).generate_list(n=10, attributes=True)
    assert len(attributes.keys()) == expected_attributes
