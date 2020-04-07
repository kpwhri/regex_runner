import re
from copy import copy
from typing import Iterable


class Match:

    def __init__(self, match, groups=None, offset=0):
        self.match = match
        self._groups = groups
        self._offset = offset

    def group(self, *index):
        if not self._groups or not index or len(index) == 1 and index[0] == 0:
            return self.match.group(*index)
        res = []
        if not isinstance(index, tuple):
            index = (index,)
        for idx in index:
            if idx == 0:
                res.append(self.match.group())
            else:
                res.append(self._groups[idx - 1])

    def groups(self):
        if not self._groups:
            return self.match.groups()
        else:
            return tuple(self._groups)

    def start(self, group=0):
        return self.match.start(group) + self._offset

    def end(self, group=0):
        return self.match.end(group) + self._offset

    def __bool__(self):
        return bool(self.match)


class Pattern:

    def __init__(self, pattern: str, negates: Iterable[str] = None,
                 requires: Iterable[str] = None, requires_all: Iterable[str] = None,
                 replace_whitespace=r'\W*',
                 capture_length=None, retain_groups=None,
                 flags=re.IGNORECASE):
        """

        :param pattern: regular expressions (uncompiled string)
        :param negates: regular expressions (uncompiled string)
        :param replace_whitespace:
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
        self.negates = []
        for negate in negates or []:
            if replace_whitespace:
                negate = replace_whitespace.join(negate.split(' '))
            self.negates.append(re.compile(negate, flags))
        self.requires = []
        for require in requires or []:
            if replace_whitespace:
                require = replace_whitespace.join(require.split(' '))
            self.requires.append(re.compile(require, flags))
        self.requires_all = []
        for require in requires_all or []:
            if replace_whitespace:
                require = replace_whitespace.join(require.split(' '))
            self.requires_all.append(re.compile(require, flags))

        self.capture_length = capture_length
        self.text = self.pattern.pattern

    def __str__(self):
        return self.text

    def _confirm_match(self, text, ignore_negation=False,
                       ignore_requires=False, ignore_requires_all=False):
        if not ignore_negation:
            for negate in self.negates:
                if negate.search(text):
                    return False
        if not ignore_requires and self.requires:
            found = False
            for require in self.requires:
                if require.search(text):
                    found = True
                    break
            if not found:
                return False
        if not ignore_requires_all:
            for require in self.requires_all:
                if not require.search(text):
                    return False
        return True

    def finditer(self, text, *, offset=0, **kwargs):
        """Look for all matches

        TODO: allow configuring window, etc.

        :param offset:
        :param text:
        :param kwargs:
        :return:
        """
        for m in self.pattern.finditer(text):
            if self._confirm_match(text, **kwargs):
                self.match_count += 1
                yield Match(m, groups=self._compress_groups(m), offset=offset)

    def matches(self, text, *, offset=0, **kwargs):
        """Look for the first match -- this evaluation is at the sentence level.

        :param offset:
        :param text:
        :param kwargs:
        :return:
        """
        m = self.pattern.search(text)
        if m:
            if not self._confirm_match(text, **kwargs):
                return False
            self.match_count += 1
            return Match(m, groups=self._compress_groups(m), offset=offset)
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
        else:
            return None

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


class MatchCask:

    def __init__(self):
        self.matches = []

    @property
    def start(self):
        if self.matches:
            return min(m.start() for m in self.matches)
        return None

    @property
    def end(self):
        if self.matches:
            return max(m.end() for m in self.matches)
        return None

    @property
    def last_start(self):
        return self.last.start()

    @property
    def last_end(self):
        return self.last.end()

    @property
    def last_text(self):
        return self.last.group()

    @property
    def last(self) -> Match:
        if self.matches:
            return self.matches[-1]

    def add(self, m: Match):
        self.matches.append(m)

    def add_all(self, matches):
        self.matches += matches

    def copy(self):
        mc = MatchCask()
        mc.matches = copy(self.matches)
        return mc

    def __repr__(self):
        return repr(set(m.group() for m in self.matches))

    def __str__(self):
        return str(set(m.group() for m in self.matches))

    def __iter__(self):
        return iter(self.matches)

    def __getitem__(self, item):
        return self.matches[item]


