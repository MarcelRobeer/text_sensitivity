*<p align="center">
  <img src="https://raw.githubusercontent.com/MarcelRobeer/text_sensitivity/master/img/ts-logo_large.png" alt="Text Sensitivity logo" width="70%">*
</p>

**<h3 align="center">
Sensitivity testing (fairness, robustness & safety) for text machine learning models**
</h3>

[![PyPI](https://img.shields.io/pypi/v/text_sensitivity)](https://pypi.org/project/text-sensitivity/)
[![Downloads](https://pepy.tech/badge/text-sensitivity)](https://pepy.tech/project/text-sensitivity)
[![Python_version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/text-sensitivity/)
[![Lint, Security & Tests](https://github.com/MarcelRobeer/text_sensitivity/actions/workflows/check.yml/badge.svg)](https://github.com/MarcelRobeer/text_sensitivity/actions/workflows/check.yml)
[![License](https://img.shields.io/pypi/l/text_sensitivity)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![Documentation Status](https://readthedocs.org/projects/text-sensitivity/badge/?version=latest)](https://text-sensitivity.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-flake8-aa0000)](https://github.com/PyCQA/flake8)
[![DOI](https://zenodo.org/badge/891502381.svg)](https://doi.org/10.5281/zenodo.14192940)

---

> Extension of [text_explainability](https://github.com/MarcelRobeer/text_explainability)

Uses the **generic architecture** of `text_explainability` to also include tests of **safety** (_how safe it the model in production_, i.e. types of inputs it can handle), **robustness** (_how generalizable the model is in production_, e.g. stability when adding typos, or the effect of adding random unrelated data) and **fairness** (_if equal individuals are treated equally by the model_, e.g. subgroup fairness on sex and nationality).

&copy; Marcel Robeer, 2021

## Quick tour

**Safety**: test if your model is able to handle different data types.

```python
from text_sensitivity import RandomAscii, RandomEmojis, combine_generators

# Generate 10 strings with random ASCII characters
RandomAscii().generate_list(n=10)

# Generate 5 strings with random ASCII characters and emojis
combine_generators(RandomAscii(), RandomEmojis()).generate_list(n=5)
```

**Robustness**: if your model performs equally for different entities ...
```python
from text_sensitivity import RandomAddress, RandomEmail

# Random address of your current locale (default = 'nl')
RandomAddress(sep=', ').generate_list(n=5)

# Random e-mail addresses in Spanish ('es') and Portuguese ('pt'), and include from which country the e-mail is
RandomEmail(languages=['es', 'pt']).generate_list(n=10, attributes=True)
```

... and if it is robust under simple perturbations.
```python
from text_sensitivity import compare_accuracy
from text_sensitivity.perturbation import to_upper, add_typos

# Is model accuracy equal when we change all sentences to uppercase?
compare_accuracy(env, model, to_upper)

# Is model accuracy equal when we add typos in words?
compare_accuracy(env, model, add_typos)
```

**Fairness**: see if performance is equal among subgroups.

```python
from text_sensitivity import RandomName

# Generate random Dutch ('nl') and Russian ('ru') names, both 'male' and 'female' (+ return attributes)
RandomName(languages=['nl', 'ru'], sex=['male', 'female']).generate_list(n=10, attributes=True)
```

## Installation
See the [installation](INSTALLATION.md) instructions for an extended installation guide.

| Method | Instructions |
|--------|--------------|
| `pip` | Install from [PyPI](https://pypi.org/project/text-sensitivity/) via `pip3 install text_sensitivity`. |
| Local | Clone this repository and install via `pip3 install -e .` or locally run `python3 setup.py install`.

## Documentation
Full documentation of the latest version is provided at [https://text-sensitivity.readthedocs.io/](https://text-sensitivity.readthedocs.io/).

## Example usage
See [example_usage.md](example_usage.md) to see an example of how the package can be used, or run the lines in `example_usage.py` to do explore it interactively.

## Releases
`text_sensitivity` is officially released through [PyPI](https://pypi.org/project/text-sensitivity/).

See [CHANGELOG.md](CHANGELOG.md) for a full overview of the changes for each version.

## Citation
```bibtex
@misc{text_sensitivity,
  title = {Python package text\_sensitivity},
  author = {Marcel Robeer},
  howpublished = {\url{https://github.com/MarcelRobeer/text_sensitivity}},
  doi = {10.5281/zenodo.14192941},
  year = {2021}
}
```

## Maintenance
### Contributors
- [Marcel Robeer](https://www.uu.nl/staff/MJRobeer) (`@MarcelRobeer`)
- [Elize Herrewijnen](https://www.uu.nl/staff/EHerrewijnen) (`@e.herrewijnen`)

### Todo
Tasks yet to be done:

* Word-level perturbations
* Add fairness-specific metrics:
    - Counterfactual fairness
* Add expected behavior
    - Robustness: equal to prior prediction, or in some cases might expect that it deviates
    - Fairness: may deviate from original prediction
* Tests
    - Add tests for perturbations
    - Add tests for sensitivity testing schemes
* Add visualization ability

## Credits
- Edward Ma. _[NLP Augmentation](https://github.com/makcedward/nlpaug)_. 2019.
- Daniele Faraglia and other contributors. _[Faker](https://github.com/joke2k/faker)_. 2012.
- Marco Tulio Ribeiro, Tongshuang Wu, Carlos Guestrin and Sameer Singh. [Beyond Accuracy: Behavioral Testing of NLP models with CheckList](https://paperswithcode.com/paper/beyond-accuracy-behavioral-testing-of-nlp). _Association for Computational Linguistics_ (_ACL_). 2020.
