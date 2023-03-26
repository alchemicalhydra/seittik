from collections.abc import Callable, Mapping
from copy import deepcopy

from .abc import NonStrSequence
from .classutils import isinstance_all
from .stringutils import conjoin_phrases
from .walk import walk_collection


def _sequence_merge_extend_lr(left, right):
    return [*left, *right]


def _sequence_merge_extend_rl(left, right):
    return _sequence_merge_extend_lr(right, left)


def _sequence_merge_overlay_lr(left, right):
    ret = left[:]
    ret[:len(right)] = right
    return ret


def _sequence_merge_overlay_rl(left, right):
    return _sequence_merge_overlay_lr(right, left)


def _sequence_merge_replace_lr(left, right):
    return right


def _sequence_merge_replace_rl(left, right):
    return left


_SEQUENCE_MERGE_STRATEGIES = {
    'extend-old-new': _sequence_merge_extend_lr,
    'extend-new-old': _sequence_merge_extend_rl,
    'overlay-old-new': _sequence_merge_overlay_lr,
    'overlay-new-old': _sequence_merge_overlay_rl,
    'replace': _sequence_merge_replace_lr,
    'keep': _sequence_merge_replace_rl,
}
_SEQUENCE_MERGE_STRATEGY_NAMES = conjoin_phrases(sorted(_SEQUENCE_MERGE_STRATEGIES.keys()), conj='or', fmt=repr)


class StopDescending(Exception):
    pass


def merge(mappings, /, *, sequence='replace'):
    """
    Recursively merge `mappings` left-to-right.

    All collections in the resulting mapping are deep-copied and thus
    safe to mutate without affecting the original arguments.

    Values are handled as follows:

    - Mappings are merged with mappings, with identical keys being
      overwritten.

    - A mapping is entirely replaced by a non-mapping, and vice-versa.

    - A sequence with the same path as an existing sequence uses the
      `sequence` argument to determine how to handle it:

      - `'replace'` (the default) replaces the old sequence with the new
        sequence.

      - `'keep'` keeps the old sequence and discards the new sequence.

      - `'extend-old-new'` replaces the old sequence with a concatenation of
        the old sequence followed by the new sequence.

      - `'extend-new-old'` replaces the old sequence with a concatenation of
        the new sequence followed by the old sequence.

      - `'overlay-old-new'` replaces the old sequence with the result of
        replacing the beginning of the old sequence with the corresponding items
        from the new sequence. (If the new sequence is as long or longer than
        the old sequence, this is equivalent to `'replace'`.)

      - `'overlay-new-old'` replaces the old sequence with the result of
        replacing the beginning of the new sequence with the corresponding items
        from the old sequence. (If the old sequence is as long or longer than
        the new sequence, this is equivalent to `'keep'`.)

      - A custom callable can be provided, which will be used to merge the
        sequences. It should accept two positional arguments: `old_sequence,
        new_sequence`, and return an appropriate item. (It is safe to return
        an argument from a `sequence` callable unchanged or mutated.)
    """
    match sequence:
        case str():
            try:
                sequence_merge = _SEQUENCE_MERGE_STRATEGIES[sequence]
            except KeyError as exc:
                raise ValueError("'sequence' must be one of {_SEQUENCE_MERGE_STRATEGY_NAMES}") from exc
        case Callable():
            sequence_merge = sequence
        case _:
            raise TypeError("'sequence' must be a callable or one of {_SEQUENCE_MERGE_STRATEGY_NAMES}")
    mapping_ix = iter(mappings)
    try:
        merged = deepcopy(next(mapping_ix))
    except StopIteration as exc:
        raise TypeError("No mappings provided to merge") from exc
    for mapping in mapping_ix:
        ix = walk_collection(
            mapping,
            full_path=True,
            strategy='DFS',
            descend=lambda x: isinstance(x, Mapping),
        )
        for full_path in ix:
            target = merged
            try:
                for parent, key, source_value in full_path:
                    try:
                        target_value = target[key]
                    except (IndexError, KeyError) as exc:
                        # Key doesn't exist in target, so assign and stop descending
                        target[key] = deepcopy(source_value)
                        raise StopDescending from exc
                    merge_values = (target_value, source_value)
                    if isinstance_all(merge_values, Mapping):
                        # Both are mappings, so keep descending
                        target = target_value
                        continue
                    if isinstance_all(merge_values, NonStrSequence):
                        # Both are sequences; sequence merge, but stop descending
                        merge_target = deepcopy(target_value)
                        target[key] = sequence_merge(merge_target, deepcopy(source_value))
                        raise StopDescending
                    # Both are different types, so assign and stop descending
                    target[key] = deepcopy(source_value)
                    raise StopDescending
            except StopDescending:
                pass
    return merged
