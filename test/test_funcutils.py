import pytest

from seittik.utils.funcutils import attach, multilambda


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


def test_multilambda_required_provided():
    @multilambda('b')
    def foo(a, b=3):
        return b(a)

    res = foo(15, lambda x: x + 3)
    assert res == 18


def test_multilambda_required():
    @multilambda('b')
    def foo(a, b=3):
        return b(a)

    @foo(15)
    def res(x):
        return x + 3

    assert res == 18


def test_multilambda_optional():
    @multilambda('b', optional=True)
    def foo(a, b=3):
        return b(a)

    @foo(15, b=True)
    def res(x):
        return x + 3

    assert res == 18


def test_multilambda_not_keyword():
    with pytest.raises(TypeError, match='with a default'):
        @multilambda('a')
        def foo(a, b=3):
            return b(a)


def test_multilambda_param_missing():
    with pytest.raises(ValueError, match='not found on decorated function'):
        @multilambda('c')
        def foo(a, b=3):
            return b(a)
            assert False
