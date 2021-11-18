def is_close_to(pattern, text, start, end, window):
    """
    Ensure that a particular match is within an `window`-character window of another pattern
    :param pattern:
    :param text:
    :param start:
    :param end:
    :param window:
    :return:
    """
    return bool(pattern.matches(text[max(0, start - window): end + window]))
