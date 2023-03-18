import pytest

from seittik.utils.flatten import flatten


def test_flatten_all():
    x = ['a', ['b', ['c', ['d', ['e']]]]]
    assert list(flatten(x)) == ['a', 'b', 'c', 'd', 'e']


def test_flatten_1():
    x = ['a', ['b', ['c', ['d', ['e']]]]]
    assert list(flatten(x, levels=1)) == ['a', 'b', ['c', ['d', ['e']]]]


def test_flatten_2():
    x = ['a', ['b', ['c', ['d', ['e']]]]]
    assert list(flatten(x, levels=2)) == ['a', 'b', 'c', ['d', ['e']]]
