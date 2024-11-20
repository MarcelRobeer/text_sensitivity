### --------------------------------
### PART 1: GENERATING DATA
### --------------------------------

# %% 
### [PART 1A: GENERATING RANDOM STRINGS FOR ROBUSTNESS TESTING]
from text_sensitivity import RandomString

# First, generate as an InstanceProvider (can easily be used to assign corresponding attribute labels or for 
# predictions with a text model)
RandomString().generate(n=10, min_length=5, max_length=50)

# %% Or simply as a list (easy to use to impute values)
RandomString().generate_list(n=10, min_length=5, max_length=50)

# %% Generate random data, only digits
from text_sensitivity import RandomDigits

RandomDigits(seed=1).generate_list(n=5)

# %% Generate random data, combining emojis, whitespace characters and ASCII characters
from text_sensitivity import (RandomAscii, RandomEmojis, RandomWhitespace,
                              combine_generators)

# Create the random generator (combing three others)
random_generator = combine_generators(RandomAscii(), RandomEmojis(), RandomWhitespace())

# Generate the data through the __call__() function
random_generator.generate_list(n=15)

# %% Generate 20 instances with random ASCII characters, whitespace and Russian (Cyrillic) characters
from text_sensitivity import RandomCyrillic

ascii_cyrillic_generator = combine_generators(RandomAscii(), RandomWhitespace(), RandomCyrillic(languages='ru'))
ascii_cyrillic_generator.generate_list(n=20)

# %% 
### [PART 1B: GENERATING RANDOM ENTITIES (ROBUSTNESS & FAIRNESS TESTING)]
# Generates data for the current locale, e.g. if it is 'nl' it generates country names in Dutch and cities in the Netherlands
from text_sensitivity import RandomCity

RandomCity().generate_list(n=10)

# %% If you specify the locale, it can generate the entity (e.g. country) for multiple languages
from text_sensitivity import RandomCountry

RandomCountry(languages=['nl', 'de', 'fr', 'jp']).generate_list(n=15)

# %% Unlike random strings, random entities can also output the corresponding attribute labels for the generated data
from text_sensitivity import RandomName

# For example, generated Dutch and Russian male and female names, and output which language and sex they are
generator = RandomName(languages=['nl', 'ru'], sex=['male', 'female'], seed=5)
generator.generate_list(n=10, attributes=True)

# %% The same data can also be captured in an instancelib.InstanceProvider and instancelib.LabelProviders
generator.generate(n=10, attributes=True)

# %% Dates 
from text_sensitivity import (RandomDay, RandomDayOfWeek, RandomMonth,
                              RandomYear)

print(RandomYear().generate_list(n=3))
print(RandomMonth(languages=['nl', 'en']).upper().generate_list(n=6))  # use .upper() to generate all uppercase or .lower() for all lower
print(RandomDay().generate_list(n=3))
print(RandomDayOfWeek().sentence().generate_list(n=3))  # use .sentence() for all sentencecase or .title() for titlecase

# %% Other examples of random entities are random street addresses, emails, phone numbers, price tags and crypto names
from text_sensitivity import (RandomAddress, RandomCryptoCurrency, RandomEmail,
                              RandomPhoneNumber, RandomPriceTag)

print(RandomAddress(sep=', ').generate_list(n=5))
print(RandomEmail(languages=['es', 'pt']).generate_list(n=10, attributes=True))
print(RandomPhoneNumber().generate_list(n=5))
print(RandomPriceTag(languages=['ru', 'de', 'it', 'br']).generate_list(n=10))
print(RandomCryptoCurrency().generate_list(n=3))

# %% 
### [PART 1C: WORKING WITH RANDOMNESS]
# Random strings and random entities are seeded for reproducibility.
# Notice how each of these produces a different result

generator = RandomCountry(seed=0)
print(generator.generate_list(n=3))
print(generator.generate_list(n=3))
print(generator.generate_list(n=3))

# %% However, if we want to generate the same list over and over, we need to use the reset_seed() function
print(generator.reset_seed().generate_list(n=3))

# %% Generators can be manually set to any integer seed
generator.seed = 1234  # sets value but does not return self
generator.set_seed(1234)  # sets value and returns self


# %%
### ----------------------------------------
### PART 2: Generating data from patterns
### ----------------------------------------
# Use curly braces to fill-in word-level tokens in a sentence
from text_sensitivity import from_pattern

# %% Generate a list ['This is his house', 'This was his house', 'This is his car', 'This was his car', ...]:
from_pattern('This {is|was} his {house|car|boat}')

# %% Generate a list ['His home town is Eindhoven.', 'Her home town is Eindhoven.',  'His home town is Meerssen.', ...]. By default uses `RandomCity()` to generate the city name.
from_pattern('{His|Her} home town is {city}.')

# %% All default patterns are included in `default_patterns()`
from text_sensitivity import default_patterns

default_patterns()

# %% Override the 'city' default with your own list ['Amsterdam', 'Rotterdam', 'Utrecht']:
from_pattern('{His|Her} home town is {city}.', city=['Amsterdam', 'Rotterdam', 'Utrecht'])

# %% Apply lower case to the first argument and uppercase to the last, getting ['Vandaag, donderdag heeft Sanne COLIN gebeld op +31612351983!', ..., 'Vandaag, maandag heeft Nora SEPP gebeld op +31612351983!', ...]
from_pattern('Vandaag, {lower:day_of_week}, heeft {first_name} {upper:first_name} gebeld op {phone_number}!', n=5)

# %%
### --------------------------------
### PART 3: PERTURBING EXISTING DATA
### --------------------------------
sample = 'This is his example string, made especially for HER!'

# %% Convert the string to all upper
from text_sensitivity.perturbation.sentences import to_upper

list(to_upper()(sample))

# %% Repeat the string 'test' n times
from text_sensitivity.perturbation.sentences import repeat_k_times

print(list(repeat_k_times(k=3)('test')))
print(list(repeat_k_times(k=7, connector='\n')('test')))

# %% Randomly swap the character case (lower to upper or vice versa)
from text_sensitivity.perturbation.characters import random_case_swap

list(random_case_swap()(sample))

# %% Add random spaces to words within a sentence, or swap characters randomly within a word (excluding stopwords and uppercase words)
from text_sensitivity.perturbation.characters import random_spaces, swap_random

print(list(random_spaces(n=5)(sample)))
print(list(swap_random(n=10, stopwords=['the' , 'is', 'of'], include_upper_case=False)(sample)))


# %% Add typos (based on QWERTY keyboard)
from text_sensitivity.perturbation.characters import add_typos

list(add_typos(n=10, stopwords=['the' , 'is', 'of'], include_numeric=False, include_special_char=False)(sample))


# %%
### ----------------------------------------
### PART 4: Working with datasets and models
### ----------------------------------------
# Create a simple dataset (classify whether strings contain punctuation or not)
from text_explainability.data import from_list

instances = ['This is his example instance, not HERS!',
             'An example sentence for you?!',
             'She has her own sentence.',
             'Provide him with something without any punctuation',
             'RANDOM UPPERCASESTRING3']
labels = ['punctuation', 'punctuation', 'punctuation', 'no_punctuation', 'no_punctuation']

env = from_list(instances, labels)

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
# Create sklearn model with pipeline
from sklearn.pipeline import Pipeline

pipeline = Pipeline([('vect', CountVectorizer()),
                     ('rf', MultinomialNB())])

# Wrap sklearn model
from text_explainability.model import import_model

model = import_model(pipeline, env, train=None)

# %% Test the input space for robustness to different characters
from text_sensitivity import input_space_robustness
from text_sensitivity.data.random.string import (RandomAscii, RandomCyrillic,
                                                 RandomEmojis,
                                                 RandomWhitespace)

input_space_robustness(model, 
                       [RandomWhitespace(), RandomAscii(), RandomEmojis(components=False), RandomCyrillic('ru')],
                       n_samples=250,
                       min_length=0,
                       max_length=500)

# %% Compare accuracy when using normal strings and when they are all lowercased
from text_sensitivity import compare_accuracy
from text_sensitivity.perturbation.sentences import to_lower

compare_accuracy(env, model, to_lower)

# %% Check whether precision scores are the same if we add an unrelated string after each sentence
from text_sensitivity import compare_precision
from text_sensitivity.perturbation.base import OneToOnePerturbation

perturbation_fn = OneToOnePerturbation.from_string(suffix='This should not affect scores')
compare_precision(env, model, perturbation_fn)


# %%
perturbation_fn = OneToOnePerturbation.from_string(prefix='This SHOULD affect scores ! ! !')
compare_accuracy(env, model, perturbation_fn)


# %%
perturbation_fn = OneToOnePerturbation.from_dictionary({'him': 'her'}, label_from='not_female', label_to='female')
compare_accuracy(env, model, perturbation_fn)

# %%
from text_sensitivity import invariance

invariance('{His|Her} home town is {city}.', n=10, model=model, expectation='punctuation')
