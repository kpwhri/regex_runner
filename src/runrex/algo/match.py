import re


class Match:

    def __init__(self, match, groups=None, offset=0):
        self._match = match
        self._groups = groups
        self._offset = offset

    @property
    def matchobj(self):
        return self._match

    @property
    def match(self):
        if isinstance(self._match, re.Match):
            return self._match.group()
        return str(self._match)

    def group(self, *index):
        if not self._groups or not index or len(index) == 1 and index[0] == 0:
            return self._match.group(*index)
        res = []
        if not isinstance(index, tuple):
            index = (index,)
        for idx in index:
            if idx == 0:
                res.append(self._match.group())
            else:
                res.append(self._groups[idx - 1])

    def groups(self):
        if not self._groups:
            return self._match.groups()
        else:
            return tuple(self._groups)

    def start(self, group=0):
        return self._match.start(group) + self._offset

    def end(self, group=0):
        return self._match.end(group) + self._offset

    def __bool__(self):
        return bool(self._match)
