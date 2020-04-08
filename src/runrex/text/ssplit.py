import re
from typing import Tuple


def default_ssplit(text: str) -> Tuple[str, int, int]:
    target = '\n'
    start = 0
    for m in re.finditer(target, text):
        yield text[start:m.end()], start, m.end()
        start = m.end()
    yield text[start:], start, len(text)
