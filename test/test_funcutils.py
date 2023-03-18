import pytest

from seittik.utils.funcutils import attach


def test_attach_one():
    @attach(bar='meow')
    def foo():
        pass
    assert foo.bar == 'meow'


def test_attach_two():
    @attach(cat='meow', dog='woof')
    def foo():
        pass
    assert foo.cat == 'meow'
    assert foo.dog == 'woof'
