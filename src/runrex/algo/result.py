import enum


class Status(enum.Enum):
    pass


class Source(enum.Enum):
    pass


class DefaultStatus(Status):
    SKIP = 99


class Result:

    __slots__ = ['_value', 'result', 'expected', '_text', 'correct',
                 '_extras', 'date', 'start', 'end']

    def __init__(self, value: Status, result=None, expected=None,
                 text=None, date=None, start=None, end=None, extras=None):
        self._value = value
        self.result = result or value.value
        self.expected = expected
        self._text = text
        self.correct = None
        self.date = date
        self.start = start  # index
        self.end = end  # index
        if not extras:
            self._extras = dict()
        elif isinstance(extras, dict):
            self._extras = dict(extras)
        else:
            self._extras = {'extras': extras}
        if self.expected:
            self.correct = self.result == self.expected

    @property
    def value(self):
        return self._value.name

    @property
    def extras(self):
        return self._extras

    @property
    def text(self):
        if self._text:
            return ' '.join(self._text.split())

    def is_skip(self):
        return self._value.value == 99

    def __repr__(self):
        return f'<Result:{self.correct}:{self.result}==exp({self.expected})>'

    def __str__(self):
        return repr(self)

    def __bool__(self):
        return self.result >= 0 and not self.is_skip()
