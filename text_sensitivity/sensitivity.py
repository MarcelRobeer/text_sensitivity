"""Sensitivity testing, for fairness and robustness."""

from typing import Iterator, List, Optional, Tuple, Union

import instancelib.machinelearning
from genbase import add_callargs, silence_tqdm
from instancelib.analysis.base import label_metrics
from instancelib.environment.text import TextEnvironment
from instancelib.instances.base import InstanceProvider
from instancelib.instances.text import TextInstanceProvider
from instancelib.labels.memory import MemoryLabelProvider
from instancelib.machinelearning.base import AbstractClassifier
from instancelib.typehints import KT, LT
from tqdm.auto import tqdm

from text_sensitivity.data.generate import from_pattern
from text_sensitivity.data.random.string import RandomString, combine_generators
from text_sensitivity.perturbation.base import Perturbation
from text_sensitivity.return_types import LabelMetrics, MeanScore, SuccessTest


def apply_perturbation(dataset: Union[InstanceProvider, TextEnvironment],
                       perturbation: Perturbation) -> Tuple[TextInstanceProvider, MemoryLabelProvider]:
    """Apply a perturbation to a dataset, getting the perturbed instances and corresponding attribute labels.

    Examples:
        Repeat each string twice:

        >>> from text_sensitivity.perturbation.sentences import repeat_k_times
        >>> apply_perturbation(env, repeat_k_times(k=2))

        Add the unrelated string 'This is unrelated.' before each instance:

        >>> from text_sensitivity.perturbation import OneToOnePerturbation
        >>> perturbation = OneToOnePerturbation.from_string(prefix='This is unrelated.')
        >>> apply_perturbation(env, perturbation)

    Args:
        dataset (Union[InstanceProvider, TextEnvironment]): Dataset to apply perturbation to (e.g. all data, train set,
            test set, set belonging to a given label, or subset of data for a (un)protected group).
        perturbation (Perturbation): Perturbation to apply, one-to-one or one-to-many.

    Returns:
        Tuple[TextInstanceProvider, MemoryLabelProvider]: Perturbed instances and corresponding attribute labels.
    """
    if isinstance(dataset, TextEnvironment):
        dataset = dataset.dataset
    if not isinstance(perturbation, Perturbation):
        perturbation = perturbation()

    new_data, attributes = [], []

    for key in dataset:
        for instances, labels in perturbation(dataset[key]):
            new_data.extend(instances) if isinstance(instances, list) else new_data.append(instances)
            attributes.extend(labels) if isinstance(labels, list) else attributes.append(labels)

    instanceprovider = TextInstanceProvider(new_data)
    instanceprovider.add_range(*dataset.get_all())
    labelprovider = MemoryLabelProvider.from_tuples(attributes)

    return instanceprovider, labelprovider


def equal_ground_truth(ground_truth: MemoryLabelProvider, instances: InstanceProvider) -> Iterator[Tuple[KT, LT]]:
    """When you expect the ground-truth label will remain equal after the perturbation is applied.

    Args:
        ground_truth (MemoryLabelProvider): Labelprovider.
        instances (InstanceProvider): Instanceprovider.

    Yields:
        Iterator[Tuple[KT, LT]]: Keys and corresponding labels.
    """
    # TODO: add ability to provide a different expectation of what will happen to the instance labels after perturbation
    for key in instances.keys():
        parent_key = key.split('|')[0] if isinstance(key, str) else str(key)
        parent_key = int(parent_key) if parent_key.isdigit() else parent_key
        yield (key, ground_truth._labeldict[parent_key])


@add_callargs
def compare_metric(env: TextEnvironment,
                   model: AbstractClassifier,
                   perturbation: Perturbation,
                   **kwargs) -> LabelMetrics:
    """Get metrics for each ground-truth label and attribute.

    Examples:
        Compare metric of `model` performance (e.g. accuracy, precision) before and after mapping each instance in a 
        dataset to uppercase.

        >>> from text_sensitivity.perturbation.sentences import to_upper
        >>> compare_metric(env, model, to_upper)

        Compare metric when randomly adding 10 perturbed instances with typos to each instance in a dataset.

        >>> from text_sensitivity.perturbation.characters import add_typos
        >>> compare_metric(env, model, add_typos(n=10))

    Args:
        env (TextEnvironment): Environment containing original instances (`.dataset`)
            and ground-truth labels (`.labels`).
        model (AbstractClassifier): Black-box model to compare metrics on.
        perturbation (Perturbation): Peturbation to apply.

    Returns:
        LabelMetrics: Original label (before perturbation), perturbed label (after perturbation) 
        and metrics for label-attribute pair.
    """
    callargs = kwargs.pop('__callargs__', None)

    # Apply perturbations and get attributes
    instances, attributes = apply_perturbation(env, perturbation)

    # Perform prediction on original instances and perturbed instances
    model_predictions = MemoryLabelProvider.from_tuples(model.predict(instances))

    # Expectation (for now that labels should remain equal)
    ground_truth = MemoryLabelProvider.from_tuples(list(equal_ground_truth(env.labels, instances)))

    lm = [(label, attribute, label_metrics(model_predictions,
                                           ground_truth,
                                           attributes.get_instances_by_label(attribute),
                                           label))
                    for attribute in list(attributes.labelset)
                    for label in list(model_predictions.labelset)]

    return LabelMetrics(instances=instances,
                        label_metrics=lm,
                        callargs=callargs)  


def compare_accuracy(*args, **kwargs):
    """Compare accuracy scores for each ground-truth label and attribute."""
    import pandas as pd
    return pd.DataFrame([(label, attribute, metrics.accuracy)
                         for label, attribute, metrics in compare_metric(*args, **kwargs)],
                        columns=['label', 'attribute', 'accuracy'])


def compare_precision(*args, **kwargs):
    """Compare precision scores for each ground-truth label and attribute."""
    import pandas as pd
    return pd.DataFrame([(label, attribute, metrics.precision)
                         for label, attribute, metrics in compare_metric(*args, **kwargs)],
                        columns=['label', 'attribute', 'precision'])


def compare_recall(*args, **kwargs):
    """Compare recall scores for each ground-truth label and attribute."""
    import pandas as pd
    return pd.DataFrame([(label, attribute, metrics.recall)
                         for label, attribute, metrics in compare_metric(*args, **kwargs)],
                        columns=['label', 'attribute', 'recall'])


@add_callargs
def input_space_robustness(model: AbstractClassifier,
                           generators: List[RandomString],
                           n_samples: int = 100,
                           min_length: int = 0,
                           max_length: int = 100,
                           seed: Optional[int] = 0,
                           **kwargs) -> SuccessTest:
    """Test the robustness of a machine learning model to different input types.

    Example:
        Test a pretrained black-box `model` for its robustness to 1000 random strings (length 0 to 500),
        containing whitespace characters, ASCII (upper, lower and numbers), emojis and Russian Cyrillic characters:

        >>> from text_sensitivity.data.random.string import RandomAscii, RandomCyrillic, RandomEmojis, RandomWhitespace
        >>> input_space_robustness(model, 
        >>>                        [RandomWhitespace(), RandomAscii(), RandomEmojis(base=True), RandomCyrillic('ru')],
        >>>                        n_samples=1000,
        >>>                        min_length=0,
        >>>                        max_length=500)

    Args:
        model (AbstractClassifier): Machine learning model to test.
        generators (List[RandomString]): Random character generators.
        n_samples (int, optional): Number of test samples. Defaults to 100.
        min_length (int, optional): Input minimum length. Defaults to 0.
        max_length (int, optional): Input maximum length. Defaults to 100.
        seed (Optional[int], optional): Seed for reproducibility purposes. Defaults to 0.

    Returns:
        SuccessTest: Percentage of success cases, list of succeeded/failed instances
    """
    callargs = kwargs.pop('__callargs__', None)

    # Combine all generators into one
    generator = combine_generators(*generators, seed=seed)

    # Generate instances
    instances = generator.generate(n=n_samples, min_length=min_length, max_length=max_length)

    # Percentage success, instances that succeeded, instances that failed
    successes: List[List[str]] = []
    failures: List[List[str]] = []

    # Do not perform it batchwise but per instance, in order to return the error-throwing failures
    with silence_tqdm(instancelib.machinelearning):
        for i in tqdm(instances, leave=False):
            try:
                model.predict([instances[i]])
                successes.append(instances[i])
            except Exception:
                failures.append(instances[i])

    return SuccessTest(1.0 if len(instances) == 0 else len(successes) / len(instances),
                       successes,
                       failures,
                       type='safety',
                       subtype='input_space',
                       callargs=callargs)


@add_callargs
def invariance(pattern: str,
               model: AbstractClassifier,
               expectation: Optional[LT] = None,
               **kwargs,
               ) -> SuccessTest:
    """Test for the failure rate under invariance.

    Args:
        pattern (str): String pattern to generate examples from.
        model (AbstractClassifier): Model to test.
        expectation (Optional[LT], optional): Expected outcome values. Defaults to None.
        **kwargs: Optional arguments passed onto the `data.generate.from_pattern()` function.

    Returns:
        SuccessTest: Percentage of success cases, list of succeeded (invariant)/failed (variant) instances
    """
    callargs = kwargs.pop('__callargs__', None)

    # Generate instances from pattern and predict
    instances, _ = from_pattern(pattern, **kwargs)
    predictions = model.predict(instances)

    if expectation is None:
        if len(predictions) == 0:
            return 0.0, [], []
        expectation = predictions[0][-1]
    if not isinstance(expectation, frozenset):
        expectation = frozenset({expectation})

    correct = [instances[id] for id, label in predictions if label == expectation]
    wrong = [instances[id] for id, label in predictions if label != expectation]

    return SuccessTest(1.0 if len(predictions) == 0 else len(correct) / len(predictions),
                       correct,
                       wrong,
                       predictions=predictions,
                       type='sensitivity',
                       subtype='invariance',
                       callargs=callargs)


@add_callargs
def mean_score(pattern: str,
               model: AbstractClassifier,
               selected_label: Optional[LT] = None,
               **kwargs) -> MeanScore:
    """Calculate mean (probability) score for a given label, for data generated from a pattern.

    Args:
        pattern (str): 
        model (AbstractClassifier): Model to generate scores from.
        selected_label (Optional[LT], optional): Label name to select. If None is replaced by the first label.
            Defaults to None.

    Returns:
        MeanScore: Mean score for the selected label, generated instances and label scores.
    """
    callargs = kwargs.pop('__callargs__', None)

    instances, _ = from_pattern(pattern, **kwargs)
    predictions = model.predict_proba_provider(instances)

    if selected_label is None:
        if len(predictions) == 0:
            return
        selected_label = list(model.encoder.labelset)[0]
    if isinstance(selected_label, frozenset):
        selected_label = list(selected_label)[0]

    predictions_by_label = [(instances[id], [proba for label, proba in list(probas) if label == selected_label][0])
                            for id, probas in predictions]

    return MeanScore(scores=[p for _, p in predictions_by_label],
                     label=selected_label,
                     instances=instances,
                     callargs=callargs,
                     **kwargs)
