import re

from runrex.algo import Match


class Negation:
    def __init__(self, term, match):
        self._term = term  # negation term
        self._match: Match = match

    @property
    def matchobj(self):
        return self._match

    @property
    def negationobj(self):
        return self._term

    def neg_group(self, *index):
        return self._term.group(*index)

    def neg_start(self, group=0):
        return self._term.start(group)

    def neg_end(self, group=0):
        return self._term.end(group)

    def start(self, group=0):
        return self._match.start(group)

    def end(self, group=0):
        return self._match.end(group)

    def group(self, *index):
        return self._match.group(*index)

    @property
    def match(self):
        if isinstance(self._match, re.Match):
            return self._match.group()
        return str(self._match)

    @property
    def term(self):
        if isinstance(self._term, re.Pattern):
            return self._term.pattern
        return str(self._term)
