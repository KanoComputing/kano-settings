import difflib


class Line(object):

    def __init__(self, line, line_no, config_filter=''):
        self.line = line
        self.line_no = line_no
        self.config_filter = config_filter

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.line

    def __eq__(self, other):
        if isinstance(other, Line):
            return self.line == other.line \
                    and self.line_no == other.line_no \
                    and self.config_filter == other.config_filter

        if isinstance(other, basestring):
            return self.line == other


class Diff(object):
    PLUS_STR = '+ '
    MINUS_STR = '- '

    def __init__(self, a, b):
        self.a = a
        self.b = b

        self.diff = difflib.Differ().compare(a, b)
        self.added = []
        self.removed = []

        for i, line in enumerate(self.diff):
            line = line.rstrip()

            if not line:
                continue

            if line.startswith(self.PLUS_STR):
                line = line.split(self.PLUS_STR, 1)[-1]
                self.added.append(Line(line, i))
                continue

            if line.startswith(self.MINUS_STR):
                line = line.split(self.MINUS_STR, 1)[-1]
                self.removed.append(Line(line, i))
                continue

        print(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '\n'.join([
            'added: {},'.format(self.added),
            'removed: {}'.format(self.removed)
        ])
