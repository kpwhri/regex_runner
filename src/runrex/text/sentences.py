from typing import Iterator

from runrex.algo import Pattern
from runrex.text.sentence import Sentence
from runrex.text.ssplit import default_ssplit


class Sentences:

    def __init__(self, text, matches=None, ssplit=default_ssplit):
        self.sentences = [Sentence(s, matches, sidx, eidx) for s, sidx, eidx in ssplit(text) if s.strip()]

    def has_pattern(self, pat, ignore_negation=False):
        for sentence in self.sentences:
            if sentence.has_pattern(pat, ignore_negation=ignore_negation):
                return sentence.text
        return False

    def has_patterns(self, *pats, has_all=False, ignore_negation=False):
        for pat in pats:
            if has_all and not self.has_pattern(pat, ignore_negation=ignore_negation):
                return False
            elif not has_all and self.has_pattern(pat, ignore_negation=ignore_negation):
                return True
        return has_all

    def get_pattern(self, pat, index=0, get_indices=False):
        """

        :param pat:
        :param index:
        :param get_indices: if True, return (group, start, end)
        :return:
        """
        for sentence in self.sentences:
            if m := sentence.get_pattern(pat, index=index, get_indices=get_indices):
                return m  # tuple if requested indices

    def get_patterns(self, *pats: Pattern, index=0, return_negation=False):
        for sentence in self.sentences:
            yield from sentence.get_patterns(*pats, index=index, return_negation=return_negation)

    def __len__(self):
        return len(self.sentences)

    def __iter__(self) -> Iterator[Sentence]:
        return iter(self.sentences)

    def __getitem__(self, item):
        return self.sentences[item]
