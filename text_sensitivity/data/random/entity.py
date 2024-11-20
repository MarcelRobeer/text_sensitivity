"""Generation of random entities (e.g. names, telephone numbers) for given languages."""

from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np
from faker.factory import Factory
from faker.generator import Generator
from genbase import LOCALE_MAP, CaseMixin, Readable, SeedMixin, get_locale
from instancelib.instances.text import TextInstanceProvider
from instancelib.labels.memory import MemoryLabelProvider
from lazy_load import force_eval


class RandomEntity(Readable, SeedMixin, CaseMixin):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 providers: List[str] = ['person'],
                 fn_name: Union[str, List[str]] = 'name',
                 attribute: str = 'fn',
                 attribute_rename: Optional[Callable[[str], str]] = None,
                 sep: str = '\n',
                 seed: int = 0):
        r"""Base class to generate entity data for (a) given language(s).

        Example:
            Generate a 10 random English names entity using package `faker`:

            >>> RandomEntity(locale='en', providers=['person'], fn_name='name').generate_list(n=10)

        Args:
            languages (Union[str, List[str]], optional): Languages to generate data from. Defaults to your current 
                locale (see `get_locale()`).
            providers (List[str], optional): Providers from `faker` used in generation. Defaults to ['person'].
            fn_name (Union[str, List[str]], optional): Function name(s) to call for each generator. Defaults to 'name'.
            attribute (str, optional): Name of additional attribute (other than language). Defaults to 'fn'.
            attribute_rename (Optional[Callable[[str], str]], optional): Rename function for attribute value. 
                Defaults to None.
            sep (str, optional): Separator to replace '\n' character with. Defaults to '\n'.
            seed (int, optional): Seed for reproducibility. Defaults to 0.
        """
        languages = force_eval(languages)
        self.languages = [languages] if isinstance(languages, str) else languages
        self.providers = [f'faker.providers.{provider}' if not provider.startswith('faker.providers.') else provider
                          for provider in providers]
        self.generators = {lang: Factory.create(LOCALE_MAP[lang] if lang in LOCALE_MAP.keys() else lang,
                                                self.providers,
                                                Generator(),
                                                None)
                           for lang in self.languages}
        self.attribute = attribute
        if attribute_rename is None:
            self.attribute_rename = lambda x: x
        else:
            self.attribute_rename = attribute_rename
        self.sep = sep
        self.fn_name = fn_name if isinstance(fn_name, list) else [fn_name]
        self._original_seed = self._seed = seed
        self._lowercase = self._sentencecase = self._titlecase = self._uppercase = False

    def generate_list(self,
                      n: int,
                      attributes: bool = False) -> Union[List[str], Tuple[List[str], Dict[str, str]]]:
        """Generate n instances of random data and return as list. 

        Args:
            n (int): Number of instances to generate.
            attributes (bool, optional): Include attributes (language, which function was used, etc.) or not. 
                Defaults to False.

        Returns:
            List[str]: Generated instances (if attributes = False).
            Tuple[List[str], Dict[str, str]]: Generated instances and corresponding attributes (if attributes = True).
        """
        np.random.seed(self._seed)
        self._seed += 1
        languages = np.random.choice(self.languages, size=n)
        fn_names = np.random.choice(self.fn_name, size=n)
        for generator in self.generators.values():
            generator.seed(self._seed)
        sentences = [self.apply_case(eval(f'self.generators["{lang}"].{fn}()').replace('\n', self.sep))  # nosec
                     for fn, lang in zip(fn_names, languages)]
        if not attributes:
            return sentences

        attr = {'language': list(languages)}
        if len(self.fn_name) > 1:
            attr[self.attribute] = [self.attribute_rename(fn) for fn in fn_names]
        return sentences, attr

    def generate(self,
                 n: int,
                 attributes: bool = False
                 ) -> Union[TextInstanceProvider, Tuple[TextInstanceProvider, Dict[str, MemoryLabelProvider]]]:
        """Generate n instances of random data. 

        Args:
            n (int): Number of instances to generate.
            attributes (bool, optional): Include attributes (language, which function was used, etc.) or not. 
                Defaults to False.

        Returns:
            TextInstanceProvider: Provider containing generated instances (if attributes = False).
            Tuple[TextInstanceProvider, Dict[str, MemoryLabelProvider]]: Provider and corresponding attribute 
                labels (if attributes = True).
        """
        res = self.generate_list(n=n, attributes=attributes)
        values = TextInstanceProvider.from_data(res[0] if attributes else res)

        if attributes:
            # Group labels, and put all of them into labelproviders with the same keys as the instanceprovider
            labels = {key: MemoryLabelProvider.from_tuples([(i, frozenset([v])) for i, v in enumerate(values)])
                      for key, values in res[1].items()}
            return values, labels
        return values


class CityByPopulationMixin(Readable):
    @staticmethod
    def cities_by_population(cities: List[str], country_code: str):
        """Add population scores to each city in a country.

        Args:
            cities (List[str]): Current list of cities. If no replacement is found, this will be returned back.
            country_code (str): Two-letter country code (e.g. 'nl').
        """
        country_code = country_code.split('_')[-1] if '_' in country_code else country_code

        import json
        import os
        from collections import OrderedDict

        import pandas as pd
        import requests

        res = []
        file = os.path.abspath(__file__ + f'/../../lists/cities_by_population_{country_code}.csv')

        if os.path.isfile(file):  # already exists, using cached file
            res = pd.read_csv(file, header=None).values.tolist()
        else:  # try and get a new one from the internet
            try:
                response = requests.get('https://public.opendatasoft.com/api/records/1.0/search/' +
                                        '?dataset=geonames-all-cities-with-a-population-1000&q=' +
                                        f'&lang={str.lower(country_code)}&fields=name,population&sort=population' +
                                        f'&refine.country_code={str.upper(country_code)}&rows={len(cities)}')
                if response.status_code != 200:
                    return cities
                res = [(city['fields']['name'], float(city['fields']['population']))
                        for city in json.loads(response.content)['records']]
                pd.DataFrame(res).to_csv(file, index=False, header=None)
            except Exception as e:
                print(e)
                return cities
        return OrderedDict(res) if len(res) > 0 else cities

    def add_likelihood_to_cities(self):
        """Add likelihood to cities, based on population."""
        for lang, generator in self.generators.items():
            if hasattr(generator.provider('faker.providers.address'), 'cities'):
                generator.provider('faker.providers.address').cities = CityByPopulationMixin.cities_by_population(
                    cities=generator.provider('faker.providers.address').cities,
                    country_code=lang)


class RandomAddress(RandomEntity, CityByPopulationMixin):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 likelihood_based_on_city_population: bool = True,
                 sep: str = '\n',
                 seed: int = 0):
        """Generate random cities in (a) given language(s)."""
        super().__init__(languages=languages,
                         providers=['address', 'person'],
                         fn_name='address',
                         sep=sep,
                         seed=seed)

        if likelihood_based_on_city_population:
            self.add_likelihood_to_cities()


class RandomCity(RandomEntity, CityByPopulationMixin):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 likelihood_based_on_city_population: bool = True,
                 seed: int = 0):
        """Generate random cities in (a) given language(s)."""
        super().__init__(languages=languages,
                         providers=['address', 'person'],
                         fn_name='city',
                         seed=seed)

        if likelihood_based_on_city_population:
            self.add_likelihood_to_cities()


class RandomCountry(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 seed: int = 0):
        """Generate random countries for (a) given language(s)."""
        super().__init__(languages=languages,
                         providers=['address'],
                         fn_name='country',
                         seed=seed)


class RandomName(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 sex: List[str] = ['male', 'female'],
                 seed: int = 0):
        """Generate random full names for (a) given language(s)."""
        if isinstance(sex, str):
            sex = [sex]
        super().__init__(languages=languages,
                         providers=['person'],
                         fn_name=[f'name_{s}' for s in sex],
                         attribute='sex',
                         attribute_rename=lambda x: str(x).replace('name_', ''),
                         seed=seed)


class RandomFirstName(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 sex: List[str] = ['male', 'female'],
                 seed: int = 0):
        """Generate random first names for (a) given language(s)."""
        if isinstance(sex, str):
            sex = [sex]
        super().__init__(languages=languages,
                         providers=['person'],
                         fn_name=[f'first_name_{s}' for s in sex],
                         attribute='sex',
                         attribute_rename=lambda x: str(x).replace('name_', ''),
                         seed=seed)


class RandomLastName(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 seed: int = 0):
        """Generate random last names for (a) given language(s)."""
        super().__init__(languages=languages,
                         providers=['person'],
                         fn_name='last_name',
                         seed=seed)


class RandomEmail(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 seed: int = 0):
        """Generate random e-mail addresses for (a) given language(s)."""
        super().__init__(languages=languages,
                         providers=['person', 'company', 'internet'],
                         fn_name='email',
                         seed=seed)


class RandomPhoneNumber(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 seed: int = 0):
        r"""Generate random phone numbers for (a) given language(s) / country."""
        super().__init__(languages=languages,
                         providers=['phone_number'],
                         fn_name='phone_number',
                         seed=seed)


class RandomYear(RandomEntity):
    def __init__(self,
                 seed: int = 0):
        """Generate random year."""
        super().__init__(languages='en',
                         providers=['date_time'],
                         fn_name='year',
                         seed=seed)


class RandomMonth(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 seed: int = 0):
        """Generate random month name in (a) given language(s)."""
        super().__init__(languages=languages,
                         providers=['date_time'],
                         fn_name='month_name',
                         seed=seed)


class RandomDay(RandomEntity):
    def __init__(self,
                 seed: int = 0):
        """Generate random day of the month."""
        super().__init__(languages='en',
                         providers=['date_time'],
                         fn_name='day_of_month',
                         seed=seed)


class RandomDayOfWeek(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 seed: int = 0):
        """Generate random day of week in (a) given language(s)."""
        super().__init__(languages=languages,
                         providers=['date_time'],
                         fn_name='day_of_week',
                         seed=seed)


class RandomPriceTag(RandomEntity):
    def __init__(self,
                 languages: Union[str, List[str]] = get_locale(),
                 seed: int = 0):
        """Generate random pricetag names in (a) given languages' currency."""
        super().__init__(languages=languages,
                         providers=['currency'],
                         fn_name='pricetag',
                         seed=seed)


class RandomCurrencySymbol(RandomEntity):
    def __init__(self,
                 seed: int = 0):
        """Generate random currency symbols."""
        super().__init__(languages='en',
                         providers=['currency'],
                         fn_name='currency_symbol',
                         seed=seed)


class RandomCryptoCurrency(RandomEntity):
    def __init__(self,
                 seed: int = 0):
        """Generate random cryptocurrency names."""
        super().__init__(languages='en',
                         providers=['currency'],
                         fn_name='cryptocurrency_name',
                         seed=seed)


class RandomLicensePlate(RandomEntity):
    def __init__(self,
                 seed: int = 0):
        """Generate random license plates for a given country."""
        super().__init__(languages='en',
                         providers=['automotive'],
                         fn_name='license_plate',
                         seed=seed)
