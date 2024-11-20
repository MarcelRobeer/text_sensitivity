import pytest

from text_sensitivity.data.wordlist import WordList

WORDS = ['word1', 'word2', 'word3', 'word4', 'abc', 'def', 'xyz']
WORDS_DICT = {w: 'good' if 'word' in w else 'bad' for w in WORDS}


@pytest.mark.parametrize('n', range(1, 6))
def test_wordlist_list_n(n):
    assert len(WordList.from_list(WORDS).generate_list(n)) == n
