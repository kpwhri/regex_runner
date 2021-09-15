import pytest

from runrex.text import Sentences
from runrex.text.ssplit import keep_offsets_ssplit, syntok_ssplit


@pytest.mark.parametrize(('text', 'n_sent', 'exp_indices'), [
    ('A sentence.\n Another sentence\nis here.',
     3, [(0, 12), (12, 30), (30, 38)]),
])
def test_keep_offsets_ssplit(text, n_sent, exp_indices):
    for i, ((sent, start, end), (exp_start, exp_end)) in enumerate(zip(
            keep_offsets_ssplit(text), exp_indices
    )):
        assert start == exp_start
        assert end == exp_end
        assert i < n_sent


@pytest.mark.parametrize(('text', 'n_sent', 'exp_indices'), [
    ('A sentence.\n Another sentence\nis here.',
     3, [(0, 11), (13, 29), (30, 38)]),
    ('This or that.\n\n \nThese and those.\n',
     2, [(0, 13), (17, 33)]),
])
def test_keep_offsets_sentence_segmentation(text, n_sent, exp_indices):
    sents = Sentences(text, None, ssplit=keep_offsets_ssplit)
    assert len(sents) == n_sent
    for sent, (exp_start, exp_end) in zip(sents, exp_indices):
        assert sent.start == exp_start
        assert sent.end == exp_end


@pytest.mark.parametrize(('text', 'n_sent', 'exp_indices'), [
    ('A sentence.\n Another sentence\nis here.',
     2, [(0, 12), (12, 38)]),
    ('This or that.\n\n \nThese and those.\n',
     2, [(0, 14), (14, 31)]),
])
def test_syntok_sentence_segmentation(text, n_sent, exp_indices):
    sents = Sentences(text, None, ssplit=syntok_ssplit)
    assert len(sents) == n_sent
    for sent, (exp_start, exp_end) in zip(sents, exp_indices):
        assert sent.start == exp_start
        assert sent.end == exp_end
