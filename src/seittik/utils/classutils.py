from abc import ABCMeta, abstractmethod
from functools import wraps
from types import MethodType
from weakref import WeakKeyDictionary


__all__ = ()


class MultiMethodMeta(ABCMeta):
    def __get__(cls, instance, owner=None):
        if instance is None:
            return MethodType(cls._class, owner)
        return MethodType(cls._instance, instance)


class multimethod(metaclass=MultiMethodMeta):
    """
    Create a method with separate class and instance invocations.

    ```{eval-rst}
    .. ipython::
        :reset_history:

    In [1]: class Foo:
      ....:     class bar(multimethod):
      ....:         def _class(cls, x):
      ....:             return x + 3
      ....:         def _instance(self, a, b):
      ....:             return a * b

    In [1]: f = Foo()

    In [1]: Foo.bar(5)
    Out[1]: 8

    In [1]: f.bar(2, 7)
    Out[1]: 14
    ```
    """
    @abstractmethod
    def _class(cls, *args, **kwargs):
        ...

    @abstractmethod
    def _instance(self, *args, **kwargs):
        ...


class classonlymethod:
    """
    Create a class method that raises a {py:exc}`TypeError` if invoked as an
    instance method.
    """
    def __init__(self, func):
        self._class = func

    def __get__(self, instance, owner=None):
        if instance is None:
            return MethodType(self._class, owner)
        return MethodType(self._instance, instance)

    def _instance(self, *args, **kwargs):
        raise TypeError(f"{self._class.__name__!r} is a class method, not an instance method")


class partialclassmethod:
    """
    Create a method that operates normally if invoked as an instance method,
    but returns a partial if invoked as a class method.
    """
    def __init__(self, func):
        self._func = func

    def __get__(self, instance, owner=None):
        if instance is None:
            @wraps(self._func)
            def _partialclassmethod(cls, *args, **kwargs):
                class PartialClassMethod:
                    def __call__(partial_self, *partial_args, **partial_kwargs):
                        return self._func(owner(*partial_args, **partial_kwargs), *args, **kwargs)
                    def __repr__(partial_self):
                        return f"<{self._func.__qualname__}({args=} {kwargs=})>"
                return PartialClassMethod()
            return MethodType(_partialclassmethod, owner)
        return MethodType(self._func, instance)


class lazyattr:
    """
    Create a lazy attribute that's only instantiated upon its first
    attempted access, using the decorated method. The resulting value is
    cached and returned on subsequent accesses.

    Calling `del` on a lazy attribute clears the cached value, causing it to
    be recomputed on future accesses.

    Keep in mind that IPython may retain references to "deleted" instances,
    causing the cache to retain references to those instances longer than
    expected.
    """
    def __init__(self, func):
        self._func = func
        self._cache = WeakKeyDictionary()

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            v = self._cache[instance]
        except KeyError:
            v = self._func(instance)
            self._cache[instance] = v
        return v

    def __set__(self, instance, value):
        self._cache[instance] = value

    def __delete__(self, instance):
        try:
            del self._cache[instance]
        except KeyError:
            pass
