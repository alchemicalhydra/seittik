import pytest

from seittik.utils.merge import merge


def test_merge_no_mappings():
    with pytest.raises(TypeError, match='No mappings provided to merge'):
        merge([])


def test_merge_bad_sequence_arg_type():
    with pytest.raises(TypeError):
        merge([{}], sequence=13)


def test_merge_bad_sequence_arg_value():
    with pytest.raises(ValueError):
        merge([{}], sequence='meow')


def test_merge_single_mapping():
    res = merge([{'a': 1, 'b': 2}])
    assert res == {'a': 1, 'b': 2}


def test_merge_two_mappings():
    res = merge([{'a': 1, 'b': 2}, {'b': 3, 'c': 4}])
    assert res == {'a': 1, 'b': 3, 'c': 4}


def test_merge_three_mappings():
    res = merge([{'a': 1, 'b': 2}, {'b': 3, 'c': 4}, {'a': 9, 'd': 13}])
    assert res == {'a': 9, 'b': 3, 'c': 4, 'd': 13}


def test_merge_nested_mappings():
    res = merge([{'a': 1, 'b': {'c': 2}}, {'b': {'c': 4, 'd': 5}, 'e': 6}])
    assert res == {'a': 1, 'b': {'c': 4, 'd': 5}, 'e': 6}


@pytest.mark.parametrize(
    ['old', 'new', 'strategy', 'result'],
    [
        [[1, 2, 3], [4, 5, 6], lambda x, y: x, [1, 2, 3]],
        [[1, 2, 3], [4, 5, 6], 'keep', [1, 2, 3]],
        [[1, 2, 3], [4, 5, 6], 'replace', [4, 5, 6]],
        [[1, 2, 3], [4, 5, 6], 'extend-old-new', [1, 2, 3, 4, 5, 6]],
        [[1, 2, 3], [4, 5, 6], 'extend-new-old', [4, 5, 6, 1, 2, 3]],
        [[1, 2, 3, 4, 5, 6], [7, 8, 9], 'overlay-old-new', [7, 8, 9, 4, 5, 6]],
        [[1, 2, 3], [4, 5, 6, 7, 8, 9], 'overlay-new-old', [1, 2, 3, 7, 8, 9]],
    ],
)
def test_merge_sequence_strategies(old, new, strategy, result):
    res = merge([{'a': old}, {'a': new}], sequence=strategy)
    assert res == {'a': result}
