import re
from typing import Iterable

from runrex.algo.direction import DirectionFlag
from runrex.algo.match import Match
from runrex.algo.negation import Negation


class Pattern:

    def __init__(self, pattern: str, *,
                 negates: Iterable[str] = None,
                 negates_pre: Iterable[str] = None,
                 negates_post: Iterable[str] = None,
                 requires: Iterable[str] = None,
                 requires_pre: Iterable[str] = None,
                 requires_post: Iterable[str] = None,
                 requires_all: Iterable[str] = None,
                 replace_whitespace=r'\W?',
                 capture_length=None, retain_groups=None,
                 flags=re.IGNORECASE):
        """

        :param pattern: regular expressions (uncompiled string)
        :param negates: regular expressions (uncompiled string)
        :param replace_whitespace: replace whitespace with this value; if using
            a custom tokenizer that leaves multiple spaces, this should be set to, e.g.,
            \\W*. This allow more readable regexes
        :param capture_length: for 'or:d' patterns, this is the number
            of actual capture groups (?:(this)|(that)|(thes))
            has capture_length = 1
            None: i.e., capture_length == max
        :param flags:
        """
        self.match_count = 0
        if replace_whitespace:
            pattern = replace_whitespace.join(pattern.split(' '))
        if retain_groups:
            for m in re.finditer(r'\?P<(\w+)>', pattern):
                term = m.group(1)
                if term in retain_groups:
                    continue
                pattern = re.sub(rf'\?P<{term}>', r'\?:', pattern)
        self.pattern = re.compile(pattern, flags)
        self.negates = list(self._compile_patterns(negates, negates_pre, negates_post, replace_whitespace, flags))
        self.requires = list(self._compile_patterns(requires, requires_pre, requires_post, replace_whitespace, flags))
        self.requires_all = list(self._compile_pattern(requires_all, replace_whitespace, flags))

        self.capture_length = capture_length
        self.text = self.pattern.pattern

    def __str__(self):
        return self.text

    def _compile_patterns(self, both, pre, post, replace_whitespace, flags):
        for group, flag in [(both, DirectionFlag.BOTH), (pre, DirectionFlag.PRE),
                            (post, DirectionFlag.POST)]:
            yield from self._compile_pattern(group, replace_whitespace, flags, flag)

    def _compile_pattern(self, group, replace_whitespace, flags, flag=None):
        for rx in group or []:
            if replace_whitespace:
                rx = replace_whitespace.join(rx.split(' '))
            if flag:
                yield re.compile(rx, flags), flag
            else:
                yield re.compile(rx, flags)

    def _get_text_for_direction(self, text, direction, match_start, match_end):
        if direction == DirectionFlag.BOTH:
            return text
        elif direction == DirectionFlag.PRE:
            return text[:match_start]
        elif direction == DirectionFlag.POST:
            return text[match_end:]

    def _confirm_match(self, text, match_start, match_end, return_negation=False,
                       ignore_negation=False,
                       ignore_requires=False, ignore_requires_all=False):
        if not ignore_negation:
            for negate, direction in self.negates:
                if neg_match := negate.search(self._get_text_for_direction(text, direction, match_start, match_end)):
                    return neg_match if return_negation else False
        if not ignore_requires and self.requires:
            found = False
            for require, direction in self.requires:
                if require.search(self._get_text_for_direction(text, direction, match_start, match_end)):
                    found = True
                    break
            if not found:
                return False
        if not ignore_requires_all:
            for require in self.requires_all:
                if not require.search(text):
                    return False
        return True

    def finditer(self, text, *, offset=0, return_negation=False, **kwargs):
        """Look for all matches

        TODO: allow configuring window, etc.

        :param offset:
        :param text:
        :param kwargs:
        :return:
        """
        for m in self.pattern.finditer(text):
            cm = self._confirm_match(text, m.start() + offset, m.end() + offset,
                                     return_negation=return_negation, **kwargs)
            if not isinstance(cm, bool):
                yield Negation(cm, m, offset=offset)
            elif cm:
                self.match_count += 1
                yield Match(m, groups=self._compress_groups(m), offset=offset)

    def matches(self, text, *, offset=0, return_negation=False, **kwargs):
        """Look for the first match -- this evaluation is at the sentence level.

        :param return_negation:
        :param offset:
        :param text:
        :param kwargs:
        :return:
        """
        m = self.pattern.search(text)
        if m:
            cm = self._confirm_match(text, m.start(), m.end(), return_negation=return_negation, **kwargs)
            if cm is False:
                return False
            elif cm is True:
                self.match_count += 1
                return Match(m, groups=self._compress_groups(m), offset=offset)
            else:  # Negation requested
                return Negation(cm, m)
        return False

    def _compress_groups(self, m):
        if self.capture_length:
            groups = m.groups()
            assert len(groups) % self.capture_length == 0
            for x in zip(*[iter(m.groups())] * self.capture_length):
                if x[0] is None:
                    continue
                else:
                    return x

    def matchgroup(self, text, index=0):
        m = self.matches(text)
        if m:
            return m.group(index)
        return m

    def sub(self, repl, text):
        return self.pattern.sub(repl, text)

    def next(self, text, **kwargs):
        m = self.pattern.search(text, **kwargs)
        if m:
            self.match_count += 1
            return text[m.end():]
        return text
