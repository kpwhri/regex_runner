import pytest

from runrex.algo.pattern import Pattern
from runrex.text import Sentence
from runrex.text import Sentences


def test_pattern_matches_sentence():
    pat = Pattern('(this|that)')
    sentence = Sentence('\t I want this, or that.\n')
    match = sentence.get_pattern(pat, get_indices=True)
    assert match is not None
    s, start, end = match
    assert s == 'this'
    assert start == 9
    assert end == 13


def test_pattern_matches_sentences():
    sentences = Sentences(' I want this, or that.\n These and those.')
    # first sentence
    match = sentences.get_pattern(Pattern('(this|that)'), get_indices=True)
    assert match is not None
    s, start, end = match
    assert s == 'this'
    assert start == 8
    assert end == 12
    # second sentence
    match = sentences.get_pattern(Pattern('(these|those)'), get_indices=True)
    assert match is not None
    s, start, end = match
    assert s == 'These'
    assert start == 24
    assert end == 29


@pytest.mark.parametrize(('pat', 'sentence', 'n_matches'), [
    (Pattern('(this|that)'), ' I want this, or that.\n', 2),
])
def test_pattern_finditer_sentence(pat: Pattern, sentence: str, n_matches):
    sentence = Sentence(sentence)
    matches = list(x[0] for x in sentence.get_patterns(pat))  # text only
    assert len(matches) == n_matches


@pytest.mark.parametrize(('pat', 'text', 'n_matches'), [
    (Pattern('(this|that)'), ' I want this, or that.\n\n But not that', 3),
])
def test_pattern_finditer_sentences(pat: Pattern, text: str, n_matches):
    sentences = Sentences(text)
    matches = list(sentences.get_patterns(pat))
    assert len(matches) == n_matches
