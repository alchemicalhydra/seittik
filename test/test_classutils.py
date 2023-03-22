import pytest

from seittik.utils.classutils import (
    classonlymethod, lazyattr, multimethod, partialclassmethod,
)


# multimethod

def test_multimethod():
    class Foo:
        class bar(multimethod):
            def _class(cls, x):
                return x * 3
            def _instance(self, a, b):
                return a + b

    assert Foo.bar(5) == 15
    foo = Foo()
    assert foo.bar(6, 7) == 13


# classonlymethod

def test_classonlymethod_instance():
    class Foo:
        @classonlymethod
        def bar(cls):
            return 'meow'

    assert Foo.bar() == 'meow'
    foo = Foo()
    with pytest.raises(TypeError):
        foo.bar()


# partialclassmethod

def test_partialclassmethod():
    class Foo:
        @partialclassmethod
        def add(self, a, b):
            return a + b

    foo = Foo()
    assert foo.add(3, 4) == 7
    part = Foo.add(3, 4)
    assert part() == 7
    assert repr(part) == '<test_partialclassmethod.<locals>.Foo.add(args=(3, 4) kwargs={})>'


# lazyattr

def test_lazyattr():
    check = []
    class Foo:
        @lazyattr
        def bar(self):
            check.append(1)
            return 3
    assert isinstance(Foo.bar, lazyattr)
    foo1 = Foo()
    assert foo1.bar == 3
    assert check == [1]
    foo1.bar = 5
    assert foo1.bar == 5
    assert check == [1]
    del foo1.bar
    assert foo1.bar == 3
    assert check == [1, 1]
    del foo1.bar
    del foo1.bar
    assert foo1.bar == 3
    assert check == [1, 1, 1]
    assert foo1.bar == 3
    assert check == [1, 1, 1]
    foo2 = Foo()
    assert foo2.bar == 3
    assert check == [1, 1, 1, 1]
    assert foo2.bar == 3
    assert check == [1, 1, 1, 1]
