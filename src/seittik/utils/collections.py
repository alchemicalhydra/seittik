__all__ = ()


class defaultlist(list):
    def __init__(self, default_factory=None, /, *args, **kwargs):
        self.default_factory = default_factory
        super().__init__(*args, **kwargs)

    def __missing__(self, index):
        size = len(self)
        range_end = abs(index) if index < 0 else index + 1
        self.extend(self.default_factory() for i in range(size, range_end))
        return super().__getitem__(index)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except IndexError:
            if self.default_factory is None:
                raise
            return self.__missing__(key)


class Seen:
    """
    Container that returns `False` the first time a given object is
    tested for membership, and `True` thereafter.

    `key` should be a one-argument function used as a comparison key, and
    defaults to `hash`.

    For tracking mutable objects, consider `Seen(id)`.

    >>> s = Seen(hash)
    >>> [x in s for x in (1, 2, 1, 2, 3)]
    [False, False, True, True, False]
    >>> s = Seen(id)
    >>> a, b, c = [[1], [2], [1]]
    >>> [x in s for x in (a, b, c, a, b, c)]
    [False, False, False, True, True, True]
    """
    def __init__(self, key=hash):
        self._seen = set()
        self._key = key

    def __contains__(self, obj):
        obj_key = self._key(obj)
        if obj_key in self._seen:
            return True
        self._seen.add(obj_key)
        return False

    def __len__(self):
        return len(self._seen)

    def __repr__(self):
        return f'<{self.__class__.__name__} ({len(self)})>'

    def clear(self):
        self._seen.clear()
