from runrex.algo.result import Result
from runrex.text import Document


def kw(*args, **kwargs):
    for val in args:
        if val is None:
            continue
        elif isinstance(val, dict):
            kwargs.update(val)
        else:
            raise ValueError(f'Unrecognized kwargs: {val}')
    return kwargs


def algo_to_result(func, document: Document, expected=None):
    for status, text, start, end in func(document):
        yield Result(status, status.value, expected=expected,
                     text=text, start=start, end=end)
