r"""Apply perturbations to TextInstances and/or strings, generating one or many new instances."""

import copy
import itertools
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple, Union

import numpy as np
from genbase import Readable
from instancelib.instances.text import MemoryTextInstance, TextInstance
from instancelib.typehints import KT, LT
from nlpaug.base_augmenter import Augmenter
from text_explainability.decorators import text_instance
from text_explainability.utils import default_detokenizer, default_tokenizer


def oneway_dictionary_mapping(instance: TextInstance,
                              dictionary: Dict[str, List[str]],
                              label_from: LT,
                              label_to: LT,
                              n: int,
                              tokenizer: Callable[[str], List[str]],
                              detokenizer: Callable[[List[str]], str]) -> Iterator[Optional[Tuple[str, LT, LT]]]:
    """Create corresponding replacements for tokens in a `TextInstance`.

    Args:
        instance (TextInstance): Instance to create mapping for.
        dictionary (Dict[str, List[str]]): Options for each token.
        label_from (LT): Label of original element.
        label_to (LT): Label of element with replacements applied.
        n (int): Number of replacements to pick.
        tokenizer (Callable[[str], List[str]]): Tokenize string into sequence of tokens.
        detokenizer (Callable[[List[str]], str]): Detokenize sequence of tokens to string.

    Yields:
        Iterator[Optional[Tuple[str, LT, LT]]]: Detokenized instance, original label and replaced label.
    """
    tokenized = tokenizer(instance.data)

    # Get all options
    options = {i: dictionary[a] for i, a in enumerate(tokenized) if a in dictionary.keys()}
    option_keys = list(options.keys())
    all_options = list(itertools.product(*options.values()))

    # Pick up to N random replacements and apply them
    for idx in set(np.random.randint(len(all_options), size=n)):
        current_option = all_options[idx]
        new_tokenized = copy.deepcopy(tokenized)
        for i, option in enumerate(current_option):
            new_tokenized[option_keys[i]] = option
        if tokenized != new_tokenized:
            yield detokenizer(new_tokenized), label_from, label_to


def one_to_one_dictionary_mapping(instance: TextInstance,
                                  dictionary: Dict[str, List[str]],
                                  label_from: LT,
                                  label_to: LT,
                                  tokenizer: Callable[[str], List[str]],
                                  detokenizer: Callable[[List[str]], str]) -> Optional[Tuple[str, LT, LT]]:
    """Create one-to-one replacement for a `TextInstance`.

    Args:
        instance (TextInstance): Instance to create mapping for.
        dictionary (Dict[str, List[str]]): Options for each token.
        label_from (LT): Label of original element.
        label_to (LT): Label of element with replacements applied.
        tokenizer (Callable[[str], List[str]]): Tokenize string into sequence of tokens.
        detokenizer (Callable[[List[str]], str]): Detokenize sequence of tokens to string.

    Yields:
        Optional[Tuple[str, LT, LT]]: None if no change applied, or tuple containing detokenized instance, original 
            label and replaced label.
    """
    res = list(oneway_dictionary_mapping(instance, dictionary, label_from=label_from, label_to=label_to,
                                         tokenizer=tokenizer, detokenizer=detokenizer, n=1))
    return res[0] if res else None


def one_to_many_dictionary_mapping(instance: TextInstance,
                                   dictionary: Dict[str, List[str]],
                                   label_from: LT,
                                   label_to: LT,
                                   n: int,
                                   tokenizer: Callable[[str], List[str]],
                                   detokenizer: Callable[[List[str]], str]) -> Optional[List[Tuple[str, LT, LT]]]:
    """Create one-to-many replacement for a `TextInstance`.

    Args:
        instance (TextInstance): Instance to create mapping for.
        dictionary (Dict[str, List[str]]): Options for each token.
        label_from (LT): Label of original element.
        label_to (LT): Label of element with replacements applied.
        n (int): Number of replacements for each instance.
        tokenizer (Callable[[str], List[str]]): Tokenize string into sequence of tokens.
        detokenizer (Callable[[List[str]], str]): Detokenize sequence of tokens to string.

    Yields:
        Optional[List[Tuple[str, LT, LT]]]: None if no change applied, or list of tuples containing detokenized 
            instance, original label and replaced label.
    """
    res = list(oneway_dictionary_mapping(instance, dictionary, label_from=label_from, label_to=label_to,
                                         tokenizer=tokenizer, detokenizer=detokenizer, n=n))
    res = list(filter(None, res))
    if len(res) == 0:
        return None
    return res


def as_list(x) -> list:
    """Ensure an element `x` is a list."""
    return [x] if not isinstance(x, Iterable) or isinstance(x, str) else x


def format_identifier(instance, key):
    """Format identifier of child."""
    return f'{instance.identifier}|{key}'


class Perturbation(Readable):
    def __init__(self,
                 perturbation_function: Callable):
        """Apply a perturbation function to a single `TextInstance`.

        Args:
            perturbation_function (Callable): Perturbation function to apply, 
                including attribute label of original instance and resulting instance(s). 
                Should return None if no perturbation has been applied.
        """
        self.perturbation_function = perturbation_function

    @classmethod
    def from_dictionary(cls, *args, **kwargs) -> 'Perturbation':
        """Construct a `Perturbation` from a dictionary."""
        raise NotImplementedError('Implemented in subclasses.')  

    @classmethod
    def from_dict(cls, *args, **kwargs):
        """Alias for `Perturbation.from_dictionary()`."""
        return cls.from_dictionary(*args, **kwargs)

    @classmethod
    def from_function(cls,
                      function: Callable[[str], Optional[Union[str, Sequence[str]]]],
                      label_from: LT = 'original',
                      label_to: LT = 'perturbed'):
        """Construct a `Perturbation` from a perturbation applied to a string.

        Example:
            Make each sentence uppercase:

            >>> OneToOnePerturbation(str.upper, 'not_upper', 'upper')

        Args:
            function (Callable[[str], Optional[Union[str, Sequence[str]]]]): Function to apply 
                to each string. Return None if no change was applied.
            label_from (LT, optional): Attribute label of original instance. Defaults to 'original'.
            label_to (LT, optional): Attribute label of perturbed instance. Defaults to 'perturbed'.
        """
        @text_instance
        def perturbation_function(instance: TextInstance) -> Optional[Tuple[Union[str, Sequence[str]], LT, LT]]:
            res = function(str(instance.data))
            return None if res is None else res, label_from, label_to

        return cls(perturbation_function)

    @classmethod
    def from_string(cls, *args, **kwargs):
        """Construct a `Perturbation` from a string."""
        raise NotImplementedError('Implemented in subclasses.')

    @classmethod
    def from_str(cls, *args, **kwargs):
        """Alias for `Perturbation.from_string()`."""
        return cls.from_string(*args, **kwargs)

    @text_instance
    def perturb(self, instance: TextInstance):
        """Apply perturbation to a single TextInstance."""
        raise NotImplementedError('Implemented in subclasses.')

    @text_instance
    def __call__(self, instance: TextInstance):
        """Apply perturbation to a single TextInstance."""
        return self.perturb(instance)


class OneToOnePerturbation(Perturbation):
    def __init__(self,
                 perturbation_function: Callable[[TextInstance], Optional[Tuple[str, LT, LT]]]):
        """Apply a perturbation function to a single `TextInstance`, getting a single result per instance.

        Args:
            perturbation_function (Callable): Perturbation function to apply, 
                including attribute label of original instance and the resulting instance.
                Should return None if no perturbation has been applied.
        """
        super().__init__(perturbation_function)

    @classmethod
    def from_dictionary(cls,
                        dictionary: Dict[str, str],
                        label_from: LT,
                        label_to: LT,
                        tokenizer: Callable = default_tokenizer,
                        detokenizer: Callable = default_detokenizer):
        """Construct a `OneToOnePerturbation` from a dictionary.

        Example:
            Replace the word 'a' or 'an' (indefinite article) with 'the' (definite article) 
            in each instance. The default tokenizer/detokenizer assumes word-level tokens:

            >>> replacements = {'a': 'the',
            >>>                 'an': 'the'}
            >>> OneToOnePerturbation.from_dictionary(replacement,
            >>>                                      label_from='indefinite',
            >>>                                      label_to='definite')

            Replace the character '.' with '!' (character-level replacement):
            >>> from text_explainability import character_tokenizer, character_detokenizer
            >>> OneToOnePerturbation.from_dictionary({'.': '!'},
            >>>                                      label_from='not_excited',
            >>>                                      label_to='excited',
            >>>                                      tokenizer=character_tokenizer,
            >>>                                      detokenizer=character_detokenizer)

        Args:
            dictionary (Dict[str, str]): Lookup dictionary to map tokens (e.g. words, characters).
            label_from (LT): Attribute label of original instance (left-hand side of dictionary).
            label_to (LT): Attribute label of perturbed instance (right-hand side of dictionary).
            tokenizer (Callable, optional): Function to tokenize instance data (e.g. words, characters).
                Defaults to default_tokenizer.
            detokenizer (Callable, optional): Function to detokenize tokens into instance data.
                Defaults to default_detokenizer.
        """
        # TODO: add case-sensitivity
        @text_instance
        def perturbation_function(instance: TextInstance) -> Optional[Tuple[str, LT, LT]]:
            return one_to_one_dictionary_mapping(instance,
                                                 dictionary={k: as_list(v) for k, v in dictionary.items()},
                                                 label_from=label_from,
                                                 label_to=label_to,
                                                 tokenizer=tokenizer,
                                                 detokenizer=detokenizer)

        return cls(perturbation_function)

    @classmethod
    def from_tuples(cls,
                    tuples: List[Tuple[str, str]],
                    label_from: LT,
                    label_to: LT,
                    tokenizer: Callable = default_tokenizer,
                    detokenizer: Callable = default_detokenizer):
        """Construct a `OneToOnePerturbation` from tuples.

        A function is constructed where if first aims to perform the mapping from the 
        tokens on the left-hand side (LHS) to the right-hand side (RHS), and if this has no 
        result it aims to perform the mapping from the tokens on the RHS to the LHS.

        Example:
            For example, if `[('he', 'she')]` with `label_from='male'` and `label_to='female'` 
            is provided it first checks whether the tokenized instance contains the word `'he'` 
            (and if so applies the perturbation and returns), and otherwise aims to map `'she'` 
            to `'he'`. If neither is possible, it returns None.

            >>> tuples = [('he', 'she'),
            >>>.          ('his', 'her')]
            >>> OneToOnePerturbation.from_tuples(tuples, label_from='male', label_to='female')

        Args:
            tuples (List[Tuple[str, str]]): Lookup tuples to map tokens (e.g. words, characters).
            label_from (LT): Attribute label of original instance (left-hand side of tuples).
            label_to (LT): Attribute label of perturbed instance (right-hand side of tuples).
            tokenizer (Callable, optional): Function to tokenize instance data (e.g. words, characters).
                Defaults to default_tokenizer.
            detokenizer (Callable, optional): Function to detokenize tokens into instance data.
                Defaults to default_detokenizer.        
        """
        dictionary_from = {k: as_list(v) for k, v in tuples}
        dictionary_to = {v: as_list(k) for k, v in tuples}

        @text_instance
        def perturbation_function(instance: TextInstance) -> Optional[Tuple[str, LT, LT]]:
            first_res = one_to_one_dictionary_mapping(instance,
                                                      dictionary=dictionary_from,
                                                      label_from=label_from,
                                                      label_to=label_to,
                                                      tokenizer=tokenizer,
                                                      detokenizer=detokenizer)
            if first_res is not None:
                return first_res
            return one_to_one_dictionary_mapping(instance,
                                                 dictionary=dictionary_to,
                                                 label_from=label_to,
                                                 label_to=label_from,
                                                 tokenizer=tokenizer,
                                                 detokenizer=detokenizer)

        return cls(perturbation_function)

    @classmethod
    def from_list(cls,
                  mapping_list: List[str],
                  label_from: LT = 'original',
                  label_to: LT = 'perturbed',
                  tokenizer: Callable = default_tokenizer,
                  detokenizer: Callable = default_detokenizer):
        """Construct a `OneToOnePerturbation` from a list.

        A function is constructed that aims to map any value in the list to any other value 
        in the list.

        Example:
            For example, if list `['Amsterdam', 'Rotterdam', 'Utrecht']` is provided it aims to map 
            'Amsterdam' to 'Rotterdam' or 'Utrecht', 'Rotterdam' to 'Amsterdam' to 'Utrecht' and 
            'Utrecht' to 'Rotterdam' or 'Amsterdam'. If None of these is possible, it returns None.

            >>> map_list = ['Amsterdam', 'Rotterdam', 'Utrecht']
            >>> OneToOnePerturbation.from_list(map_list)

        Args:
            mapping_list (List[str]): Lookup list of tokens (e.g. words, characters).
            label_from (LT): Attribute label of original instance (non-replaced).
            label_to (LT): Attribute label of perturbed instance (replaced).
            tokenizer (Callable, optional): Function to tokenize instance data (e.g. words, characters).
                Defaults to default_tokenizer.
            detokenizer (Callable, optional): Function to detokenize tokens into instance data.
                Defaults to default_detokenizer.        
        """
        # TODO: add case-sensitivity
        mapping_dict = {k: v for k, v in set(list(itertools.combinations(mapping_list, 2)))}
        return OneToManyPerturbation.from_dictionary(mapping_dict,
                                                     label_from=label_from,
                                                     label_to=label_to,
                                                     tokenizer=tokenizer,
                                                     detokenizer=detokenizer)

    @classmethod
    def from_string(cls,
                    prefix: Optional[str] = None,
                    suffix: Optional[str] = None,
                    replacement: Optional[str] = None,
                    label_from: LT = 'original',
                    label_to: LT = 'perturbed',
                    connector: str = ' ',
                    connector_before: Optional[str] = None,
                    connector_after: Optional[str] = None):
        r"""Construct a `OneToOnePerturbation` from a string (replacement, prefix and/or suffix).

        Provides the ability to replace each instance string with a new one, add a prefix to 
        each instance string and/or add a suffix to each instance string. At least one of `prefix`, 
        `suffix` or `replacement` should be a string to apply the replacement.

        Example:
            Add a random unrelated string 'Dit is ongerelateerd.' to each instance (as prefix), where you 
            expect that predictions will not change:

            >>> OneToOnePerturbation.from_string(prefix='Dit is ongerelateerd.', label_to='with_prefix')

            Or add a negative string 'Dit is negatief!' to each instance (as suffix on the next line), 
            where you expect that instances will have the same label or become more negative:

            >>> OneToOnePerturbation.from_string(suffix='Dit is negatief!',
            >>>                                  connector_after='\n',
            >>>                                  label_to='more_negative')

            Or replace all instances with 'UNKWRDZ':
            >>> OneToOnePerturbation.from_string(replacement='UNKWRDZ')

        Raises:
            ValueError: At least one of `prefix`, `suffix` and `replacement` should be provided.

        Args:
            label_from (LT): Attribute label of original instance. Defaults to 'original'.
            label_to (LT): Attribute label of perturbed instance. Defaults to 'perturbed'.
            prefix (Optional[str], optional): Text to add before `instance.data`. Defaults to None.
            suffix (Optional[str], optional): Text to add after `instance.data`. Defaults to None.
            replacement (Optional[str], optional): Text to replace `instance.data` with. Defaults to None.
            connector (str): General connector between `prefix`, `instance.data` and `suffix`. Defaults to ' '.
            connector_before (Optional[str], optional): Overrides connector between `prefix` and `instance.data`, 
                if it is None `connector` is used. Defaults to None.
            connector_after (Optional[str], optional): Overrides connector between `instance.data` and `suffix`, 
                if it is None `connector` is used. Defaults to None.
        """
        if prefix is None and suffix is None and replacement is None:
            raise ValueError('At least one of prefix, suffix and replacement should be provided.')

        if prefix is None:
            connector_before = ''
        if suffix is None:
            connector_after = ''     
        if connector_before is None:
            connector_before = connector
        if connector_after is None:
            connector_after = connector
        prefix = '' if prefix is None else prefix
        suffix = '' if suffix is None else suffix

        @text_instance
        def perturbation_function(instance: TextInstance) -> Optional[Tuple[str, LT, LT]]:
            text = replacement if replacement is not None else instance.data
            return f'{prefix}{connector_before}{text}{connector_after}{suffix}', label_from, label_to

        return cls(perturbation_function)

    @classmethod
    def from_nlpaug(cls,
                    augmenter: Augmenter,
                    label_from: LT = 'original',
                    label_to: LT = 'perturbed',
                    **augment_kwargs):
        """Construct a `OneToOnePerturbation` from a `nlpaug`_ Augmenter.

        Example:
            Add random spaces to words in a sentence using `nlpaug.augmenter.word.SplitAug()`:

            >>> import nlpaug.augmenter.word as naw
            >>> OneToOnePerturbation.from_nlpaug(naw.SplitAug(), label_to='with_extra_space')

            Or add keyboard typing mistakes to lowercase characters in a sentence using 
            `nlpaug.augmenter.char.KeyboardAug()`:

            >>> import nlpaug.augmenter.char as nac
            >>> augmenter = nac.KeyboardAug(include_upper_case=False,
            >>>                             include_special_char=False,
            >>>                             include_numeric=False)
            >>> OneToOnePerturbation.from_nlpaug(augmenter, label_from='no_typos', label_to='typos')

        Args:
            augmenter (Augmenter): Class with `.augment()` function applying a perturbation to a string.
            label_from (LT, optional): Attribute label of original instance. Defaults to 'original'.
            label_to (LT, optional): Attribute label of perturbed instance. Defaults to 'perturbed'.
            **augment_kwargs: Optional arguments passed to `.augment()` function.

        .. _nlpaug:
            https://github.com/makcedward/nlpaug
        """
        # assert isinstance(augmenter, Augmenter), \
        #     'Can only construct from nlpaug.base_augmenter.Augmenter subclasses.'

        @text_instance
        def perturbation_function(instance: TextInstance) -> Optional[str]:
            try:
                return augmenter.augment(str(instance.data), n=1, **augment_kwargs)[0]
            except:  # noqa: E722
                return None

        return cls.from_function(perturbation_function, label_from=label_from, label_to=label_to)

    @text_instance
    def perturb(self, instance: TextInstance) -> Optional[Sequence[Tuple[TextInstance, Sequence[Tuple[KT, LT]]]]]:
        """Apply a perturbation function to a single `TextInstance`, getting a single result per instance.

        Args:
            perturbation_function (Callable): Perturbation function to apply, 
                including attribute label of original instance and the resulting instance.
                Should return None if no perturbation has been applied.

        Returns:
            Optional[Sequence[Tuple[TextInstance, Sequence[Tuple[KT, LT]]]]]: None if no perturbation has been applied. 
                Otherwise a sequence of perturbed TextInstances, and attribute labels for the original and perturbed 
                instances.
        """
        res = self.perturbation_function(instance)

        if res is None or isinstance(res, list) and all(r is None for r in res) or not res:
            return

        if isinstance(res, list):
            res = res[0]

        perturbed, original_labels, labels = res

        perturbed = as_list(perturbed)
        original_labels = as_list(original_labels)
        labels = as_list(labels)

        for perturbed_text, original_label, label in zip(perturbed, original_labels, labels):
            if perturbed_text is not None and perturbed_text != str(instance.data):
                identifier = format_identifier(instance, 0)
                yield (MemoryTextInstance(identifier, perturbed_text, None),
                       [(instance.identifier, frozenset({original_label})),
                        (identifier, frozenset({label}))])


class OneToManyPerturbation(Perturbation):
    def __init__(self,
                 perturbation_function: Callable[[TextInstance],
                                                 Optional[Tuple[Sequence[str], LT, Union[LT, Sequence[LT]]]]]):
        """Apply a perturbation function to a single `TextInstance`, getting a multiple results per instance.

        Args:
            perturbation_function (Callable): Perturbation function to apply, 
                including attribute label of original instance and the resulting instances.
                Should return None if no perturbation has been applied.
        """
        super().__init__(perturbation_function)

    @classmethod
    def from_function(cls,
                      function: Callable[[str], Optional[Union[str, Sequence[str]]]],
                      label_from: LT = 'original',
                      label_to: LT = 'perturbed',
                      n: int = 10,
                      perform_once: bool = False):
        """Construct a `OneToManyPerturbation` from a perturbation applied to a string.

        Args:
            function (Callable[[str], Optional[Union[str, Sequence[str]]]]): Function to apply 
                to each string. Return None if no change was applied.
            label_from (LT, optional): Attribute label of original instance. Defaults to 'original'.
            label_to (LT, optional): Attribute label of perturbed instance. Defaults to 'perturbed'.
            n (int, optional): Number of instances to generate. Defaults to 10.
            perform_once (bool, optional): If the n parameter is in class construction perform once. Defaults to False.
        """
        import inspect

        if 'n' in inspect.signature(function).parameters:
            return super().from_function(lambda x: function(x, n=n), label_from=label_from, label_to=label_to)
        elif perform_once:
            return super().from_function(function, label_from=label_from, label_to=label_to)

        def perform_n_times(instance):
            perturbed = list(filter(None, [function(instance) for _ in range(n)]))
            return None if len(perturbed) == 0 else perturbed

        return super().from_function(lambda x: perform_n_times(x), label_from=label_from, label_to=label_to)

    @classmethod
    def from_dictionary(cls,
                        dictionary: Dict[str, List[str]],
                        label_from: LT,
                        label_to: LT,
                        n: int = 10,
                        tokenizer: Callable = default_tokenizer,
                        detokenizer: Callable = default_detokenizer):
        """Construct a `OneToManyPerturbation` from a dictionary.

        Example:
            Replace the word 'good' (positive) with 'bad', 'mediocre', 'terrible' (negative) up to
            5 times in each instance. The default tokenizer/detokenizer assumes word-level tokens:

            >>> replacements = {'good': ['bad', 'mediocre', 'terrible']}
            >>> OneToManyPerturbation.from_dictionary(replacement,
            >>>                                       n=5,
            >>>                                       label_from='positive',
            >>>                                       label_to='negative')

        Args:
            dictionary (Dict[str, List[str]]): Lookup dictionary to map tokens (e.g. words, characters).
            label_from (LT): Attribute label of original instance (left-hand side of dictionary).
            label_to (LT): Attribute label of perturbed instance (right-hand side of dictionary).
            n (int, optional): Number of instances to generate. Defaults to 10.
            tokenizer (Callable, optional): Function to tokenize instance data (e.g. words, characters).
                Defaults to default_tokenizer.
            detokenizer (Callable, optional): Function to detokenize tokens into instance data.
                Defaults to default_detokenizer.
        """
        # TODO: add case-sensitivity
        @text_instance
        def perturbation_function(instance: TextInstance) -> Optional[Tuple[str, LT, LT]]:
            return one_to_many_dictionary_mapping(instance,
                                                  dictionary={k: as_list(v) for k, v in dictionary.items()},
                                                  label_from=label_from,
                                                  label_to=label_to,
                                                  n=n,
                                                  tokenizer=tokenizer,
                                                  detokenizer=detokenizer)

        return cls(perturbation_function)

    @classmethod
    def from_nlpaug(cls,
                    augmenter: Augmenter,
                    label_from: LT = 'original',
                    label_to: LT = 'perturbed',
                    n: int = 10,
                    **augment_kwargs):
        """Construct a `OneToManyPerturbation` from a `nlpaug`_ Augmenter.

        Example:
            Add `n=5` versions of keyboard typing mistakes to lowercase characters in a sentence using 
            `nlpaug.augmenter.char.KeyboardAug()`:

            >>> import nlpaug.augmenter.char as nac
            >>> augmenter = nac.KeyboardAug(include_upper_case=False,
            >>>                             include_special_char=False)
            >>> OneToManyPerturbation.from_nlpaug(augmenter, n=5, label_from='no_typos', label_to='typos')

        Args:
            augmenter (Augmenter): Class with `.augment()` function applying a perturbation to a string.
            label_from (LT, optional): Attribute label of original instance. Defaults to 'original'.
            label_to (LT, optional): Attribute label of perturbed instance. Defaults to 'perturbed'.
            n (int, optional): Number of instances to generate. Defaults to 10.
            **augment_kwargs: Optional arguments passed to `.augment()` function.

        .. _nlpaug:
            https://github.com/makcedward/nlpaug
        """
        @text_instance
        def perturbation_function(instance: TextInstance) -> Optional[str]:
            try:
                return augmenter.augment(str(instance.data), n=n, **augment_kwargs)
            except:  # noqa: E722
                return None

        return cls.from_function(perturbation_function, perform_once=True, label_from=label_from, label_to=label_to)

    @text_instance
    def perturb(self, instance: TextInstance) -> Optional[Sequence[Tuple[TextInstance, Sequence[Tuple[KT, LT]]]]]:
        """Apply a perturbation function to a single `TextInstance`, getting a multiple results per instance.

        Args:
            perturbation_function (Callable): Perturbation function to apply, 
                including attribute label of original instance and the resulting instances.
                Should return None if no perturbation has been applied.

        Returns:
            Optional[Sequence[Tuple[TextInstance, Sequence[Tuple[KT, LT]]]]]: None if no perturbation has been applied. 
                Otherwise a sequence of perturbed TextInstances, and attribute labels for the original and perturbed 
                instances.
        """
        res = self.perturbation_function(instance)

        if res is None or isinstance(res, list) and all(r is None for r in res):
            return

        perturbed, original_label, labels = res

        original_label = (instance.identifier, frozenset({original_label}))

        labels = as_list(labels)
        if len(labels) == 1:
            labels = labels * len(perturbed)

        filtered_keys = [i for i, p in enumerate(perturbed) if p != str(instance.data)]
        return [([MemoryTextInstance(format_identifier(instance, key), perturbed[key], None) for key in filtered_keys],
                 [original_label] + 
                 [(format_identifier(instance, key), frozenset({labels[key]})) for key in filtered_keys])]
