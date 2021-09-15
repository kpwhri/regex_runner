from copy import copy

from runrex.algo import Match


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
