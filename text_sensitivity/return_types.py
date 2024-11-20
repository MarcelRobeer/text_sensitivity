"""Return types for sensitivity (tests)."""

from typing import List, Optional, Union

from genbase.utils import extract_metrics
from instancelib.labels import LabelProvider, MemoryLabelProvider
from text_explainability.generation.return_types import Instances

from text_sensitivity.ui.notebook import Render


class SuccessTest(Instances):
    def __init__(self,
                 success_percentage: float,
                 successes,
                 failures,
                 predictions: Optional[Union[LabelProvider, list, dict]] = None,
                 type: str = 'robustness',
                 subtype: str = 'input_space',
                 callargs: Optional[dict] = None,
                 **kwargs):
        """Return type for success test.

        Args:
            success_percentage (float): Percentage of successful cases.
            successes (_type_): Instances that succeeded.
            failures (_type_): Instances that failed.
            predictions (Optional[Union[LabelProvider, list, dict]], optional): Predictions to subdivide successes/
                failures into labels. Defaults to None.
            type (str, optional): Type description. Defaults to 'robustness'.
            subtype (str, optional): Subtype description. Defaults to 'input_space'.
            callargs (Optional[dict], optional): Arguments used when the function was called. Defaults to None.
        """
        super().__init__(instances={'successes': successes, 'failures': failures},
                         type=type,
                         subtype=subtype,
                         callargs=callargs,
                         renderer=Render,
                         **kwargs)
        self.success_percentage = success_percentage
        self.predictions = self.__load_predictions(predictions)

    def __load_predictions(self, predictions):
        if predictions is None:
            return None
        if not isinstance(predictions, LabelProvider):
            return MemoryLabelProvider.from_tuples(predictions)
        return predictions

    @property
    def content(self):
        """Content as dictionary."""
        res = {'success_percentage': self.success_percentage,
               'failure_percentage': 1.0 - self.success_percentage,
               'successes': self.instances['successes'],
               'failures': self.instances['failures']}
        if self.predictions is not None:
            res['predictions'] = self.predictions
        return res


class LabelMetrics(Instances):
    def __init__(self,
                 instances,
                 label_metrics,
                 type: Optional[str] = 'sensitivity',
                 subtype: Optional[str] = 'label_metrics',
                 callargs: Optional[dict] = None,
                 **kwargs):
        """Return type for labelwise metrics.

        Args:
            instances (_type_): Instances.
            label_metrics (_type_): Metric for each label.
            type (Optional[str], optional): Type description. Defaults to 'sensitivity'.
            subtype (Optional[str], optional): Subtype description. Defaults to 'label_metrics'.
            callargs (Optional[dict], optional): Arguments used when the function was called. Defaults to None.
        """
        super().__init__(instances, type=type, subtype=subtype, callargs=callargs, renderer=Render, **kwargs)
        self.keys = [k for k, _ in enumerate(label_metrics)]
        self.metric_labels = {k: l for k, (l, _, _) in enumerate(label_metrics)}
        self.metric_attributes = {k: a for k, (_, a, _) in enumerate(label_metrics)}
        self.__metrics = {k: m for k, (_, _, m) in enumerate(label_metrics)}
        self.metrics, self.properties = extract_metrics(self.__metrics)

    @property
    def content(self):
        """Content as dictionary."""
        res = {'label_metrics': [{'label': self.metric_labels[k],
                                  'attribute': self.metric_attributes[k],
                                  'metrics': self.metrics[k]} for k in self.keys]}
        res['metrics'] = self.properties
        return res


class MeanScore(Instances):
    def __init__(self,
                 scores: List[float],
                 label: str,
                 instances,
                 type: Optional[str] = 'sensitivity',
                 subtype: Optional[str] = 'mean_score',
                 callargs: Optional[dict] = None,
                 **kwargs):
        """Return type for `text_sensitivity.mean_score()`.

        Args:
            scores (List[float]): Score for each instance.
            label (str): Name of label.
            instances (_type_): Instances.
            type (Optional[str], optional): Type description. Defaults to 'sensitivity'.
            subtype (Optional[str], optional): Subtype description. Defaults to 'mean_score'.
            callargs (Optional[dict], optional): Arguments used when the function was called. Defaults to None.
        """
        super().__init__(instances, type=type, subtype=subtype, callargs=callargs, renderer=Render, **kwargs)
        self.scores = scores
        self.label = label

    @property
    def content(self):
        """Content as dictionary."""
        return {'scores': self.scores,
                'mean_score': sum(self.scores) / len(self.scores),
                'label': self.label,
                'instances': self.instances}
