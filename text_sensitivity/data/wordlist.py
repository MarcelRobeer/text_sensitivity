"""Select data from a list of words, optionally with a probability to choose each element."""

from functools import lru_cache
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from genbase import CaseMixin, Readable, SeedMixin

Label = Union[str, int]


class WordList(Readable, SeedMixin, CaseMixin):
    def __init__(self,
                 wordlist: pd.DataFrame,
                 main_column: Optional[Label] = None,
                 attribute_column: Optional[Label] = None,
                 seed: int = 0):
        """Capture data in wordlist.

        Args:
            wordlist (pd.DataFrame): Dataframe containing a column with data (e.g. city names).
            main_column (Optional[Label], optional): Column containing data. Defaults to None.
            attribute_column (Optional[Label], optional): Column containing attributes. If None defaults to the main 
                column.
            seed (int, optional): Seed for reproducibility. Defaults to 0.
        """
        self.wordlist = wordlist
        self.__wordlist = wordlist.copy(deep=True)
        self.main_column = main_column
        self.attribute_column = attribute_column
        self._seed = self._original_seed = seed
        self._lowercase = self._sentencecase = self._titlecase = self._uppercase = False

    @classmethod
    def from_list(cls, wordlist: List[str], name: Label = 'words', seed: int = 0):
        """Create a `WordList` from a list of strings.

        Example:
            Create list of city names and pick one random element:

            >>> wl = WordList.from_list(['Amsterdam', 'Rotterdam', 'Utrecht'], name='city')
            >>> wl.generate_list(n=1)

        Args:
            wordlist (List[str]): List of strings.
            name (Label, optional): Name of attribute. Defaults to 'words'.
            seed (int, optional): Seed for reproducibility. Defaults to 0.

        Returns:
            WordList: WordList class.
        """
        return cls(pd.DataFrame(wordlist, columns=[name]), seed=seed)

    @classmethod
    def from_dictionary(cls,
                        wordlist: Dict,
                        key_name: Label = 'key',
                        value_name: Label = 'value',
                        value_as_main: bool = False,
                        seed: int = 0):
        """Create a `WordList` from a dictionary.

        Example:
            Create list of pronouns with genders:

            >>> wl = WordList.from_dictionary({'he': 'male', 'she': 'female', 'they': 'neuter'},
            ...                               key_name='pronoun',
            ...                               value_name='gender')

        Args:
            wordlist (Dict): Dictionary of elements and corresponding attribute.
            key_name (Label, optional): Name of keys. Defaults to 'key'.
            value_name (Label, optional): Name of values. Defaults to 'value'.
            value_as_main (bool, optional): Whether data is in the key column (False) or value column (True). 
                Defaults to False.
            seed (int, optional): Seed for reproducibility. Defaults to 0.

        Returns:
            WordList: WordList class.
        """
        main_column = value_name if value_as_main else key_name
        attribute_column = key_name if value_as_main else value_name
        return cls(pd.DataFrame(list(wordlist.items()), columns=[key_name, value_name]), main_column=main_column,
                   attribute_column=attribute_column, seed=seed)

    @classmethod
    def from_dict(cls, *args, **kwargs):
        """Alias for `WordList.from_dictionary()`."""
        return cls.from_dictionary(*args, **kwargs)

    @classmethod
    def from_csv(cls,
                 filename: str,
                 main_column: Optional[Label] = None,
                 attribute_column: Optional[Label] = None,
                 seed: int = 0,
                 *args,
                 **kwargs):
        """Create a `WordList` from a CSV file.

        Args:
            filename (str): Filename.
            main_column (Optional[Label], optional): Data column. Defaults to None.
            attribute_column (Optional[Label], optional): Attribute column. Defaults to None.
            seed (int, optional): Seed for reproducibility. Defaults to 0.
            **kwargs: Optional arguments passed to `pandas.read_csv()`.

        Returns:
            WordList: WordList class.
        """
        return cls(pd.read_csv(filename, *args, **kwargs), main_column=main_column,
                   attribute_column=attribute_column, seed=seed)

    @classmethod
    def from_json(cls,
                  filename: str,
                  main_column: Optional[Label] = None,
                  attribute_column: Optional[Label] = None,
                  seed: int = 0,
                  *args,
                  **kwargs):
        """Create a `WordList` from a JSON file.

        Args:
            filename (str): Filename.
            main_column (Optional[Label], optional): Data column. Defaults to None.
            attribute_column (Optional[Label], optional): Attribute column. Defaults to None.
            seed (int, optional): Seed for reproducibility. Defaults to 0.
            **kwargs: Optional arguments passed to `pandas.read_json()`.

        Returns:
            WordList: WordList class.
        """
        return cls(pd.read_json(filename, *args, **kwargs), main_column=main_column,
                   attribute_column=attribute_column, seed=seed)

    @classmethod
    def from_excel(cls,
                   filename: str,
                   main_column: Optional[Label] = None,
                   attribute_column: Optional[Label] = None,
                   seed: int = 0,
                   *args,
                   **kwargs):
        """Create a `WordList` from an Excel (`.xls` or `.xlsx`) file.

        Args:
            filename (str): Filename.
            main_column (Optional[Label], optional): Data column. Defaults to None.
            attribute_column (Optional[Label], optional): Attribute column. Defaults to None.
            seed (int, optional): Seed for reproducibility. Defaults to 0.
            **kwargs: Optional arguments passed to `pandas.read_excel()`.

        Returns:
            WordList: WordList class.
        """
        return cls(pd.read_excel(filename, *args, **kwargs), main_column=main_column,
                   attribute_column=attribute_column, seed=seed)

    @classmethod
    def from_pickle(cls,
                    filename: str,
                    main_column: Optional[Label] = None,
                    attribute_column: Optional[Label] = None,
                    seed: int = 0,
                    *args,
                    **kwargs):
        """Create a `WordList` from a Pickled (`.pkl`) file.

        Args:
            filename (str): Filename.
            main_column (Optional[Label], optional): Data column. Defaults to None.
            attribute_column (Optional[Label], optional): Attribute column. Defaults to None.
            seed (int, optional): Seed for reproducibility. Defaults to 0.
            **kwargs: Optional arguments passed to `pandas.read_pickle()`.

        Returns:
            WordList: WordList class.
        """
        return cls(pd.read_pickle(filename, *args, **kwargs), main_column=main_column,
                                  attribute_column=attribute_column, seed=seed)

    @classmethod
    def from_file(cls,
                  filename: str,
                  main_column: Optional[Label] = None,
                  attribute_column: Optional[Label] = None,
                  seed: int = 0,
                  *args,
                  **kwargs):
        """Create a `WordList` from a file.

        The file type is inferred based on the file extension.

        Args:
            filename (str): Filename.
            main_column (Optional[Label], optional): Data column. Defaults to None.
            attribute_column (Optional[Label], optional): Attribute column. Defaults to None.
            seed (int, optional): Seed for reproducibility. Defaults to 0.
            **kwargs: Optional arguments passed to `pandas` reader.

        Returns:
            WordList: WordList class.
        """
        import os
        extension = str.lower(os.path.splitext(filename)[1])

        extensions_dict = {'csv': cls.from_csv,
                           'json': cls.from_json,
                           'pkl': cls.from_pickle,
                           'xls': cls.from_excel,
                           'xlsx': cls.from_excel}

        if extension in extensions_dict:
            return extensions_dict[extension](filename=filename, main_column=main_column,
                                              attribute_column=attribute_column, seed=seed, *args, **kwargs)
        else:
            return cls(pd.read_table(filename, *args, **kwargs), main_column=main_column,
                       attribute_column=attribute_column, seed=seed)

    @lru_cache(1)
    def get(self,
            sort_by: Optional[Label] = None,
            attributes: bool = False,
            **sort_kwargs) -> List[str]:
        """Get all elements in wordlist.

        Args:
            sort_by (Optional[Label], optional): Label to sort on (e.g. frequency). Defaults to None.
            attributes (bool, optional): Include attributes or not. Defaults to False.

        Returns:
            List[str]: Wordlist elements.
        """
        wordlist = self.wordlist.sort_values(by=sort_by, **sort_kwargs) if sort_by is not None else self.wordlist
        col = wordlist.iloc[:, 0] if self.main_column is None or self.main_column not in self.wordlist.columns \
            else wordlist.loc[:, self.main_column]
        res = [self.apply_case(c) for c in list(col)]

        if not attributes:
            return res

        attr = {} if self.attribute_column is None or self.attribute_column not in self.wordlist.columns \
            else {self.attribute_column: list(wordlist.loc[:, self.attribute_column])}
        return res, attr

    def generate_list(self,
                      n: Optional[int] = None,
                      attributes: bool = False,
                      likelihood_column: Optional[Label] = None) -> List[str]:
        """Generate a random list of `n` elements.

        Args:
            n (Optional[int], optional): Number of elements to generate. Defaults to None.
            attributes (bool, optional): Include attributes or not. Defaults to False.
            likelihood_column (Optional[Label], optional): Attribute to determine likelihood on. Defaults to None.

        Returns:
            List[str]: Wordlist elements (up to `n`).
        """
        if n is None or isinstance(n, int) and n >= len(self.wordlist.index):
            return self.get(attributes=attributes)
        if likelihood_column is not None:
            likelihood_column = self.wordlist[likelihood_column].values / self.wordlist[likelihood_column].sum()

        if attributes:
            items, attr = self.get(attributes=True)
        else:
            items = self.get()

        np.random.seed(self._seed)
        ids = np.random.choice(len(items), size=n, replace=False, p=likelihood_column)
        selected_items = [items[i] for i in ids]

        if not attributes:
            return selected_items
        return selected_items, {k: [v[i] for i in ids] for k, v in attr.items()}

    def filter(self,
               column: Label,
               values: Union[Label, List[Label]]) -> 'WordList':
        """Filter the wordlist column if it is in values.

        Args:
            column (Label): Column to filter.
            values (Union[Label, List[Label]]): Values to filter.

        Returns:
            WordList: Self.
        """
        if not isinstance(values, list):
            values = [values]
        self.wordlist = self.wordlist[self.wordlist[column].isin(values)]
        return self

    def reset(self):
        """Reset wordlist."""
        self.wordlist = self.__wordlist.copy(deep=True)
        return self

    def __len__(self):
        """Length of wordlist."""
        return len(self.get())

    def __getitem__(self, item):
        """Get item in wordlist."""
        return self.get()[item]


class WordListGetterMixin:
    def get(self, *args, **kwargs):
        """Get item in wordlist."""
        return self.wordlist.get(*args, **kwargs)

    def generate_list(self, *args, **kwargs):
        """Wrapper of `WordList.generate_list()`."""
        return self.wordlist.generate_list(*args, **kwargs)

    def filter(self, *args, **kwargs):
        """Wrapper of `WordList.filter()`."""
        return self.wordlist.filter(*args, **kwargs)

    def reset(self):
        """Wrapper of `WordList.reset()`."""
        return self.wordlist.reset()

    def __len__(self):
        """Wordlist length."""
        return len(self.wordlist)
