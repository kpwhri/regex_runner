import re
from typing import Tuple
from loguru import logger

try:
    from syntok import segmenter as syntok_segmenter
except ImportError:
    logger.warning('syntok not installed: defaulting to regex tokenizer')
    syntok_segmenter = False


def keep_offsets_ssplit(text: str, delim='\n') -> Tuple[str, int, int]:
    start = 0
    for m in re.finditer(delim, text):
        yield text[start:m.end()], start, m.end()
        start = m.end()
    yield text[start:], start, len(text)


def regex_ssplit(text: str, *, delim='\n') -> Tuple[str, int, int]:
    start = 0
    for m in re.finditer(delim, text):
        sentence = ' '.join(text[start:m.end()].split())
        end = start + len(sentence)
        yield sentence, start, end
        start = end
    sentence = ' '.join(text[start:].split())
    yield sentence, start, start + len(sentence)


def syntok_ssplit(text: str, ignore_newlines=True) -> Tuple[str, int, int]:
    if ignore_newlines:
        # remove only single newlines, assume multiples are paragraph breaks
        text = ' '.join(re.split(r'(?<!\n)\n(?!\n)', text))
    start = 0
    for paragraph in syntok_segmenter.analyze(text):
        for sentence in paragraph:
            sentence = ' '.join(tok.value for tok in sentence)
            end = start + len(sentence)
            yield sentence, start, end
            start = end


if syntok_segmenter:
    default_ssplit = syntok_ssplit
else:
    default_ssplit = regex_ssplit
