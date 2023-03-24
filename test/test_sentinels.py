import pytest

from seittik.utils.sentinels import Sentinel


def test_sentinel_false():
    MEOW = Sentinel('MEOW')
    assert not MEOW


def test_sentinel_never_eq():
    MEOW = Sentinel('MEOW')
    assert MEOW != MEOW


def test_sentinel_repr():
    MEOW = Sentinel('MEOW')
    assert repr(MEOW) == '<MEOW>'


def test_sentinel_unhashable():
    MEOW = Sentinel('MEOW')
    with pytest.raises(TypeError):
        hash(MEOW)


def test_sentinel_uncallable():
    MEOW = Sentinel('MEOW')
    assert not callable(MEOW)
