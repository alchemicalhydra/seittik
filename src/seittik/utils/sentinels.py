__all__ = ()


class SentinelMeta(type):
    def __bool__(cls):
        return False

    def __eq__(cls, other):
        return False

    def __repr__(cls):
        return f"<{cls.__name__}>"

    __hash__ = None


def sentinel(name):
    return SentinelMeta(name, (), {})


_END = sentinel('END')
_MISSING = sentinel('MISSING')
_POOL = sentinel('POOL')
