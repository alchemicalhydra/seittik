__all__ = ()


class Sentinel:
    def __init__(self, name):
        self.name = name

    def __bool__(self):
        return False

    def __eq__(self, other):
        return False

    def __repr__(self):
        return f"<{self.name}>"

    __hash__ = None


_END = Sentinel('END')
_MISSING = Sentinel('MISSING')
_POOL = Sentinel('POOL')
