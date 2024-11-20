from text_sensitivity._version import __version__, __version_info__
from text_sensitivity.data.generate import default_patterns, from_pattern
from text_sensitivity.data.random.entity import (RandomAddress, RandomCity, RandomCountry, RandomCryptoCurrency,
                                                 RandomCurrencySymbol, RandomDay, RandomDayOfWeek, RandomEmail,
                                                 RandomFirstName, RandomLastName, RandomLicensePlate, RandomMonth,
                                                 RandomName, RandomPhoneNumber, RandomPriceTag, RandomYear)
from text_sensitivity.data.random.string import (RandomAscii, RandomCyrillic, RandomDigits, RandomEmojis, RandomLower,
                                                 RandomPunctuation, RandomSpaces, RandomString, RandomUpper,
                                                 RandomWhitespace, combine_generators)
from text_sensitivity.metrics import FairnessMetrics
from text_sensitivity.perturbation import OneToManyPerturbation, OneToOnePerturbation, Perturbation
from text_sensitivity.sensitivity import (compare_accuracy, compare_metric, compare_precision, compare_recall,
                                          input_space_robustness, invariance, mean_score)
