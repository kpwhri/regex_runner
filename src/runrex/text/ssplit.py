import re
from typing import Tuple
from loguru import logger

try:
    from syntok import segmenter as syntok_segmenter
except ImportError:
    logger.warning('syntok not installed')
    syntok_segmenter = False


def default_ssplit(text: str, *, delim='\n') -> Tuple[str, int, int]:
    start = 0
    for m in re.finditer(delim, text):
        yield text[start:m.end()], start, m.end()
        start = m.end()
    yield text[start:], start, len(text)


def ssplit(text: str, ignore_newlines=True):
    if ignore_newlines or not syntok_segmenter:
        # remove only single newlines, assume multiples are paragraph breaks
        text = ' '.join(re.split(r'(?<!\n)\n(?!\n)', text))
    for paragraph in syntok_segmenter.analyze(text):
        for sentence in paragraph:
            yield ' '.join(tok.value for tok in sentence)
