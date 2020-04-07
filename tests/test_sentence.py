import pytest

from runrex.text import Sentence


@pytest.mark.parametrize(('sentence', 'exp_start_idx', 'exp_end_idx'), [
    (' What is this? ', 1, 14),
    ('\n What is this?\t\t \n', 2, 15),
])
def test_sentence_strip(sentence, exp_start_idx, exp_end_idx):
    s = Sentence(sentence)
    assert s.start == exp_start_idx
    assert s.end == exp_end_idx
    assert s.text == sentence.strip()
