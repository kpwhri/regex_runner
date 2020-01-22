import pytest

from runrex.algo.pattern import Pattern, Sentence, Sentences


def test_pattern_matches_sentence():
    pat = Pattern('(this|that)')
    sentence = Sentence(' I want this, or that.\n')
    match = sentence.get_pattern(pat)
    assert match is not None


@pytest.mark.parametrize(('pat', 'sentence', 'n_matches'), [
    (Pattern('(this|that)'), ' I want this, or that.\n', 2),
])
def test_pattern_finditer_sentence(pat: Pattern, sentence: str, n_matches):
    sentence = Sentence(sentence)
    matches = list(sentence.get_patterns(pat))
    assert len(matches) == n_matches


@pytest.mark.parametrize(('pat', 'text', 'n_matches'), [
    (Pattern('(this|that)'), ' I want this, or that.\n\n But not that', 3),
])
def test_pattern_finditer_sentences(pat: Pattern, text: str, n_matches):
    sentences = Sentences(text)
    matches = list(sentences.get_patterns(pat))
    assert len(matches) == n_matches
