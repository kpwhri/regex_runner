from dataclasses import dataclass, InitVar

from typing.re import Match as ReMatch

from runrex.algo import Match
from runrex.algo import Negation


@dataclass
class Annotation:
    section: str
    sentence_idx: int
    label: str
    start_index: int = None
    end_index: int = None
    text: str = None
    negation: str = None
    target: str = None
    source_text: InitVar[str] = None
    gap_text_match: InitVar[ReMatch] = None
    context_window: InitVar[int] = 90
    precontext: str = None  # calculated
    postcontext: str = None  # calculated
    gapcontext: str = None

    def __post_init__(self, source_text: str, gap_text_match: ReMatch, context_window: int = 90):
        if source_text and self.start_index is not None and self.end_index:
            self.precontext = source_text[max(0, self.start_index - context_window): self.start_index]
            self.postcontext = source_text[self.end_index: self.end_index + context_window]
            if gap_text_match:
                if self.start_index > gap_text_match.start():
                    self.gapcontext = source_text[gap_text_match.end(): self.start_index]
                else:
                    self.gapcontext = source_text[self.end_index: gap_text_match.start()]

    @classmethod
    def from_match(cls, section: str, sentence_idx: int, label, match: Match, source_text: str, *, index=None):
        target = match.group(index) if index else None
        return cls(section.strip() if section else '', sentence_idx, label,
                   match.start(), match.end(), match.group(),
                   source_text=source_text, target=target)

    @classmethod
    def from_negation(cls, section, sentence_idx: int, label, negation: Negation, source_text: str, *, index=None):
        target = negation.group(index) if index else None
        return cls(section.strip() if section else '', sentence_idx, label,
                   negation.start(), negation.end(), negation.group(),
                   negation=negation.term_group(), gap_text_match=negation.negationobj, source_text=source_text,
                   target=target)

    @property
    def match_text(self):
        return self.text.strip().replace('\n', ' ')

    def to_dict(self):
        return {
            'section': self.section,
            'sentence_idx': self.sentence_idx,
            'label': self.label,
            'start_index': self.start_index,
            'end_index': self.end_index,
            'match': self.match_text,
            'negation': self.negation,
            'precontext': self.precontext,
            'postcontext': self.postcontext,
            'gapcontext': self.gapcontext,
            'target': self.target,
        }


def add_annotation(note, section, sentence_idx, pos_label, neg_label, result, source_text, *,
                   index=None):
    if not section and hasattr(note, 'get_section_at_index'):
        section = note.get_section_at_index(result.start())
    if isinstance(result, Match):
        note.add_annotation(Annotation.from_match(section, sentence_idx, pos_label, result, source_text,
                                                  index=index))
    elif isinstance(result, Negation):
        note.add_annotation(Annotation.from_negation(section, sentence_idx, neg_label, result, source_text,
                                                     index=index))
    else:
        print(f'Ignoring result of type {type(result)}')
