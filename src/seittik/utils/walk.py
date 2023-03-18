from collections import deque
from collections.abc import Mapping

from .abc import NonStrSequence
from .argutils import check_int_positive
from .sentinels import _MISSING


class NonIterableNode(TypeError):
    pass


def iter_collection_node(node):
    """
    Yield `(key, value)` tuples for a NonStrSequence or a Mapping.
    """
    match node:
        case NonStrSequence():
            return enumerate(node)
        case Mapping():
            return node.items()
        case _:
            raise NonIterableNode(f"Not an iterable node: {node=} {type(node)=}")


# Provided as a separate generator so the proper `walk_collection` can
# immediately raise an exception if any arguments are invalid.
def _walk_collection(
    *,
    collection,
    local_iter_node,
    full_path,
    leaves_only,
    strategy,
    max_depth,
    descend,
    ):
    try:
        pipeline = deque([([(collection, k, v)]) for k, v in local_iter_node(collection)])
    except NonIterableNode as exc:
        raise TypeError(f"Provided collection is not iterable: {collection!r}") from exc
    while True:
        try:
            path = pipeline.popleft()
        except IndexError:
            break
        parent, key, item = path[-1]
        try:
            if descend is not _MISSING and not descend(item):
                raise NonIterableNode
            contents = local_iter_node(item)
        except NonIterableNode:
            yield tuple(path) if full_path else (parent, key, item)
            continue
        else:
            if not leaves_only:
                yield tuple(path) if full_path else (parent, key, item)
        if max_depth is not _MISSING and len(path) >= max_depth:
            if leaves_only:
                yield (parent, key, item)
            continue
        pipe_contents = [path + [(item, k, v)] for k, v in contents]
        if strategy == 'DFS':
            pipeline.extendleft(reversed(pipe_contents))
        else:
            pipeline.extend(pipe_contents)


def walk_collection(
    collection, /, *,
    full_path=False,
    leaves_only=False,
    strategy='DFS',
    max_depth=_MISSING,
    descend=_MISSING,
    children=_MISSING,
    ):
    """
    Iterate over the nodes of `collection`.

    Yields `(parent, key, node)` tuples, where `parent[key] is node`.

    If `full_path` is true, instead yields tuples of `(parent, key, node)`
    tuples representing the full path to a given node.

    If `leaves_only` is true, only leaf nodes will be yielded.

    `strategy` must be one of `'DFS'` (depth-first search; default) or
    `'BFS'` (breadth-first search).

    If `max_depth` is provided as a positive integer, only descend up to the
    provided depth. `max_depth=1` would yield only the values directly
    within the collection, `max_depth=2` would yield those items as well as
    their children, and so on.

    If `descend` is a callable, only nodes for which `descend(node)` is true
    will be recursively descended into.

    If `children` is a callable, `children(node)` should return an iterable
    yielding child node `(key, value)` pairs for a given mapping `node`,
    which will be used instead of descending into every possible mapping and
    non-string sequence.

    If `children` is a string, as a convenience, it will yield only values
    of matching keys when mappings are encountered.
    """
    match strategy:
        case str() if strategy in ('DFS', 'BFS'):
            pass
        case str():
            raise ValueError("'strategy' must be one of 'DFS', 'BFS'")
        case _:
            raise TypeError("'strategy' must be a string and one of 'DFS', 'BFS'")
    if max_depth is not _MISSING:
        check_int_positive('max_depth', max_depth)
    if descend is not _MISSING and not callable(descend):
        raise TypeError("'descend' must be a callable")
    match children:
        case str():
            def local_iter_node(node):
                match node:
                    case NonStrSequence():
                        return enumerate(node)
                    case Mapping():
                        return ((k, v) for k, v in node.items() if k == children)
                    case _:
                        raise NonIterableNode(f"Not an iterable node: {node=} {type(node)=}")
        case _ if children is _MISSING:
            local_iter_node = iter_collection_node
        case _ if callable(children):
            local_iter_node = children
        case _:
            raise TypeError("'children' must be a callable or a string")
    return _walk_collection(
        collection=collection,
        local_iter_node=local_iter_node,
        full_path=full_path,
        leaves_only=leaves_only,
        strategy=strategy,
        max_depth=max_depth,
        descend=descend,
    )
