import pytest

from runrex.algo import Pattern, Negation
from runrex.text import Sentence
from runrex.text import Sentences
from runrex.text.ssplit import keep_offsets_ssplit


def test_pattern_return_negate():
    m = Pattern('test', negates=[r'\bnot?\b']).matches('do not test this', return_negation=True)
    assert isinstance(m, Negation)
    assert m.neg_group() == 'not'
    assert m.match == 'test'


def test_pattern_no_return_negate():
    m = Pattern('test', negates=[r'\bnot?\b']).matches('do not test this')
    assert m is False


def test_sentence_return_negate():
    p = Pattern('test', negates=[r'\bnot?\b'])
    text = Sentence('do not test this').get_pattern(p, return_negation=True)
    assert text == 'test'


def test_sentence_return_negation_keyword():
    p = Pattern('test', negates=[r'\bnot?\b'])
    text, neg = Sentence('do not test this').get_pattern(
        p, return_negation=True, return_negation_keyword=True
    )
    assert text == 'test'
    assert neg == 'not'


def test_pattern_matches_sentence():
    pat = Pattern('(this|that)')
    sentence = Sentence('\t I want this, or that.\n')
    match = sentence.get_pattern(pat, get_indices=True)
    assert match is not None
    s, start, end = match
    assert s == 'this'
    assert start == 9
    assert end == 13


def test_pattern_matches_sentences_keep_offsets():
    sentences = Sentences(' I want this, or that.\n These and those.',
                          ssplit=keep_offsets_ssplit)
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


def test_pattern_matches_sentences():
    sentences = Sentences(' I want this, or that.\n These and those.')
    # first sentence
    match = sentences.get_pattern(Pattern('(this|that)'), get_indices=True)
    assert match is not None
    s, start, end = match
    assert s == 'this'
    assert start == 7
    assert end == 11
    # second sentence
    match = sentences.get_pattern(Pattern('(these|those)'), get_indices=True)
    assert match is not None
    s, start, end = match
    assert s == 'These'
    assert start == 23
    assert end == 28


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


@pytest.mark.parametrize(('pat', 'text', 'n_matches', 'n_negation'), [
    (Pattern('(this|that)', negates=['not']), ' I want this, or that.\n\n But not that', 3, 1),
])
def test_pattern_finditer_sentences_return_negation(pat: Pattern, text: str, n_matches: int, n_negation: int):
    sentences = Sentences(text)
    matches = list(sentences.get_patterns(pat, return_negation=True))
    assert len(matches) == n_matches
    assert len([is_neg for _, _, _, is_neg in matches if is_neg]) == n_negation
