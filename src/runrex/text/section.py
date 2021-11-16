from typing import Iterable

from runrex.algo import MatchCask, Pattern
from runrex.text.sentence import Sentence


class Section:

    def __init__(self, sentences: Iterable[Sentence], mc: MatchCask = None, add_matches=False):
        """

        :param sentences:
        :param mc:
        :param add_matches: use if you are copying data rather than
            passing around the same match object (default)
        """
        self.sentences = list(sentences)
        self.text = '\n'.join(sent.text for sent in sentences)
        self.matches = mc or MatchCask()
        if add_matches:
            for sent in self.sentences:
                self.matches.add_all(sent.matches.matches)

    @property
    def match_start(self):
        return self.matches.start

    @property
    def match_end(self):
        return self.matches.end

    @property
    def match_text(self):
        return self.matches.last_text

    @property
    def start(self):
        return min(sent.start for sent in self.sentences)

    @property
    def end(self):
        return max(sent.end for sent in self.sentences)

    def has_pattern(self, pat: Pattern, ignore_negation=False):
        for sentence in self.sentences:
            m = sentence.has_pattern(pat, ignore_negation=ignore_negation)
            if m:
                self.matches.add(m)
                return m

    def get_pattern(self, pat: Pattern, index=0, get_indices=False):
        for sentence in self.sentences:
            yield from sentence.get_pattern(pat, index=index, get_indices=get_indices)

    def get_patterns(self, *pats: Pattern, index=0, return_negation=False):
        for sentence in self.sentences:
            yield from sentence.get_patterns(*pats, index=index, return_negation=return_negation)

    def has_patterns(self, *pats, has_all=False, ignore_negation=False, get_count=False):
        """

        :param pats:
        :param has_all:
        :param ignore_negation:
        :param get_count: number of patterns to match
        :return:
        """
        if get_count:
            has_all = False  # ensure this is properly set
        cnt = 0
        for pat in pats:
            match = self.has_pattern(pat, ignore_negation=ignore_negation)
            if get_count:
                if match:
                    cnt += 1
            elif has_all and not match:
                return False
            elif not has_all and match:
                return True
        if get_count:
            return cnt
        return has_all

    def __bool__(self):
        return len(self.sentences) > 0 and bool(self.text.strip())

    def __add__(self, other):
        return Section(self.sentences + other.sentences, self.matches.copy().add_all(other.matches.matches))

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text
