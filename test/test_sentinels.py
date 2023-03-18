import pytest

from seittik.utils.sentinels import sentinel


def test_sentinel_false():
    MEOW = sentinel('MEOW')
    assert not MEOW


def test_sentinel_never_eq():
    MEOW = sentinel('MEOW')
    assert MEOW != MEOW


def test_sentinel_repr():
    MEOW = sentinel('MEOW')
    assert repr(MEOW) == '<MEOW>'


def test_sentinel_unhashable():
    MEOW = sentinel('MEOW')
    with pytest.raises(TypeError):
        hash(MEOW)
