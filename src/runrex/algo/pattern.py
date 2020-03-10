import re
from copy import copy
from typing import Tuple, List, Iterable


class Match:

    def __init__(self, match, groups=None):
        self.match = match
        self._groups = groups

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
        return self.match.start(group)

    def end(self, group=0):
        return self.match.end(group)

    def __bool__(self):
        return bool(self.match)


class Pattern:

    def __init__(self, pattern: str, negates: Iterable[str] = None,
                 requires: Iterable[str] = None, requires_all: Iterable[str] = None,
                 replace_whitespace=r'\W*',
                 capture_length=None, retain_groups=None,
                 flags=re.IGNORECASE):
        """

        :param pattern: regular expressions (uncompiled)
        :param negates: regular expressions (uncompiled)
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

    def finditer(self, text, **kwargs):
        """Look for all matches

        TODO: allow configuring window, etc.

        :param text:
        :param kwargs:
        :return:
        """
        for m in self.pattern.finditer(text):
            if self._confirm_match(text, **kwargs):
                self.match_count += 1
                yield Match(m, groups=self._compress_groups(m))

    def matches(self, text, **kwargs):
        """Look for the first match -- this evaluation is at the sentence level.

        :param text:
        :param kwargs:
        :return:
        """
        m = self.pattern.search(text)
        if m:
            if not self._confirm_match(text, **kwargs):
                return False
            self.match_count += 1
            return Match(m, groups=self._compress_groups(m))
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

    def add(self, m):
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


def default_ssplit(text: str) -> Tuple[str, int, int]:
    target = '\n'
    start = 0
    for m in re.finditer(target, text):
        yield text[start:m.end()], start, m.end()
        start = m.end()
    yield text[start:], start, len(text)


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

    def get_patterns(self, pat, index=0):
        for sentence in self.sentences:
            yield from sentence.get_patterns(pat, index=index)

    def __len__(self):
        return len(self.sentences)

    def __iter__(self):
        return iter(self.sentences)

    def __getitem__(self, item):
        return self.sentences[item]


class Sentence:

    def __init__(self, text, mc: MatchCask = None, start=0, end=None):
        self.text = text
        self.matches = mc or MatchCask()
        self.start = start
        self.end = end if end else len(self.text)
        self.strip()  # remove extra start/ending characters

    def strip(self):
        ltext = self.text.lstrip()
        start_incr = len(self.text) - len(ltext)
        self.start += start_incr
        rtext = ltext.rstrip()
        self.end -= len(self.text) - len(rtext) - start_incr
        self.text = rtext

    def has_pattern(self, pat, ignore_negation=False):
        m = pat.matches(self.text, ignore_negation=ignore_negation)
        if m:
            self.matches.add(m)
        return bool(m)

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
        :param get_indices: to maintain backward compatibility
        :return:
        """
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
            if get_indices:
                return m.group(index), m.start(index) + self.start, m.end(index) + self.start
            else:
                return m.group(index)

    def get_patterns(self, pat: Pattern, index=0) -> Tuple[str, int, int]:
        """

        :param pat:
        :param index: group index (if using particular regex match group)
        :return:
        """
        for m in pat.finditer(self.text):
            self.matches.add(m)
            yield m.group(index), m.start(index), m.end(index)


class Section:

    def __init__(self, sentences, mc: MatchCask = None, add_matches=False):
        """

        :param sentences:
        :param mc:
        :param add_matches: use if you are copying data rather than
            passing around the same match object (default)
        """
        self.sentences = sentences
        self.text = '\n'.join(sent.text for sent in sentences)
        self.matches = mc or MatchCask()
        if add_matches:
            for sent in self.sentences:
                self.matches.add_all(sent.matches.matches)

    def has_pattern(self, pat, ignore_negation=False):
        m = pat.matches(self.text, ignore_negation=ignore_negation)
        if m:
            self.matches.add(m)
        return bool(m)

    def get_pattern(self, pat, index=0, get_indices=False):
        for sentence in self.sentences:
            yield from sentence.get_pattern(pat, index=index, get_indices=get_indices)

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


class Document:
    HISTORY_REMOVAL = re.compile(r'HISTORY:.*?(?=[A-Z]+:)')

    def __init__(self, name, file=None, text=None, encoding='utf8', ssplit=default_ssplit):
        """

        :param name:
        :param file:
        :param text:
        :param encoding:
        """
        self.name = name
        self.text = text
        self.matches = MatchCask()
        if file:
            with open(file, encoding=encoding) as fh:
                self.text = fh.read()
        if not self.text:
            raise ValueError(f'Missing text for {name}, file: {file}')
        # remove history section
        self.new_text = self._clean_text(self.HISTORY_REMOVAL.sub('\n', self.text))
        self.sentences = Sentences(self.new_text, self.matches, ssplit=ssplit or default_ssplit)

    def _clean_text(self, text):
        """
        These algorithms work on a sentence by sentence level, so occasionally need
            to clean up where the sentence boundaries are.
        :param text:
        :return:
        """
        text = re.sub(r': *\n', r': ', text, flags=re.I)
        return text

    def remove_patterns(self, *pats, ignore_negation=False):
        text = self.text
        for pat in pats:
            text = pat.sub('', text)
        if text:
            return Document(self.name, text=text)
        else:
            return None

    def has_pattern(self, pat, ignore_negation=False, by_sentence=True):
        """
        Look for patterns and their negation by sentence
        :param pat:
        :param ignore_negation:
        :param by_sentence:
        :return:
        """
        if by_sentence:
            return self.sentences.has_pattern(pat, ignore_negation=ignore_negation)
        else:
            m = pat.matches(self.text, ignore_negation=ignore_negation)
            if m:
                self.matches.add(m)
            return bool(m)

    def get_pattern(self, pat, index=0):
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
            if not isinstance(index, (list, tuple)):
                index = (index,)
            return m.group(*index)
        return m

    def get_patterns(self, *pats, index=0, names=None):
        """

        :param pats:
        :param index:
        :param names: if included, return name of matched pattern
            list same length as number of patterns
        :return:
        """
        for i, pat in enumerate(pats):
            res = self.get_pattern(pat, index=index)
            if res:
                if names:
                    return res, names[i]
                return res
        return None

    def has_patterns(self, *pats, has_all=False, ignore_negation=False, by_sentence=True):
        for pat in pats:
            if has_all and not self.has_pattern(pat, ignore_negation, by_sentence=by_sentence):
                return False
            elif not has_all and self.has_pattern(pat, ignore_negation, by_sentence=by_sentence):
                return True
        return has_all

    def select_sentences_with_patterns(self, *pats, negation=None, has_all=False,
                                       neighboring_sentences=0):
        for i, sentence in enumerate(self.sentences):
            sents = set()
            if sentence.has_patterns(*pats, has_all=has_all):
                if negation:
                    if sentence.has_patterns(*negation):
                        continue
                sents.add(i)
                for j in range(neighboring_sentences):
                    if i + j < len(self.sentences):
                        sents.add(i + j)
                    if i - j >= 0:
                        sents.add(i - j)
            if sents:
                yield Section([self.sentences[i] for i in sorted(list(sents))], self.matches)

    def select_all_sentences_with_patterns(self, *pats, negation=None, has_all=False, get_range=False,
                                           neighboring_sentences=0):
        sents = set()
        for i, sentence in enumerate(self.sentences):
            if sentence.has_patterns(*pats, has_all=has_all):
                if negation:
                    if sentence.has_patterns(*negation):
                        continue
                sents.add(i)
                for j in range(neighboring_sentences):
                    if i + j < len(self.sentences):
                        sents.add(i + j)
                    if i - j >= 0:
                        sents.add(i - j)
        sents = sorted(list(sents))
        if not sents:
            return None
        elif len(sents) == 1:
            return Section([self.sentences[sents[0]]], self.matches)
        elif get_range:
            return Section(self.sentences[sents[0]:sents[-1] + 1], self.matches)
        else:
            return Section([self.sentences[i] for i in sents], self.matches)

    def split(self, rx, group=1):
        prev_start = 0
        prev_name = None
        sections = Sections()
        for m in re.finditer(rx, self.text):
            if prev_name:
                sections.add(prev_name, self.text[prev_start: m.start()])
            prev_name = m.group(group)
            prev_start = m.end()
        if prev_name:
            sections.add(prev_name, self.text[prev_start:])
        return sections

    def __iter__(self) -> Sentence:
        for sent in self.sentences:
            yield sent


class Sections:

    def __init__(self):
        self.sections = {}

    def add(self, name, text, ssplit=default_ssplit):
        self.sections[name.upper()] = Section(
            [Sentence(s, start=sidx, end=eidx) for s, sidx, eidx in ssplit(text) if s.strip()]
        )

    def get_sections(self, *names) -> Section:
        sect = Section([])
        for name in names:
            name = name.upper()
            if name in self.sections:
                sect += self.get_section(name)
        return sect

    def get_section(self, name):
        if name.upper() in self.sections:
            return self.sections[name.upper()]
        return Section([])
