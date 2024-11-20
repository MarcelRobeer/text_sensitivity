"""Extension of `genbase.ui.notebook` for custom rendering of `text_sensitivity."""

import copy

from genbase.ui import get_color
from genbase.ui.notebook import Render as BaseRender
from genbase.ui.notebook import format_instances
from text_explainability.ui.notebook import default_renderer, get_meta_descriptors

TEST_EXP = {'robustness+input_space': 'This sensitivity test checks if your model is able to handle ' +
                                      'different input character (sequences) without throwing errors.',
            'sensitivity+invariance': 'This sensitivity test has the assumption that all instances will have the ' +
                                      'same expected prediction for all instances.',
            'sensitivity+label_metrics': 'This sensitivity test compares metrics calculated on a dataset (e.g. ' +
                                         'train set) before and after applying a dataset-wide (global) perturbation.'}
__acc = 'https://en.wikipedia.org/wiki/Accuracy_and_precision#In_binary_classification'
__prec_rec = 'https://en.wikipedia.org/wiki/Precision_and_recall'
__tpfptnfn = 'https://en.wikipedia.org/wiki/Confusion_matrix'
METRIC_MAP = {'accuracy': ('Accuracy', 'Acc.', __acc),
              'f1': ('F1-score', 'F1', 'https://en.wikipedia.org/wiki/F-score'),
              'precision': ('Precision', 'Prec.', __prec_rec),
              'recall': ('Recall', 'Rec.', __prec_rec),
              'wss': ('Work Saved over Sampling (WSS)', 'WSS', 'https://pubmed.ncbi.nlm.nih.gov/16357352/'),
              'true_positives': ('True Positives (TP)', 'TP', __tpfptnfn),
              'true_negatives': ('True Negatives (TN)', 'TN', __tpfptnfn),
              'false_positives': ('False Positives (FP)', 'FP', __tpfptnfn),
              'false_negatives': ('False Negatives (FN)', 'FN', __tpfptnfn)}
PERC = ['accuracy', 'f1', 'precision', 'recall', 'wss']


def h(title) -> str:
    """Format title as HTML h3."""
    return f'<h3>{title}</h3>'


def success_test_renderer(meta: dict, content: dict, **renderargs) -> str:
    """Render `text_sensitivity.return_types.SuccessTest` as HTML."""
    def none_to_show(success_failure: str, succeeded_failed: str):
        return f'<p>No {success_failure} to show, because all instances {succeeded_failed}.</p>'

    n_success, n_fail = len(content['successes']), len(content['failures'])
    kwargs = {'predictions': content['predictions']} if 'predictions' in content else {}

    color = get_color(content['success_percentage'],
                      min_value=0.0,
                      max_value=1.0,
                      colorscale=[(0, '#A50026'), (0.5, '#BBBB00'), (1.0, '#006837')])
    html = h('Test results')
    html += f'<p style="font-size: 110%">Success: <b style="color: {color}">{content["success_percentage"]:0.2%}</b> '
    html += f'({n_success} out of {n_success + n_fail}).</p>'
    html += h('Success')
    html += format_instances(content['successes'], **kwargs) if n_success > 0 \
        else none_to_show('successes', 'failed')
    html += h('Failures')
    html += format_instances(content['failures'], **kwargs) if n_fail \
        else none_to_show('failures', 'succeeded')
    return html


def metrics_renderer(meta: dict, content: dict, **renderargs) -> str:
    """Render `text_sensitivity.return_types.Metrics` as HTML."""
    for label in ['confusion_matrix', 'pos_label', 'neg_label', 'wss']:
        content['metrics'].remove(label)
        for m in content['label_metrics']:
            _ = m['metrics'].pop(label, None)

    html = h('Results')
    has_attribute = all('attribute' in row for row in content['label_metrics'])

    from collections import defaultdict
    METRICS_ORDER = defaultdict(default_factory=lambda x: x,
                                accuracy=0,
                                precision=1,
                                recall=2,
                                f1=3,
                                true_positives=4,
                                false_positives=5,
                                true_negatives=6,
                                false_negatives=7)

    # Sort metrics
    metrics = sorted(content['metrics'], key=METRICS_ORDER.get)

    header_ext = ['Predicted Label', 'Attribute'] if has_attribute else ['Predicted Label']
    header = ''.join([f'<th>{h}</th>' for h in header_ext + [METRIC_MAP.get(m, [m, m])[1] for m in metrics]])

    def get_label(row):
        label = [f'<kbd>{row["label"]}</kbd>']
        return label + [f'<kbd>{row["attribute"]}</kbd>'] if has_attribute else label

    label_metrics = [get_label(row) + [f'{row["metrics"][m]:.2%}'
                                       if str.lower(m) in PERC and isinstance(row['metrics'][m], (int, float))
                                       else f'{row["metrics"][m]}' for m in metrics if m in row['metrics']]
                                       for row in content['label_metrics']]

    table_content = ''.join('<tr>' + ''.join(f'<td>{metric}</td>' for metric in lm) + '</tr>' for lm in label_metrics)
    html += f'<div class="table-wrapper"><table><tr>{header}</tr>{table_content}</table></div>'

    html += h('Metrics included')
    html += '<ul>'
    for m in metrics:
        html += f'<li><a href="{METRIC_MAP[m][-1]}" target="_blank">{METRIC_MAP[m][0]}</a></li>' if m in METRIC_MAP \
            else f'<li>{m}</li>'
    html += '</ul>'
    return html 


def score_renderer(meta: dict, content: dict, **renderargs) -> str:
    """Render score as HTML."""
    html = h('Mean score')
    html += f'<p>Mean score for label <kbd>{content["label"]}</kbd>: <b>{content["mean_score"]:.3f}</b> ' 
    html += f'(average over {len(content["instances"])} instances).</p>'
    html += h('Generated instances')
    html += format_instances(content['instances'], **{'score': content['scores']})
    return html


class Render(BaseRender):
    def __init__(self, *configs):
        """Rendered for `text_sensitivity`."""
        super().__init__(*configs) 
        self.main_color = '#D32F2F'
        self.package_link = 'https://text-sensitivity.readthedocs.io/'

    @property
    def tab_title(self):
        """Title of main tab."""
        return 'Sensitivity Test Results'

    @property
    def custom_tab_title(self):
        """Title of custom tab."""
        return 'Test Settings'

    def get_renderer(self, meta: dict):
        """Get rendererer depending on meta descriptor."""
        type, subtype, _ = get_meta_descriptors(meta)

        if type == 'safety':
            if subtype == 'input_space':
                return success_test_renderer
        if subtype == 'invariance':
            return success_test_renderer
        elif subtype == 'label_metrics':
            return metrics_renderer
        elif subtype == 'mean_score':
            return score_renderer
        return default_renderer

    def format_title(self, title: str, h: str = 'h1', **renderargs) -> str:
        """Generic formatting for titles."""
        return super().format_title(title, h=h, **renderargs).replace('_', ' ').title()

    def render_subtitle(self, meta: dict, content, **renderargs) -> str:
        """Generic formatting for subtitles."""
        type, subtype, _ = get_meta_descriptors(meta)
        name = f'{type}+{subtype}'
        return self.format_subtitle(TEST_EXP[name]) if name in TEST_EXP else ''

    def custom_tab(self, config: dict, **renderargs) -> str:
        """Custom tab, showing call arguments (`callargs`) for a sensitivity test."""
        meta = config["META"]
        if 'callargs' not in meta:
            return ''
        try:
            callargs = copy.deepcopy(meta['callargs'])
        except TypeError:
            callargs = copy.copy(meta['callargs'])
        _ = callargs.pop('__name__', None)
        _ = callargs.pop('model', None)
        if 'kwargs' in callargs:
            kwargs = callargs.pop('kwargs')
            for k, v in kwargs.items():
                callargs[k] = v

        def fmt(k, v) -> str:
            if isinstance(v, list):
                return '<ul>' + ''.join([f'<li>{fmt(k, v_)}</li>' for v_ in v]) + '</ul>'
            elif isinstance(v, dict):
                if 'dataset' in v and 'labels' in v:
                    html = f'<kbd>{v["__class__"]}</kbd>' if '__class__' in v else ''
                    return html + format_instances(v['dataset'], label=v['labels'])
                if '__class__' in v:
                    if v['__class__'].startswith('text_sensitivity.data.random.string'):
                        options = v['options']
                        if isinstance(options, str):
                            options = f'"{options}"'
                        return f'<kbd>{v["__class__"]}</kbd> ({options})'
            elif str.lower(k) == 'expectation':
                return f'<kbd>{v}</kbd>'
            return str(v)

        html = ''.join([f'<tr><td>{k}:</td><td>{fmt(k, v)}</td></tr>' for k, v in callargs.items()])
        return f'<div class="table-wrapper"><table class="sensitivity-test-settings">{html}</table></div>'
