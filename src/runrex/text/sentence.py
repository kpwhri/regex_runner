from typing import Tuple

from runrex.algo import MatchCask, Pattern, Negation


class Sentence:

    def __init__(self, text, mc: MatchCask = None, start=0, end=None):
        self.text = text
        self.matches = mc or MatchCask()
        self.start = start
        self.end = end if end else len(self.text)
        self.strip()  # remove extra start/ending characters
        self._last_search_found_pattern = []

    def reset_found_pattern(self):
        self._last_search_found_pattern = []

    @property
    def last_found(self):
        return self._last_search_found_pattern[-1]

    @property
    def any_found(self):
        return any(self._last_search_found_pattern)

    def strip(self):
        """
        Remove begin and end characters, but keep track of new offsets
        :return:
        """
        ltext = self.text.lstrip()
        start_incr = len(self.text) - len(ltext)
        self.start += start_incr
        rtext = ltext.rstrip()
        self.end -= len(self.text) - len(rtext) - start_incr
        self.text = rtext

    def _update_last_search(self, val: bool):
        self._last_search_found_pattern.append(val)

    def has_pattern(self, pat: Pattern, ignore_negation=False):
        m = pat.matches(self.text, ignore_negation=ignore_negation, offset=self.start)
        self._update_last_search(bool(m))
        if m:
            self.matches.add(m)
        return m

    def has_patterns(self, *pats, has_all=False, ignore_negation=False):
        for pat in pats:
            if has_all and not self.has_pattern(pat, ignore_negation=ignore_negation):
                self._update_last_search(False)
                return False
            elif not has_all and self.has_pattern(pat, ignore_negation=ignore_negation):
                self._update_last_search(True)
                return True
        self._update_last_search(has_all)
        return has_all

    def get_pattern(self, pat: Pattern, *, index=0, get_indices=False, return_negation=False,
                    return_negation_keyword=False):
        """

        :param return_negation: if True return Negation instance rather than ignoring negation
        :param pat:
        :param index:
        :param get_indices: to maintain backward compatibility
        :return:
        """
        # incorporate offset information
        m = pat.matches(self.text, offset=self.start, return_negation=return_negation)
        self._update_last_search(bool(m))
        if m:
            self.matches.add(m)
            if get_indices:  # offset has already been added in pat.matches
                if return_negation_keyword:
                    return m.group(index), m.start(index), m.end(index), m.neg_group()
                return m.group(index), m.start(index), m.end(index)
            elif return_negation_keyword:
                return m.group(index), m.neg_group()
            else:
                return m.group(index)

    def get_patterns(self, *pats: Pattern, index=0, return_negation=False) -> Tuple[str, int, int]:
        """

        :param return_negation: if True return Negation instance rather than ignoring negation
        :param pats:
        :param index: group index (if using particular regex match group)
        :return:
        """
        found = False
        for pat in pats:
            for m in pat.finditer(self.text, offset=self.start, return_negation=return_negation):
                found = True
                self.matches.add(m)
                if return_negation:
                    yield m.group(index), m.start(index), m.end(index), isinstance(m, Negation)
                else:
                    yield m.group(index), m.start(index), m.end(index)
        self._update_last_search(found)
