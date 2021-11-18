import pytest

from runrex.algo import Pattern
from runrex.algo.utils import is_close_to


@pytest.mark.parametrize('text, start, end, window, exp', [
    ('pain for 1 week', 9, 15, 20, True),
    ('1 week of acute pain', 0, 6, 20, True),
    ('pain blah blah blah blah blah 1 week', 30, 36, 20, False),
    ('1 week of joy and happiness blah blah blah blah blah pain', 0, 6, 20, False),
])
def test_is_close_to(text, start, end, window, exp):
    assert is_close_to(Pattern(r'\bpain\b'), text, start, end, window) is exp
