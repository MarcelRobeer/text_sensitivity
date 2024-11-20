"""Apply perturbation to one or multiple (tokenized) strings."""

from text_sensitivity.perturbation.base import OneToManyPerturbation, OneToOnePerturbation, Perturbation
from text_sensitivity.perturbation.characters import (add_typos, delete_random, random_case_swap, random_lower,
                                                      random_spaces, random_upper, swap_random)
# from text_sensitivity.perturbation.words import 
from text_sensitivity.perturbation.sentences import repeat_k_times, to_lower, to_upper
