class Minimum:
    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __repr__(self):
        return '<MINIMUM>'


class Maximum:
    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return True

    def __repr__(self):
        return '<MAXIMUM>'


MINIMUM = Minimum()
MAXIMUM = Maximum()
