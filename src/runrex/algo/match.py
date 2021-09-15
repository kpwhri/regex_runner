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
