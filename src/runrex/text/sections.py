from runrex.text.section import Section
from runrex.text.sentence import Sentence
from runrex.text.ssplit import default_ssplit


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
