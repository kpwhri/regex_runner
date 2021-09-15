import re
from typing import Tuple
from loguru import logger

try:
    from syntok import segmenter as syntok_segmenter
except ImportError:
    logger.warning('syntok not installed: defaulting to regex tokenizer')
    syntok_segmenter = False


def regex_ssplit(text: str, *, delim='\n') -> Tuple[str, int, int]:
    start = 0
    for m in re.finditer(delim, text):
        yield ' '.join(text[start:m.end()].split()), start, m.end()
        start = m.end()
    yield ' '.join(text[start:].split()), start, len(text)


def syntok_ssplit(text: str, ignore_newlines=True):
    if ignore_newlines:
        # remove only single newlines, assume multiples are paragraph breaks
        text = ' '.join(re.split(r'(?<!\n)\n(?!\n)', text))
    for paragraph in syntok_segmenter.analyze(text):
        for sentence in paragraph:
            yield ' '.join(tok.value for tok in sentence)


if syntok_segmenter:
    default_ssplit = syntok_ssplit
else:
    default_ssplit = regex_ssplit
