from collections.abc import Iterator

from .argutils import check_int_positive
from .abc import NonStrSequence
from .sentinels import _MISSING
from .walk import walk_collection, NonIterableNode


def iter_flatten(node):
    match node:
        case Iterator() | NonStrSequence():
            return enumerate(node)
        case _:
            raise NonIterableNode(f"Not an iterable node: {node=} {type(node)=}")


def flatten(ix, /, *, levels=_MISSING):
    if levels is not _MISSING:
        check_int_positive('levels', levels)
        levels += 1
    for _, _, v in walk_collection(ix, leaves_only=True, max_depth=levels, children=iter_flatten):
        yield v
