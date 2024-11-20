"""Module for sensitivity metrics."""

from typing import Dict, List, Optional, Union

from genbase import Readable
from instancelib.analysis.base import label_metrics
from instancelib.labels import LabelProvider, MemoryLabelProvider
from instancelib.typehints import LT


def binarize(labels: LabelProvider,
             select: Union[int, str, list, frozenset],
             new_label: str = 'priviliged',
             other_label: str = 'unpriviliged') -> MemoryLabelProvider:
    """Convert labels in a LabelProvider to binary labels `new_label` and `other_label`.

    Args:
        labels (LabelProvider): LabelProvider to convert attribute labels to `new_label` and `other_label`.
        select (Union[int, str, list, frozenset]): Label(s) to select.
        new_label (str, optional): Label if attribute falls in selected values. Defaults to 'priviliged'.
        other_label (str, optional): Label if attribute does not fall in selected values. Defaults to 'unpriviliged'.

    Returns:
        MemoryLabelProvider: Attribute labels with either `new_label` or `other_label`.
    """
    if isinstance(select, (int, str)):
        select = [select]
    if isinstance(select, list):
        select = frozenset(select)
    new_label = frozenset({new_label})
    other_label = frozenset({other_label})

    def create_new_labels():
        for label in labels.labelset:
            for instance in labels.get_instances_by_label(label):
                yield instance, new_label if label in select else other_label

    return MemoryLabelProvider.from_tuples(list(create_new_labels()))


class Metric(Readable):
    def __init__(self,
                 name: str,
                 all: float,
                 priviliged: float,
                 unpriviliged: float,
                 abbr: Optional[str] = None):
        """Named metric.

        Args:
            name (str): Name of metric.
            all (float): Score of all
            priviliged (float): Score of priviliged group (e.g. sex = male).
            unpriviliged (float): Score for unpriviliged group (e.g. sex = not male).
            abbr (Optional[str], optional): Abbreviation of name. Defaults to None.
        """
        self.name = name
        self.all = all
        self.priviliged = priviliged
        self.unpriviliged = unpriviliged
        if abbr is not None:
            self.abbr = abbr

    @property
    def ratio(self):
        r"""Ratio between unpriviliged and priviliged scores.

        .. math::
           \frac{\text{metric} | A = \text{unprivileged}}{\text{metric} | A = \text{privileged}}
        """
        if self.priviliged == 0.:
            return float('inf')
        return self.unpriviliged / self.priviliged

    @property
    def difference(self):
        r"""Difference between unpriviliged and priviliged scores.

        .. math::
           \text{metric} | A = \text{unprivileged} - \text{metric} | A = \text{privileged}
        """
        return self.unpriviliged - self.priviliged


class FairnessMetrics:
    def __init__(self,
                 attributes: Dict[str, LabelProvider],
                 ground_truth: LabelProvider,
                 predictions: LabelProvider,
                 pos_label: Optional[LT] = None,
                 priviliged_groups: Optional[List[Dict[str, LT]]] = None,
                 unpriviliged_groups: Optional[List[Dict[str, LT]]] = None):
        """Calculate fairness metrics for provided attributes, ground truth values and predictions.

        Args:
            attributes (Dict[str, LabelProvider]): Dictionary of named attributes (e.g. sex, ethnicity, ...).
            ground_truth (LabelProvider): Ground truth labels of instances.
            predictions (LabelProvider): Predicted labels of instances.
            pos_label (Optional[LT], optional): Positive label. Defaults to None.
            priviliged_groups (Optional[List[Dict[str, LT]]], optional): Dictionary with the priviliged group names 
                for some attributes. Defaults to None.
            unpriviliged_groups (Optional[List[Dict[str, LT]]], optional): Dictionary with the unpriviliged group names 
                for some attributes. Defaults to None.

        Example:
            Calculate fairness metrics for `sex` (male/female) and `race` (Caucasian, Hispanic, African-American):

            >>> attributes = {'sex': ..., 'race': ..., 'name': ...}
            >>> FairnessMetric(attributes=attributes,
            ...                ground_truth=ground_truth,
            ...                predictions=predictions,
            ...                priviliged_groups={'sex': 'male', 'race': 'caucasian'})
        """
        self._original_attributes = attributes
        self.attributes = self.__binarize(attributes,
                                          priviliged_groups,
                                          unpriviliged_groups)
        self.ground_truth = ground_truth
        self.predictions = predictions
        self.pos_label = list(self.predictions.labelset)[-1] if pos_label is None \
            else pos_label

    def __binarize(self,
                   attributes,
                   priviliged_groups,
                   unpriviliged_groups):
        """Binarize attributes to priviliged/unpriviliged."""
        res = {}
        for k, v in attributes.items():
            if k in priviliged_groups:
                res[k] = binarize(v, select=priviliged_groups[k])
            elif k not in priviliged_groups and k in unpriviliged_groups:
                res[k] = binarize(v, select=v.labelset - frozenset(unpriviliged_groups[k]))        
        return res

    @property
    def all(self):
        """All indices."""
        return frozenset.intersection(frozenset(self.ground_truth._labeldict.keys()),
                                      frozenset(self.predictions._labeldict.keys()))

    @property
    def priviliged(self):
        """Indices of priviliged instances."""
        p = frozenset.union(*[v.get_instances_by_label('priviliged') for v in self.attributes.values()])
        return frozenset.intersection(self.all, p)

    @property
    def unpriviliged(self):
        """Indices of unpriviliged instances."""
        u = frozenset.union(*[v.get_instances_by_label('unpriviliged') for v in self.attributes.values()])
        return frozenset.intersection(self.all, u)

    def label_metrics(self, keys):
        """Calculate label metrics for given keys."""
        return label_metrics(self.ground_truth, self.predictions, keys, label=self.pos_label)

    def _metric_from_fn(self, name: str, fn, abbr: Optional[str] = None):
        def try_fn(keys):
            try:
                return fn(self.label_metrics(keys))
            except ZeroDivisionError:
                return 0.0

        return Metric(name=name,
                      all=try_fn(self.all),
                      priviliged=try_fn(self.priviliged),
                      unpriviliged=try_fn(self.unpriviliged),
                      abbr=abbr)

    def _metric_from_conf_mat(self, name: str, fn, abbr: Optional[str] = None):
        def conf_fn(metric):
            TP = len(metric.true_positives)
            FP = len(metric.false_positives)
            FN = len(metric.false_negatives)
            TN = len(metric.true_negatives)
            return fn(TP, FP, FN, TN)

        return self._metric_from_fn(name=name, fn=conf_fn, abbr=abbr)

    @property
    def statistical_parity(self):
        """Statistical parity :math:`Pr(Y = 1) = P/(P+N)`."""
        def base_rate(tp, fp, fn, tn):
            return (tp + fp) / (tp + fp + fn + tn)
        return self._metric_from_conf_mat(name='statistical_parity',
                                          fn=base_rate)

    @property
    def accuracy(self):
        """Accuracy: :math:`(TP + TN)/(P + N)`."""
        return self._metric_from_fn(name='accuracy', fn=(lambda x: x.accuracy))

    @property
    def precision(self):
        """Precision: :math:`TP / (TP + FP)`."""
        return self._metric_from_fn(name='precision', fn=(lambda x: x.precision))

    @property
    def recall(self):
        """Recall: :math:`TP / (TP + FN)`"""
        return self._metric_from_fn(name='recall', fn=(lambda x: x.recall))

    @property
    def error_rate(self):
        """Error rate: :math:`(FP + FN) / (TP + FP + FN + TN)`."""
        def err_rate(tp, fp, fn, tn):
            return (fp + fn) / (tp + fp + fn + tn)
        return self._metric_from_conf_mat(name='error_rate', abbr='ERR', fn=err_rate)

    @property
    def false_discovery_rate(self):
        """False Discovery Rate (FDR): :math:`FP / (TP + FP)`."""
        def fdr(tp, fp, fn, tn):
            return fp / (tp + fp)
        return self._metric_from_conf_mat(name='false_discovery_rate', abbr='FDR', fn=fdr)

    @property
    def false_negative_rate(self):
        """False Negative Rate (FNR): :math:`FN / (FP + TP)`."""
        def fnr(tp, fp, fn, tn):
            return fn / (tp + fp)
        return self._metric_from_conf_mat(name='false_negative_rate', abbr='FNR', fn=fnr)

    @property
    def false_omission_rate(self):
        """False Omission Rate (FOR): :math:`FN / (TN + FN)`."""
        def fomr(tp, fp, fn, tn):
            return fn / (tn + fn)
        return self._metric_from_conf_mat(name='false_omission_rate', abbr='FOR', fn=fomr)

    @property
    def false_positive_rate(self):
        """False Positive Rate (FPR): :math:`FP / (TN + FN)`."""
        def fpr(tp, fp, fn, tn):
            return fp / (tn + fn)
        return self._metric_from_conf_mat(name='false_positive_rate', abbr='FPR', fn=fpr)

    @property
    def negative_predictive_value(self):
        """Negative Predictive Value (NPV): :math:`TN / (TN + FN)`."""
        def npv(tp, fp, fn, tn):
            return tn / (tn + fn)
        return self._metric_from_conf_mat(name='negative_predictive_value', abbr='NPV', fn=npv)

    @property
    def positive_predicted_value(self):
        """Positive Predictive Value (NPV): :math:`TP / (TP + FP)`, alias for precision."""
        def ppv(tp, fp, fn, tn):
            return tn / (tn + fn)
        return self._metric_from_conf_mat(name='positive_predicted_value', abbr='PPV', fn=ppv)

    @property
    def true_negative_rate(self):
        """True Negative Rate (TNR), alias for `specificity`."""
        metric = self.sensitivity
        metric.name = 'true_negative_rate'
        metric.abbr = 'TNR'
        return metric

    @property
    def true_positive_rate(self):
        """True Positive Rate (TPR), alias for `recall`."""
        metric = self.recall
        metric.name = 'true_positive_rate'
        metric.abbr = 'TPR'
        return metric

    @property
    def selection_rate(self):
        """Selection rate: :math:`(TP + FP) / (TP + FP + TN + FN)`."""
        def sr(tp, fp, fn, tn):
            return (tp + fp) / (tp + fp + tn + fn)
        return self._metric_from_conf_mat(name='selection_rate', fn=sr)

    @property
    def sensitivity(self):
        """Sensitivity, alias for `recall`."""
        metric = self.recall
        metric.name = 'sensitivity'
        return metric

    @property
    def specificity(self):
        """Specificity: :math:`TN / (FN + TN)`."""
        def tnr(tp, fp, fn, tn):
            return tn / (fn + tn)
        return self._metric_from_conf_mat(name='specificity', fn=tnr)

    @property
    def disparate_impact(self):
        """Alias for statistical parity ratio."""
        return self.statistical_parity.ratio

    @property
    def mean_difference(self):
        """Alias for statistical parity difference."""
        return self.statistical_parity.difference
