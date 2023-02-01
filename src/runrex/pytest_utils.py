from runrex.text import Document


def pytest_algo_function(func, text, *args, **kwargs):
    """
    Simplify testing the `has_algo` or `is_algo` function.

    E.g.,
    * exp (expected value): None (if expecting no results) or Status (enum)
    * text (text to test):
    assert exp in test_algo_function(has_social_isolation, text)
    """
    doc = Document(None, text=text)
    results = [status for status, *_ in func(doc, *args, **kwargs)]
    if len(results) == 0:
        return [None]
    return results
