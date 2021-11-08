import re
from typing import Iterable, List, Optional, Iterator

from runrex.algo import MatchCask
from runrex.text.section import Section
from runrex.text.sections import Sections
from runrex.text.sentence import Sentence
from runrex.text.sentences import Sentences
from runrex.text.ssplit import default_ssplit


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

    @classmethod
    def clean_text(cls, text, ssplit=default_ssplit):
        return re.sub(r': *\n', r': ', Document.HISTORY_REMOVAL.sub('\n', text), flags=re.I)

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

    def iter_sentence_by_pattern(self, *pats, ignore_negation=None, has_all=False) -> Iterable[Sentence]:
        for sentence in self:
            if sentence.has_patterns(*pats, ignore_negation=ignore_negation, has_all=has_all):
                yield sentence

    def _select_sentence_idx_with_neighbors(self, sentence, i, *pats, negation=None, has_all=False,
                                            neighboring_sentences=0) -> Iterable[int]:
        if sentence.has_patterns(*pats, has_all=has_all):
            if negation:
                if sentence.has_patterns(*negation):
                    return
            yield i
            for j in range(neighboring_sentences):
                if i + j < len(self.sentences):
                    yield i + j
                if i - j >= 0:
                    yield i - j

    def _select_all_sentence_indices(self, sentence, i, *pats, negation=None, has_all=False,
                                     neighboring_sentences=0) -> List[int]:
        return sorted([idx for idx in
                       self._select_sentence_idx_with_neighbors(sentence, i, *pats, negation=negation, has_all=has_all,
                                                                neighboring_sentences=neighboring_sentences)])

    def select_sentences_with_patterns(self, *pats, negation=None, has_all=False,
                                       neighboring_sentences=0) -> Iterable[Section]:
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
                                           neighboring_sentences=0) -> Optional[Section]:
        sents = []
        for i, sentence in enumerate(self.sentences):
            sents += self._select_all_sentence_indices(sentence, i, *pats, negation=negation, has_all=has_all,
                                                       neighboring_sentences=neighboring_sentences)
        if not sents:  # must be sorted
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

    def __iter__(self) -> Iterator[Sentence]:
        for sent in self.sentences:
            yield sent

    def __getitem__(self, item):
        return self.sentences[item]

    def neighbors(self, index, num_neighbors=1) -> List[Sentence]:
        """
        Get sentences with neighbors by sentence index
        :param index:
        :param num_neighbors:
        :return:
        """
        return self[max(index + num_neighbors, 0): index + num_neighbors]

    def neighbors_text(self, index, num_neighbors=1, join=' '):
        return join.join(sent.text for sent in self.neighbors(index, num_neighbors=num_neighbors))
