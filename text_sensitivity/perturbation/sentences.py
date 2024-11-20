"""Create sentence-level perturbations (`text_sensitivity.perturbation.base.Perturbation`)."""

from typing import Optional

from text_sensitivity.perturbation.base import OneToOnePerturbation


def to_upper() -> OneToOnePerturbation:
    """Make all characters in a string uppercase.

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.
    """
    return OneToOnePerturbation.from_function(str.upper, 'not_upper', 'upper')


def to_lower() -> OneToOnePerturbation:
    """Make all characters in a string lowercase.

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.
    """
    return OneToOnePerturbation.from_function(str.lower, 'not_lower', 'lower')


def repeat_k_times(k: int = 10, connector: Optional[str] = ' '):
    """Repeat a string k times.

    Args:
        k (int, optional): Number of times to repeat a string. Defaults to 10.
        connector (Optional[str], optional): Connector between adjacent repeats. Defaults to ' '.

    Returns:
        Perturbation: Object able to apply perturbations on strings or TextInstances.
    """
    if connector is None:
        connector = ''

    def repeat_k(string: str) -> str:
        return connector.join([string] * k)

    return OneToOnePerturbation.from_function(repeat_k, label_to='repeated')
