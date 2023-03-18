from collections.abc import Mapping, Sequence

import pytest

from seittik.utils.abc import NonStrSequence
from seittik.utils.walk import walk_collection, NonIterableNode


# walk_collection


def test_walk_collection_nested_lists():
    w = walk_collection(['a', ['b', ['c', ['d', ['e']]]]])
    assert list(w) == [
        (['a', ['b', ['c', ['d', ['e']]]]], 0, 'a'),
        (['a', ['b', ['c', ['d', ['e']]]]], 1, ['b', ['c', ['d', ['e']]]]),
        (['b', ['c', ['d', ['e']]]], 0, 'b'),
        (['b', ['c', ['d', ['e']]]], 1, ['c', ['d', ['e']]]),
        (['c', ['d', ['e']]], 0, 'c'),
        (['c', ['d', ['e']]], 1, ['d', ['e']]),
        (['d', ['e']], 0, 'd'),
        (['d', ['e']], 1, ['e']),
        (['e'], 0, 'e'),
    ]


def test_walk_collection_nested_dicts():
    w = walk_collection({'a': {'b': {'c': {'d': 'e'}}}})
    assert list(w) == [
        ({'a': {'b': {'c': {'d': 'e'}}}}, 'a', {'b': {'c': {'d': 'e'}}}),
        ({'b': {'c': {'d': 'e'}}}, 'b', {'c': {'d': 'e'}}),
        ({'c': {'d': 'e'}}, 'c', {'d': 'e'}),
        ({'d': 'e'}, 'd', 'e'),
    ]


def test_walk_collection_nested_lists_leaves_only():
    w = walk_collection(['a', ['b', ['c', ['d', ['e']]]]], leaves_only=True)
    assert list(w) == [
        (['a', ['b', ['c', ['d', ['e']]]]], 0, 'a'),
        (['b', ['c', ['d', ['e']]]], 0, 'b'),
        (['c', ['d', ['e']]], 0, 'c'),
        (['d', ['e']], 0, 'd'),
        (['e'], 0, 'e'),
    ]


def test_walk_collection_nested_dicts_leaves_only():
    w = walk_collection({'a': {'b': {'c': {'d': 'e'}}}}, leaves_only=True)
    assert list(w) == [
        ({'d': 'e'}, 'd', 'e'),
    ]


def test_walk_collection_nested_lists_max_depth_2():
    w = walk_collection(['a', ['b', ['c', ['d', ['e']]]]], max_depth=2)
    assert list(w) == [
        (['a', ['b', ['c', ['d', ['e']]]]], 0, 'a'),
        (['a', ['b', ['c', ['d', ['e']]]]], 1, ['b', ['c', ['d', ['e']]]]),
        (['b', ['c', ['d', ['e']]]], 0, 'b'),
        (['b', ['c', ['d', ['e']]]], 1, ['c', ['d', ['e']]]),
    ]


def test_walk_collection_nested_dicts_max_depth_2():
    w = walk_collection({'a': {'b': {'c': {'d': 'e'}}}}, max_depth=2)
    assert list(w) == [
        ({'a': {'b': {'c': {'d': 'e'}}}}, 'a', {'b': {'c': {'d': 'e'}}}),
        ({'b': {'c': {'d': 'e'}}}, 'b', {'c': {'d': 'e'}}),
    ]


def test_walk_collection_nested_lists_max_depth_2_leaves_only():
    w = walk_collection(['a', ['b', ['c', ['d', ['e']]]]], max_depth=2, leaves_only=True)
    assert list(w) == [
        (['a', ['b', ['c', ['d', ['e']]]]], 0, 'a'),
        (['b', ['c', ['d', ['e']]]], 0, 'b'),
        (['b', ['c', ['d', ['e']]]], 1, ['c', ['d', ['e']]]),
    ]


def test_walk_collection_nested_dicts_max_depth_2_leaves_only():
    w = walk_collection({'a': {'b': {'c': {'d': 'e'}}}}, max_depth=2, leaves_only=True)
    assert list(w) == [
        ({'b': {'c': {'d': 'e'}}}, 'b', {'c': {'d': 'e'}}),
    ]


def test_walk_collection_arg_strategy_bad():
    with pytest.raises(ValueError):
        walk_collection(['a', 'b', 'c'], strategy='MEOW')
    with pytest.raises(TypeError):
        walk_collection(['a', 'b', 'c'], strategy=13)


def test_walk_collection_arg_descend_bad():
    with pytest.raises(TypeError):
        walk_collection(['a', 'b', 'c'], descend='MEOW')
    with pytest.raises(TypeError):
        walk_collection(['a', 'b', 'c'], descend=13)


def test_walk_collection_arg_children_bad():
    with pytest.raises(TypeError):
        walk_collection(['a', 'b', 'c'], children=['meow'])
    with pytest.raises(TypeError):
        walk_collection(['a', 'b', 'c'], children=13)


def test_walk_collection_arg_collection_noniterable():
    with pytest.raises(TypeError):
        list(walk_collection('meow'))


def test_walk_collection_custom_descend_sequence_only():
    def descend(node):
        return isinstance(node, NonStrSequence)
    w = walk_collection(['a', {'b': {'c': 'd'}}, ['e', ['f']]], descend=descend)
    assert list(w) == [
        (['a', {'b': {'c': 'd'}}, ['e', ['f']]], 0, 'a'),
        (['a', {'b': {'c': 'd'}}, ['e', ['f']]], 1, {'b': {'c': 'd'}}),
        (['a', {'b': {'c': 'd'}}, ['e', ['f']]], 2, ['e', ['f']]),
        (['e', ['f']], 0, 'e'),
        (['e', ['f']], 1, ['f']),
        (['f'], 0, 'f'),
    ]


def test_walk_collection_custom_descend_mapping_only():
    def descend(node):
        return isinstance(node, Mapping)
    w = walk_collection(['a', {'b': {'c': 'd'}}, ['e', ['f']]], descend=descend)
    assert list(w) == [
        (['a', {'b': {'c': 'd'}}, ['e', ['f']]], 0, 'a'),
        (['a', {'b': {'c': 'd'}}, ['e', ['f']]], 1, {'b': {'c': 'd'}}),
        ({'b': {'c': 'd'}}, 'b', {'c': 'd'}),
        ({'c': 'd'}, 'c', 'd'),
        (['a', {'b': {'c': 'd'}}, ['e', ['f']]], 2, ['e', ['f']]),
    ]


def test_walk_collection_strategy_dfs():
    w = walk_collection(['a', ['b', ['c']], ['d', ['e']]], strategy='DFS')
    assert list(w) == [
        (['a', ['b', ['c']], ['d', ['e']]], 0, 'a'),
        (['a', ['b', ['c']], ['d', ['e']]], 1, ['b', ['c']]),
        (['b', ['c']], 0, 'b'),
        (['b', ['c']], 1, ['c']),
        (['c'], 0, 'c'),
        (['a', ['b', ['c']], ['d', ['e']]], 2, ['d', ['e']]),
        (['d', ['e']], 0, 'd'),
        (['d', ['e']], 1, ['e']),
        (['e'], 0, 'e'),
    ]


def test_walk_collection_strategy_bfs():
    w = walk_collection(['a', ['b', ['c']], ['d', ['e']]], strategy='BFS')
    assert list(w) == [
        (['a', ['b', ['c']], ['d', ['e']]], 0, 'a'),
        (['a', ['b', ['c']], ['d', ['e']]], 1, ['b', ['c']]),
        (['a', ['b', ['c']], ['d', ['e']]], 2, ['d', ['e']]),
        (['b', ['c']], 0, 'b'),
        (['b', ['c']], 1, ['c']),
        (['d', ['e']], 0, 'd'),
        (['d', ['e']], 1, ['e']),
        (['c'], 0, 'c'),
        (['e'], 0, 'e'),
    ]


def test_walk_collection_children_str():
    w = walk_collection(['a', {'x': {'a': [8, 9], 'x': [13, 14]}, 'y': {'b': 2}}, {'d': 'e', 'x': {'x': 99}}], children='x')
    assert list(w) == [
        (['a', {'x': {'a': [8, 9], 'x': [13, 14]}, 'y': {'b': 2}}, {'d': 'e', 'x': {'x': 99}}], 0, 'a'),
        (['a', {'x': {'a': [8, 9], 'x': [13, 14]}, 'y': {'b': 2}}, {'d': 'e', 'x': {'x': 99}}],
         1,
         {'x': {'a': [8, 9], 'x': [13, 14]}, 'y': {'b': 2}}),
        ({'x': {'a': [8, 9], 'x': [13, 14]}, 'y': {'b': 2}}, 'x', {'a': [8, 9], 'x': [13, 14]}),
        ({'a': [8, 9], 'x': [13, 14]}, 'x', [13, 14]),
        ([13, 14], 0, 13),
        ([13, 14], 1, 14),
        (['a', {'x': {'a': [8, 9], 'x': [13, 14]}, 'y': {'b': 2}}, {'d': 'e', 'x': {'x': 99}}], 2, {'d': 'e', 'x': {'x': 99}}),
        ({'d': 'e', 'x': {'x': 99}}, 'x', {'x': 99}),
        ({'x': 99}, 'x', 99),
    ]


def test_walk_collection_children_sequences_including_strings():
    def children(node):
        match node:
            case NonStrSequence() | str() if len(node) > 1:
                return enumerate(node)
            case _:
                raise NonIterableNode
    w = walk_collection(['a', 'bcd', ['e', ['f']]], children=children)
    assert list(w) == [
        (['a', 'bcd', ['e', ['f']]], 0, 'a'),
        (['a', 'bcd', ['e', ['f']]], 1, 'bcd'),
        ('bcd', 0, 'b'),
        ('bcd', 1, 'c'),
        ('bcd', 2, 'd'),
        (['a', 'bcd', ['e', ['f']]], 2, ['e', ['f']]),
        (['e', ['f']], 0, 'e'),
        (['e', ['f']], 1, ['f']),
    ]
