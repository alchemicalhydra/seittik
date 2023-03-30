"""
Functional pipes for processing iterable data.

Pipes are much more powerful when combined with *shears*; see
{py:mod}`seittik.shears`.
"""
import array
import builtins
import collections
from collections.abc import (
    Callable, Container, Iterable, Iterator,
    Mapping, MutableSequence, Sequence, Set, Sized,
)
import functools
import inspect
import itertools
import math
import os
import pathlib
import random
import statistics
import struct
from types import EllipsisType, FunctionType

from .utils.abc import NonStrSequence
from .utils.argutils import (
    check_int, check_int_positive, check_int_positive_or_none,
    check_int_zero_or_positive, check_k_args, check_slice_args, replace,
)
from .utils.classutils import (
    classonlymethod, lazyattr, multimethod, partialclassmethod,
)
from .utils.collections import Seen
from .utils.compareutils import MAXIMUM, MINIMUM
from .utils.diceutils import DiceRoll
from .utils.flatten import flatten
from .utils.merge import merge
from .utils.randutils import SHARED_RANDOM
from .utils.sentinels import _DROP, _END, _KEEP, _MISSING, _POOL, Sentinel
from .utils.structutils import calc_struct_input
from .utils.walk import walk_collection


__all__ = ('Pipe',)


DROP = _DROP
END = _END
KEEP = _KEEP


class EnumerateInfo:
    def __init__(self, i, *, is_first=False, is_last=False):
        self.i = i
        self.index = i
        self.is_first = is_first
        self.is_last = is_last

    def __repr__(self):
        index = self.index
        is_first = self.is_first
        is_last = self.is_last
        return f"<EnumerateInfo {index=} {is_first=} {is_last=}>"


class PlainSource:
    def __init__(self, source):
        self._source = source

    def __repr__(self):
        return repr(self._source)

    def __call__(self):
        return self._source


class Pipe:
    """
    A fluent interface for processing iterable data.

    A Pipe is built out of three kinds of parts, or *stages*:

    - A Pipe has a *source*, which is the initial iterable of data provided to
      a Pipe.

      {py:class}`Pipe` also provides alternate constructors which generate
      their own sources (e.g., {py:meth}`Pipe.range` for ranges of numbers).

    - Pipes have zero or more *steps*, which are intermediate transformation
      of data, each represented internally by a one-argument function that
      accepts an iterable, and returns a new iterable.

      Calling a step method clones the current Pipe and returns the clone with
      that step appended; it does not mutate the Pipe in-place, nor does it
      perform any evaluation.

    - A Pipe is evaluated by calling a *sink*, which applies all steps and
      returns a final value of some kind.

    A Pipe can also be iterated upon directly, which acts as a sink that
    yields successive items with all steps applied.

    Providing an initial source is optional. A Pipe that has not yet been
    evaluated can be called with a source, which will clone the Pipe using
    the provided source.

    Similarly, all sinks act as partials if called as class methods,
    accepting a source which will be immediately evaluated.

    ```{ipython}

    # All of these are equivalent:
    In [1]: Pipe([1, 2, 3, 4, 5]).list()
    Out[1]: [1, 2, 3, 4, 5]

    In [1]: Pipe()([1, 2, 3, 4, 5]).list()
    Out[1]: [1, 2, 3, 4, 5]

    In [1]: Pipe.list()([1, 2, 3, 4, 5])
    Out[1]: [1, 2, 3, 4, 5]
    ```
    """
    DROP = _DROP
    KEEP = _KEEP

    def __init__(self, source=_MISSING, *, rng=_MISSING):
        self._source = source if source is _MISSING else PlainSource(source)
        self._steps = []
        if rng is not _MISSING:
            self._set_rng(rng)

    def __call__(self, source):
        """
        A Pipe can be called with a new source, which clones the Pipe, replaces
        the existing source, and returns the new Pipe.
        """
        p = self.clone()
        p._source = source if source is _MISSING else PlainSource(source)
        return p

    def __getitem__(self, key):
        """
        A Pipe can be indexed or sliced.

        - `Pipe[n]` is equivalent to calling {py:meth}`Pipe.nth`
        - `Pipe[start:stop:step]` is equivalent to calling {py:meth}`Pipe.slice`
        """
        match key:
            case int():
                return self.nth(key)
            case slice():
                return self.slice(key.start, key.stop, key.step)
            case _:
                raise TypeError(f"{self.__class__.__name__} indices must be integers or slices, not {type(key)}")

    def __iter__(self):
        """
        Iterating over a Pipe evaluates it and yields the resulting items.
        """
        yield from self._evaluate()

    def __repr__(self):
        match self._source:
            case _ if self._source is _MISSING:
                sourcestr = '*'
            case FunctionType():
                sourcestr = self._source.__name__.lstrip('pipe_')
            case _:
                sourcestr = repr(self._source)
        stepstr = ' => '.join([sourcestr, *(step.__name__.lstrip('pipe_') for step in self._steps)])
        return f"<Pipe {stepstr}>"

    def __reversed__(self):
        return self.clone().reverse()

    ##############################################################
    # Internal evaluation logic

    @classmethod
    def _with_source(cls, func):
        p = cls()
        p._source = func
        return p

    def _with_step(self, step):
        p = self.clone()
        p._steps.append(step)
        return p

    def _process(self, sink):
        res = self._depinject(self._source)
        for step in self._steps:
            res = self._depinject(step, res)
        if sink is not _MISSING:
            res = self._depinject(sink, res)
        return res

    def _evaluate(self, sink=_MISSING):
        if self._source is _MISSING:
            if sink is not _MISSING:
                def pipe_partial(source):
                    return self(source)._process(sink)
                return pipe_partial
            raise TypeError("A source must be provided to evaluate a Pipe")
        return self._process(sink)

    def _depinject(self, stage, res=_MISSING):
        stage_params = [
            k for k, p in inspect.signature(stage).parameters.items()
            if p.kind in {inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD}
        ]
        stage_args = []
        for stage_param in stage_params:
            match (stage_param, res):
                case (('ix' | 'pipe' | 'res' | 'seq'), _) if res is _MISSING:
                    raise ValueError(f"{stage!r} is a source and requested a prior step")
                # Result as-is
                case ('res', Iterable()):
                    stage_args.append(res)
                case ('res', _):
                    raise TypeError(f"{stage!r} requested an iterable and got non-iterable {res!r}")
                # Iterator
                case ('ix', Iterator()):
                    stage_args.append(res)
                case ('ix', Iterable()):
                    stage_args.append(iter(res))
                case ('ix', _):
                    raise TypeError(f"{stage!r} requested an iterator and got non-iterable {res!r}")
                # Sequence (list, tuple, str)
                case ('seq', Sequence()):
                    stage_args.append(res)
                case ('seq', Iterable()):
                    stage_args.append(list(res))
                case ('seq', _):
                    raise TypeError(f"{stage!r} requested a sequence and got non-iterable {res!r}")
                # MutableSequence (list)
                case ('mutseq', MutableSequence()):
                    stage_args.append(res)
                case ('mutseq', Iterable()):
                    stage_args.append(list(res))
                case ('mutseq', _):
                    raise TypeError(f"{stage!r} requested a mutable sequence and got non-iterable {res!r}")
                # Pipe
                case ('pipe', self.__class__()):
                    stage_args.append(res)
                case ('pipe', Iterable()):
                    stage_args.append(self.__class__(res))
                case ('pipe', _):
                    raise TypeError(f"{stage!r} requested a {self.__class__.__name__} and got non-iterable {res!r}")
                # Reference to bare Pipe class
                case ('cls', _):
                    stage_args.append(self.__class__)
                # Reference to the Pipe's RNG
                case ('rng', _):
                    stage_args.append(self._rng)
                # Unknown
                case _:
                    raise ValueError(f"{stage!r} requested an unknown parameter type: {stage_param!r}")
        return stage(*stage_args)

    ##############################################################
    # Random Number Generator (RNG) support

    @lazyattr
    def _rng(self):
        return SHARED_RANDOM

    def _set_rng(self, rng):
        match rng:
            case random.Random():
                self._rng = rng
            case _ if rng is _MISSING:
                del self._rng
            case 'shared':
                del self._rng
            case 'pseudo':
                self._rng = random.Random()
            case 'crypto':
                self._rng = random.SystemRandom()
            case str():
                raise ValueError(f"'set_rng' accepts string values of 'shared', 'pseudo', or 'crypto'; got {rng!r}")
            case _:
                raise TypeError(
                    "'set_rng' accepts strings or instances of `random.Random`;"
                    f" got {rng!r} of type {type(rng)!r} instead"
                )

    def set_rng(self, rng=_MISSING):
        """
        Clone this Pipe and set the new Pipe's random number generator to `rng`,
        which should be an instance of `random.Random`.

        If `rng` is not provided, it will be reset to the shared RNG instance
        used by default across Python.

        `rng` may optionally be one of the following strings, as a convenience:

        - `"shared"` to reset to the shared RNG instance
        - `"pseudo"` to create a new instance of `random.Random`
        - `"crypto"` to create a new instance of `random.SystemRandom`
        """
        p = self.clone()
        p._set_rng(rng)
        return p

    def seed_rng(self, seed=None):
        """
        Clone this Pipe and set the new Pipe's random number generator seed to
        `seed`.
        """
        p = self.clone()
        p._rng = p._rng.__class__(seed)
        return p

    ##############################################################
    # Clone an existing Pipe

    def clone(self):
        """
        Return a clone of this Pipe.

        It's usually unnecessary to call this explicitly unless building
        alternative Pipes from a template Pipe.

        Cloning a Pipe does *not* replace its RNG; you need to explicitly call
        {py:meth}`set_rng` or {py:meth}`seed_rng` for that.
        """
        p = self.__class__._with_source(self._source)
        p._steps = self._steps.copy()
        return p

    ##############################################################
    # Cache an existing Pipe's source

    def cache(self):
        """
        Force-evaluate this Pipe and return a new Pipe with the result
        as a new source.

        Existing steps are cleared from the new Pipe.
        """
        return self.__class__(self.list())

    ##############################################################
    # Create a new Pipe: alternate constructors

    @classonlymethod
    def items(cls, mapping, /):
        """
        {{pipe_source}} Yield the items (key-value pairs) of `mapping`.
        """
        def pipe_items():
            return mapping.items()
        return cls._with_source(pipe_items)

    @classonlymethod
    def iterdir(cls, path):
        """
        {{pipe_source}} Yield {py:class}`pathlib.Path` instances for the
        contents of the provided directory.

        See {py:meth}`pathlib.Path.iterdir`.
        """
        def pipe_iterdir():
            return pathlib.Path(path).iterdir()
        return cls._with_source(pipe_iterdir)

    @classonlymethod
    def iterfunc(cls, func, initial):
        """
        {{pipe_source}} Yield `initial`, then yield the results of successively
        calling `func` on the prior item yielded.

        Contrast with {py:meth}`Pipe.repeatfunc`, which simply calls `func` with
        supplied arguments forever.

        ```{ipython}

        In [1]: add1 = lambda x: x + 1

        In [1]: Pipe.iterfunc(add1, 13).take(5).list()
        Out[1]: [13, 14, 15, 16, 17]
        ```

        ```{marble}
        [ iterfunc(add1, 13) ]
        -13------------------|
        [      add1(13)      ]
        ----14---------------|
        [      add1(14)      ]
        -------15------------|
        [      add1(15)      ]
        ----------16---------|
        [      add1(16)      ]
        -13-14-15-16-17------>
        ```
        """
        def pipe_iterfunc():
            ret = initial
            yield ret
            while True:
                ret = func(ret)
                yield ret
        return cls._with_source(pipe_iterfunc)

    @classonlymethod
    def keys(cls, mapping, /):
        """
        {{pipe_source}} Yield the keys of `mapping`.
        """
        def pipe_keys():
            return mapping.keys()
        return cls._with_source(pipe_keys)

    @classonlymethod
    def randfloat(cls, a=0, b=1, /):
        """
        {{pipe_source}} Yield uniform random floats between `a` and `b`.

        If `a` and `b` are omitted, they default to `0` and `1`.

        `b` is not guaranteed to ever be a result (i.e., the range should be
        considered as `[a, b)`.

        Contrast with {py:meth}`Pipe.randrange`, which yields discrete integers
        within a closed range.
        """
        def pipe_randfloat(rng):
            if a == 0 and b == 1:
                while True:
                    yield rng.random()
            else:
                while True:
                    yield rng.uniform(a, b)
        return cls._with_source(pipe_randfloat)

    @classonlymethod
    def randrange(cls, *args, **kwargs):
        """
        {{pipe_source}} Yield random integers from a given range.

        Takes the same arguments as {py:meth}`Pipe.range`, and the possible
        results are the same as the full set of results there, except that
        `stop` must be specified.

        As with {py:meth}`Pipe.range`, `stop` is inclusive, not exclusive.

        ```{ipython}

        @suppress
        In [1]: import random; random.seed(0)

        In [1]: Pipe.randrange(1, 6).take(5).list()
        Out[1]: [4, 4, 1, 3, 5]
        ```

        ```{marble}
        [ randrange(1, 6) ]
        -4-4-1-3-5-------->
        ```

        Contrast with {py:meth}`Pipe.randfloat`, which yields floating-point
        numbers.
        """
        start, stop, step = check_slice_args('range', args, kwargs)
        def pipe_randrange(rng):
            while True:
                yield rng.randrange(start, stop + 1, step)
        return cls._with_source(pipe_randrange)

    @classonlymethod
    def range(cls, *args, **kwargs):
        """
        {{pipe_source}} Yield a range of numbers, *inclusive* of the upper
        bound.

        Accepts `start`, `stop`, and `step` as positional or keyword arguments.

        - `start` is the beginning of the range, inclusive.
        - `stop` is the end of the range, inclusive.
        - `step` is the increment (or, if negative, decrement).

        `start` defaults to 0, `stop` defaults to positive infinity, and `step`
        defaults to 1.

        As positional arguments:

        - `Pipe.range(stop)`
        - `Pipe.range(start, stop)`
        - `Pipe.range(start, stop, step)`

        Positional and keyword arguments can be mixed as long as they do not
        overlap; `Pipe.range` will raise a `TypeError` if they do.

        Note that `stop` is *inclusive*; see `Pipe.rangetil` for an exclusive
        `stop`.

        ```{ipython}

        In [1]: Pipe.range(10).list()
        Out[1]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        In [1]: Pipe.range(1, 10).list()
        Out[1]: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        ```
        """
        start, stop, step = check_slice_args('range', args, kwargs)
        if stop is None:
            def pipe_range():
                return itertools.count(start=start, step=step)
        else:
            stop = stop + (1 if step > 0 else -1)
            def pipe_range():
                return builtins.range(start, stop, step)
        return cls._with_source(pipe_range)

    @classonlymethod
    def rangetil(cls, *args, **kwargs):
        """
        {{pipe_source}} Yield a range of numbers, *exclusive* of the upper
        bound.

        Accepts `start`, `stop`, and `step` as positional or keyword arguments.

        - `start` is the beginning of the range, inclusive.
        - `stop` is the end of the range, exclusive.
        - `step` is the increment (or, if negative, decrement).

        `start` defaults to 0, `stop` defaults to positive infinity, and `step`
        defaults to 1.

        As positional arguments:

        - `Pipe.range(stop)`
        - `Pipe.range(start, stop)`
        - `Pipe.range(start, stop, step)`

        Positional and keyword arguments can be mixed as long as they do not
        overlap; `Pipe.range` will raise a `TypeError` if they do.

        Note that `stop` is *exclusive*; see `Pipe.range` for an inclusive
        `stop`.

        ```{ipython}

        In [1]: Pipe.rangetil(10).list()
        Out[1]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        In [1]: Pipe.rangetil(1, 10).list()
        Out[1]: [1, 2, 3, 4, 5, 6, 7, 8, 9]
        ```
        """
        start, stop, step = check_slice_args('rangetil', args, kwargs)
        if stop is None:
            def pipe_rangetil():
                return itertools.count(start=start, step=step)
        else:
            def pipe_rangetil():
                return builtins.range(start, stop, step)
        return cls._with_source(pipe_rangetil)

    @classonlymethod
    def repeat(cls, value, n=None):
        """
        {{pipe_source}} Yield `value` forever, or up to `n` times.

        `Pipe.repeat(x) => x, x, x, ...`

        See {py:meth}`Pipe.cycle` to repeat an iterable of values, instead.

        ```{ipython}

        In [1]: Pipe.repeat('meow').take(5).list()
        Out[1]: ['meow', 'meow', 'meow', 'meow', 'meow']
        ```

        ```{marble}
        [ repeat(a)          ]
        -a--a--a--a--a--a--a->
        ```
        """
        check_int_positive_or_none('n', n)
        src = itertools.repeat(value) if n is None else itertools.repeat(value, times=n)
        def pipe_repeat():
            return src
        return cls._with_source(pipe_repeat)

    @classonlymethod
    def repeatfunc(cls, func, *args, **kwargs):
        """
        {{pipe_source}} Yield the result of calls to `func` forever.

        Contrast with {py:meth}`Pipe.iterfunc`, which starts with a seed value
        and passes the previous result into the next function call, instead.

        ```{ipython}

        @suppress
        In [1]: import random; random.seed(0)

        In [1]: Pipe.repeatfunc(int, 6).take(5).list()
        Out[1]: [6, 6, 6, 6, 6]

        In [1]: Pipe.repeatfunc(dict, a=1, b=2).take(2).list()
        Out[1]: [{'a': 1, 'b': 2}, {'a': 1, 'b': 2}]

        In [1]: Pipe.repeatfunc(random.randint, 1, 6).take(5).list()
        Out[1]: [4, 4, 1, 3, 5]
        ```
        """
        def pipe_repeatfunc():
            while True:
                yield func(*args, **kwargs)
        return cls._with_source(pipe_repeatfunc)

    @classonlymethod
    def roll(cls, *args):
        """
        {{pipe_source}} Yield results of rolling dice.

        Accepts any of:
        - A string in `[NUM]d[SIZE]` notation, e.g., `3d6` for the result of
          rolling three six-sided dice.
        - A string in `[NUM]d[SIZE][+-][MOD]` notation, e.g., `3d6+2` for the
          result of rolling three six-sided dice and then adding 2 to that result.
        - A single integer, e.g., `6` for the result of rolling a single
          six-sided die.
        - Two integers, e.g., `3` and `6` for the result of rolling three six-sided
          dice.
        - Three integers, e.g., `3`, `6`, and `2` for the result of rolling
          three six-sided dice and then adding two to that result.

        ```{ipython}

        @suppress
        In [1]: import random; random.seed(0)

        In [1]: Pipe.roll(10).take(3).list()
        Out[1]: [7, 7, 1]

        In [1]: Pipe.roll(3, 6).take(6).list()
        Out[1]: [12, 11, 10, 10, 8, 14]

        In [1]: Pipe.roll('1d12+3').take(1).list()
        Out[1]: [13]
        ```
        """
        def pipe_roll(rng):
            dice = DiceRoll(*args, rng=rng)
            while True:
                yield dice.roll()
        return cls._with_source(pipe_roll)

    @classonlymethod
    def unfold(cls, func, seed):
        """
        {{pipe_source}} Yield items created from `func` and an initial `seed`.

        `func` must accept one argument and should return a pair `(value,
        feedback)`. `value` is yielded, `func(feedback)` is called, and this
        repeats until `func` returns a non-pair, which stops the iteration.

        This is the dual operation of {py:meth}`Pipe.fold`.

        ```{ipython}

        In [1]: build_pow2 = lambda x: (x, x * 2)

        In [1]: Pipe.unfold(build_pow2, 2).take(6).list()
        Out[1]: [2, 4, 8, 16, 32, 64]
        ```

        ```{marble}
        [ unfold(build_pow2, 2) ]
        -2---4---8---16--32--64->
        ```
        """
        def pipe_unfold():
            feedback = seed
            while True:
                match func(feedback):
                    case v, feedback:
                        yield v
                    case _:
                        return
        return cls._with_source(pipe_unfold)

    @classonlymethod
    def values(cls, mapping, /):
        """
        {{pipe_source}} Yield the values of `mapping`.
        """
        def pipe_values():
            return mapping.values()
        return cls._with_source(pipe_values)

    @classonlymethod
    def walk(
        cls, collection, /, *,
        full_path=False,
        leaves_only=False,
        strategy='DFS',
        max_depth=_MISSING,
        descend=_MISSING,
        children=_MISSING
        ):
        """
        {{pipe_source}} Yields the nodes of `collection` as `(parent, key,
        node)` tuples, where `parent[key] is node`.

        If `full_path` is true, instead yields tuples of `(parent, key, node)`
        tuples representing the full path to a given node.

        If `leaves_only` is true, only leaf nodes will be yielded.

        `strategy` must be one of `'DFS'` (depth-first search; default) or
        `'BFS'` (breadth-first search).

        If `max_depth` is provided as a positive integer, only descend up to the
        provided depth. `max_depth=1` would yield only the values directly
        within the collection, `max_depth=2` would yield those items as well as
        their children, and so on.

        If `descend` is a callable, only nodes for which `descend(node)` is true
        will be recursively descended into.

        If `children` is a callable, `children(node)` should return an iterable
        yielding child node `(key, value)` pairs for a given mapping `node`,
        which will be used instead of descending into every possible mapping and
        non-string sequence.

        If `children` is a string, as a convenience, it will yield only values
        of matching keys when mappings are encountered.
        """
        def pipe_walk():
            return walk_collection(
                collection,
                full_path=full_path,
                leaves_only=leaves_only,
                strategy=strategy,
                max_depth=max_depth,
                descend=descend,
                children=children,
            )
        return cls._with_source(pipe_walk)

    @classonlymethod
    def walkdir(cls, path, top_down=True, on_error=None, follow_symlinks=False):
        """
        {{pipe_source}} Yield tuples of `(dir, [*subdirs], [*files])` for
        recursively walking the provided path.

        `dir` is a {py:class}`pathlib.Path` instance, and `subdirs` and `files`
        are lists of string names.
        """
        # This was added in Python 3.12, so we implement it ourselves.
        # (We can't simply overlay `os.walk` and map all the results to
        # `pathlib.Path`, as the semantics for symlinks are different.)
        def pipe_walkdir():
            walker = os.walk(
                path,
                topdown=top_down,
                onerror=on_error,
                followlinks=follow_symlinks,
            )
            for dirpath, _, _ in walker:
                dp = pathlib.Path(dirpath)
                dn, fn = cls(dp.iterdir()).partition(lambda p: p.is_dir() and (follow_symlinks or not p.is_symlink()))
                yield (dp, [p.name for p in dn], [p.name for p in fn])
        return cls._with_source(pipe_walkdir)

    ##############################################################
    # Create a new Pipe OR modify an existing Pipe

    class cartesian_product(multimethod):
        """
        {{pipe_sourcestep}} Yield all possible ordered tuples of the items'
        elements.

        See {py:func}`itertools.product`.

        Contrast with {py:meth}`Pipe.product`, which is a sink that returns the
        result of multiplying the Pipe's items.
        """

        def _class(cls, *iterables, repeat=1):
            """
            {{pipe_source}} Yield all possible ordered tuples of the elements of
            *iterables*.
            """
            def pipe_cartesian_product():
                return itertools.product(*iterables, repeat=repeat)
            return cls._with_source(pipe_cartesian_product)

        def _instance(self, repeat=1):
            """
            {{pipe_step}} Yield all possible ordered tuples of the elements of this
            Pipe's items.
            """
            def pipe_cartesian_product(res):
                return itertools.product(*res, repeat=repeat)
            return self._with_step(pipe_cartesian_product)

    class chain(multimethod):
        """
        {{pipe_sourcestep}} Yield items from sub-iterables, in order.

        Contrast with {py:meth}`Pipe.interleave`.

        See {py:func}`itertools.chain`.

        ```{ipython}

        In [1]: Pipe.chain('abc', 'def', 'ghi').list()
        Out[1]: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        ```

        ```{marble}
        x---a-b-c-->
         y--d-e-f-->
          z-g-h-i-->
        [ chain()           ]
        --a-b-c-d-e-f-g-h-i->
        ```
        """

        def _class(cls, *iterables):
            """
            {{pipe_source}} Yield items from each of *iterables*, in order.
            """
            def pipe_chain():
                return itertools.chain(*iterables)
            return cls._with_source(pipe_chain)

        def _instance(self):
            """
            {{pipe_step}} Yield from each of this Pipe's items, in order.
            """
            def pipe_chain(res):
                return itertools.chain.from_iterable(res)
            return self._with_step(pipe_chain)

    class interleave(multimethod):
        """
        {{pipe_sourcestep}} Yield cross-wise from each sub-iterable.

        Contrast with {py:meth}`Pipe.chain`.

        :param collections.abc.Iterable iterables: Iterables to source from.
        :param bool fair: If true, stop after the shortest iterable is
        exhausted; otherwise, keep yielding until all are exhausted.

        ```{ipython}

        In [1]: Pipe.interleave('abc', 'def', 'ghi').list()
        Out[1]: ['a', 'd', 'g', 'b', 'e', 'h', 'c', 'f', 'i']
        ```

        ```{marble}
        x---a-b-c--|
         y--d-e-f--|
          z-g-h-i--|
        [ interleave()      ]
        --a-d-g-b-e-h-c-f-i->
        ```
        """

        def _class(cls, *iterables, fair=False):
            """
            {{pipe_source}} Yield cross-wise from each of `iterables`.
            """
            if fair:
                src = itertools.chain.from_iterable(zip(*iterables))
            else:
                src = (
                    x for x in itertools.chain.from_iterable(
                        itertools.zip_longest(*iterables, fillvalue=_MISSING)
                    )
                    if x is not _MISSING
                )
            def pipe_interleave():
                return src
            return cls._with_source(pipe_interleave)

        def _instance(self, fair=False):
            """
            {{pipe_step}} Yield cross-wise from each of this Pipe's items.
            """
            def pipe_interleave(res):
                if fair:
                    return itertools.chain.from_iterable(zip(*res))
                else:
                    return (
                        x for x in itertools.chain.from_iterable(
                            itertools.zip_longest(*res, fillvalue=_MISSING)
                        )
                        if x is not _MISSING
                    )
            return self._with_step(pipe_interleave)

    class struct_unpack(multimethod):
        """
        {{pipe_sourcestep}} Yield items unpacked from a buffer according to a
        format string.

        See {external:py:func}`struct.unpack`.
        """
        def _class(cls, format_, buffer, /):
            """
            {{pipe_source}} Yield tuples of unpacked bytes from `buffer` using
            `format`.
            """
            def pipe_struct_unpack():
                return struct.iter_unpack(format_, buffer)
            return cls._with_source(pipe_struct_unpack)

        def _instance(self, format_, /):
            """
            {{pipe_step}} Yield tuples of unpacked bytes from the Pipe's items using
            `format`.
            """
            def pipe_struct_unpack(res):
                for item in res:
                    yield struct.unpack(format_, item)
            return self._with_step(pipe_struct_unpack)

    class zip(multimethod):
        """
        {{pipe_sourcestep}} Zip all input items together and yield the resulting
        tuples.

        The yielded items (possibly excepting the final one) will each have a
        length equal to `n`, where `n` is the number of input sub-iterables
        being processed.

        Each element of the yielded items will be taken from the input
        sub-iterable matching its index in the tuple.

        Passing a zipped iterable back into {py:meth}`Pipe.zip` is equivalent to
        an unzip.

        By default, the length of the shortest output item determines how many
        total items will be yielded. Longer items will be silently truncated.

        If `fillvalue` is provided, the length of the *longest* item will
        instead determine how many total items will be yielded, and shorter
        items will be padded using `fillvalue`.

        If `strict` is true, all input items must be the same length, or a
        `ValueError` will be raised.

        See {external:py:func}`zip` and {py:func}`itertools.zip_longest`.
        """

        def _class(cls, *iterables, fillvalue=_MISSING, strict=False):
            """
            {{pipe_source}} Yield the results of zipping together *iterables*.
            """
            if fillvalue is not _MISSING:
                if strict:
                    raise TypeError("'fillvalue' and 'strict' are mutually exclusive")
                def pipe_zip():
                    return itertools.zip_longest(*iterables, fillvalue=fillvalue)
            else:
                def pipe_zip():
                    return builtins.zip(*iterables, strict=strict)
            return cls._with_source(pipe_zip)

        def _instance(self, fillvalue=_MISSING, strict=False):
            """
            {{pipe_step}} Yield the results of zipping together each of this Pipe's
            items.

            The source must be finite, and it will be exhausted upon evaluation.
            """
            if fillvalue is not _MISSING:
                if strict:
                    raise TypeError("'fillvalue' and 'strict' are mutually exclusive")
                def pipe_zip(res):
                    return itertools.zip_longest(*res, fillvalue=fillvalue)
            else:
                def pipe_zip(res):
                    return builtins.zip(*res, strict=strict)
            return self._with_step(pipe_zip)

    ##############################################################
    # Modify an existing Pipe: intermediate steps

    def append(self, *items):
        """
        {{pipe_step}} Yield each of the source's items, then yield each of `items`.

        Compare with {py:meth}`Pipe.prepend`, which yields the `items` first,
        and then yields the source's items.
        """
        def pipe_append(res):
            return itertools.chain(res, items)
        return self._with_step(pipe_append)

    def broadcast(self, n):
        """
        {{pipe_step}} Yield tuples containing each item repeated `n` times.

        Equivalent to yielding `(item,) * n` for each item.

        ```{marble}
        -2----------------->
        [ broadcast(2)     ]
        -2,2----2,2----2,2->
        ```
        """
        def pipe_broadcast(res):
            for v in res:
                yield (v,) * n
        return self._with_step(pipe_broadcast)

    def broadmap(self, *funcs):
        """
        {{pipe_step}} Yield tuples containing each of `funcs` applied to `item`.

        Equivalent to yielding `tuple(func(item) for func in funcs)` for each
        item.

        Compare with {py:meth}`Pipe.dictmap`.

        ```{ipython}

        In [1]: Pipe([1, 2, 3]).broadmap(str, lambda x: x * x).list()
        Out[1]: [('1', 1), ('2', 4), ('3', 9)]
        ```
        """
        def pipe_broadmap(res):
            for v in res:
                yield tuple(func(v) for func in funcs)
        return self._with_step(pipe_broadmap)

    def chunk(self, n, *, step=_MISSING, fillvalue=_MISSING, fair=False):
        """
        {{pipe_step}} Yield source items chunked into size-`n` tuples.

        `step` controls where each chunk starts at, just like {py:meth}`slice`,
        and defaults to `n`. A `step` smaller than `n` will yield sliding
        windows, and a `step` larger than `n` will skip source items.

        If `fillvalue` is provided, any final chunk smaller than `n` will be
        padded using `fillvalue`.

        If `fair` is true and the final chunk is smaller than `n`, it will be
        dropped, otherwise it will be yielded as-is.

        ```{ipython}

        # Standard chunks:
        In [1]: Pipe('abcdef').chunk(2).list()
        Out[1]: [('a', 'b'), ('c', 'd'), ('e', 'f')]

        # Equivalent, since step defaults to n
        In [1]: Pipe('abcdef').chunk(2, step=2).list()
        Out[1]: [('a', 'b'), ('c', 'd'), ('e', 'f')]

        In [1]: Pipe('abcdef').chunk(3).list()
        Out[1]: [('a', 'b', 'c'), ('d', 'e', 'f')]

        In [1]: Pipe('abcde').chunk(2).list()
        Out[1]: [('a', 'b'), ('c', 'd'), ('e',)]

        In [1]: Pipe('abcde').chunk(2, fair=True).list()
        Out[1]: [('a', 'b'), ('c', 'd')]

        In [1]: Pipe('abcde').chunk(2, fillvalue='x').list()
        Out[1]: [('a', 'b'), ('c', 'd'), ('e', 'x')]

        In [1]: Pipe('abcde').chunk(3, fillvalue='x').list()
        Out[1]: [('a', 'b', 'c'), ('d', 'e', 'x')]

        In [1]: Pipe('abcde').chunk(3).list()
        Out[1]: [('a', 'b', 'c'), ('d', 'e')]

        In [1]: Pipe('abcde').chunk(3, fair=True).list()
        Out[1]: [('a', 'b', 'c')]

        # Sliding windows
        In [1]: Pipe('abc').chunk(2, step=1).list()
        Out[1]: [('a', 'b'), ('b', 'c')]

        In [1]: Pipe('abcde').chunk(2, step=1).list()
        Out[1]: [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e')]

        In [1]: Pipe('abcde').chunk(3, step=1).list()
        Out[1]: [('a', 'b', 'c'), ('b', 'c', 'd'), ('c', 'd', 'e')]

        In [1]: Pipe('abc').chunk(2, step=3).list()
        Out[1]: [('a', 'b')]

        In [1]: Pipe('abcd').chunk(2, step=3).list()
        Out[1]: [('a', 'b'), ('d',)]

        In [1]: Pipe('abcd').chunk(2, step=3, fillvalue='x').list()
        Out[1]: [('a', 'b'), ('d', 'x')]

        In [1]: Pipe('abcde').chunk(3, step=4).list()
        Out[1]: [('a', 'b', 'c'), ('e',)]

        In [1]: Pipe('abcde').chunk(3, step=4, fillvalue='x').list()
        Out[1]: [('a', 'b', 'c'), ('e', 'x', 'x')]
        ```
        """
        if fillvalue is not _MISSING and fair:
            raise TypeError("'fillvalue' and 'fair' are mutually exclusive")
        check_int_positive('n', n)
        step = replace(_MISSING, n, step)
        check_int_positive('step', step)
        def pipe_chunk(ix):
            chunk = collections.deque(maxlen=n)
            while True:
                try:
                    v = next(ix)
                except StopIteration:
                    break
                else:
                    chunk.append(v)
                    if len(chunk) < n:
                        continue
                    yield tuple(chunk)
                    if step > 1:
                        try:
                            for _ in range(step):
                                if chunk:
                                    chunk.popleft()
                                else:
                                    next(ix)
                        except StopIteration:
                            break
            final_chunk_len = len(chunk)
            if 0 < final_chunk_len < n:
                if fair:
                    return
                if fillvalue is not _MISSING:
                    chunk.extend((fillvalue,) * (n - final_chunk_len))
                yield tuple(chunk)
        return self._with_step(pipe_chunk)

    def chunkby(self, key):
        """
        {{pipe_step}} Yield tuples of adjacent elements grouped by `key`.

        Contrast with {py:meth}`Pipe.groupby`, which is a sink that groups
        elements into a `dict` by a key function regardless of their position.
        """
        def pipe_chunkby(res):
            for _, g in itertools.groupby(res, key):
                yield tuple(g)
        return self._with_step(pipe_chunkby)

    def clamp(self, *args, min=MINIMUM, max=MAXIMUM):
        """
        {{pipe_step} Yield values clamped between `min` and `max`.

        - If `min` is provided, any items less than `min` will yield `min`
          instead.
        - If `max` is provided, any items greater than `max` will yield `max`
          instead.

        Accepts `min` and `max` as either positional or keyword arguments. If
        provided as positional arguments, *both* `min` and `max` must be
        specified, and *must not* be specified as keyword arguments.
        """
        match args:
            case (_, _) if min is not MINIMUM or max is not MAXIMUM:
                raise TypeError("Cannot specify both positional and keyword arguments for 'min' or 'max'")
            case (arg_min, arg_max):
                pass
            case () if min is MINIMUM and max is MAXIMUM:
                raise TypeError("At least one of 'min' or 'max' must be specified")
            case ():
                arg_min = min
                arg_max = max
            case _:
                raise TypeError("Either zero or two positional arguments must be provided")
        def pipe_clamp(res):
            for item in res:
                yield builtins.min(builtins.max(item, arg_min), arg_max)
        return self._with_step(pipe_clamp)

    def combinations(self, k, *, replacement=False):
        """
        {{pipe_step}} Yield all size-`k` combinations of the source items.

        `k` can also be provided as `(k_min, k_max)`, yielding combinations in
        ascending order of size between `k_min` and `k_max`.

        If `replacement` is true, source items may be repeated within a single
        combination.

        Combinations are unique without respect to ordering; when ordering
        matters, use {py:meth}`Pipe.permutations` instead.

        See {py:func}`itertools.combinations` and
        {py:func}`itertools.combinations_with_replacement`.
        """
        k_min, k_max = check_k_args('k', k, default=_POOL)
        func = itertools.combinations_with_replacement if replacement else itertools.combinations
        def pipe_combinations(seq):
            i_min, i_max = replace(_POOL, len(seq), k_min, k_max)
            for i in range(i_min, i_max + 1):
                yield from func(seq, i)
        return self._with_step(pipe_combinations)

    def concat(self, *iterables):
        """
        {{pipe_step}} Yield all items from the source, then all items from each
        of `iterables`, in order.

        Compare with {py:meth}`Pipe.precat`, which yields from the provided
        iterables first, and then yields the source's items.

        Contrast with {py:meth}`Pipe.chain`, which treats each source item as a
        sub-iterable to yield items from.
        """
        def pipe_concat(res):
            return itertools.chain(res, *iterables)
        return self._with_step(pipe_concat)

    def cycle(self, n=None):
        """
        {{pipe_step}} Yield items from the source in a loop, either forever or `n`
        times.

        Dispatches to {py:func}`itertools.cycle` if `n` is not provided.

        See {py:meth}`Pipe.repeat` to repeat a single value, instead.

        ```{marble}
        -1-2-3-|
        [ cycle()          ]
        -1-2-3-1-2-3-1-2-3->
        ```
        """
        check_int_positive_or_none('n', n)
        match n:
            case None:
                def pipe_cycle(res):
                    return itertools.cycle(res)
            case 1:
                def pipe_cycle(ix):
                    return ix
            case _:
                def pipe_cycle(res):
                    cache = []
                    for item in res:
                        yield item
                        cache.append(item)
                    for _ in range(n - 1):
                        yield from cache
        return self._with_step(pipe_cycle)

    def debug(self, fmt='{!r}', /):
        """
        {{pipe_step}} For each item, call `print(fmt.format(item))` as a side effect
        and yield the item unchanged.

        `fmt` defaults to `'{!r}'`.
        """
        def pipe_debug(res):
            for item in res:
                print(fmt.format(item))
                yield item
        return self._with_step(pipe_debug)

    def depeat(self, *, key=_MISSING):
        """
        {{pipe_step}} Yield items, but skip consecutive duplicates.

        If `key` is provided, compare `key(item)` instead of `item`.

        Contrast with {py:meth}`Pipe.unique`.

        ```{ipython}

        In [1]: Pipe('abbcccacbba').depeat().list()
        Out[1]: ['a', 'b', 'c', 'a', 'c', 'b', 'a']
        ```

        ```{marble}
        -a-b-b-c-c-c-a-c-b-b-a->
        [ depeat()             ]
        -a-b---c-----a-c-b---a->
        ```
        """
        match key:
            case Callable() | Sentinel():
                pass
            case _:
                raise TypeError("'key' must be a callable")
        last = _MISSING
        if key is not _MISSING:
            def pipe_depeat(res):
                nonlocal last
                for v in res:
                    v_keyed = key(v)
                    if v_keyed is not last:
                        yield v
                        last = v_keyed
        else:
            def pipe_depeat(res):
                nonlocal last
                for v in res:
                    if v is not last:
                        yield v
                        last = v
        return self._with_step(pipe_depeat)

    def dictmap(self, template=_MISSING, **kwargs):
        """
        {{pipe_step}} Yield dicts that are copies of `template`, but with the
        values replaced with the result of calling each value with each input
        item.

        Alternately, `**kwargs` can be used to provide key/value pairs directly.

        Equivalent to yielding, for each item:

        `{k: v(item) for item in ix for k, v in template.items()}`

        Compare with {py:meth}`Pipe.broadmap`.

        ```{ipython}

        # Equivalent:
        In [1]: Pipe([1, 2, 3]).dictmap({'a': str, 'b': lambda x: x * x}).list()
        Out[1]: [{'a': '1', 'b': 1}, {'a': '2', 'b': 4}, {'a': '3', 'b': 9}]

        In [1]: Pipe([1, 2, 3]).dictmap(a=str, b=lambda x: x * x).list()
        Out[1]: [{'a': '1', 'b': 1}, {'a': '2', 'b': 4}, {'a': '3', 'b': 9}]
        ```
        """
        template = replace(_MISSING, {}, template)
        template.update(kwargs)
        def pipe_dictmap(res):
            for item in res:
                yield {k: v(item) for k, v in template.items()}
        return self._with_step(pipe_dictmap)

    def drop(self, n=_MISSING):
        """
        {{pipe_step}} Skip the first `n` items and yield the rest.

        ```{marble}
        -1-2-3-4-5-6-7-8-9->
        [ drop(4)          ]
        ---------5-6-7-8-9->
        ```
        """
        check_int_zero_or_positive('n', n)
        def pipe_drop(res):
            return itertools.islice(res, n, None)
        return self._with_step(pipe_drop)

    def dropwhile(self, pred):
        """
        {{pipe_step}} Skip items until `pred(item)` is true, then yield that
        item and all following items without testing them.

        See {py:func}`itertools.dropwhile`.
        """
        def pipe_dropwhile(res):
            return itertools.dropwhile(pred, res)
        return self._with_step(pipe_dropwhile)

    def enumerate(self, start=0):
        """
        {{pipe_step}} Yield `(index, item)` pairs for each item.

        See {external:py:func}`enumerate`.

        Contrast with {py:meth}`Pipe.enumerate_info`.
        """
        def pipe_enumerate(res):
            return builtins.enumerate(res, start=start)
        return self._with_step(pipe_enumerate)

    def enumerate_info(self, start=0):
        """
        {{pipe_step}} Like `enumerate` but yield `(info, value)` pairs where `info` is an
        object with the following attributes:

        - `.i`/`.index`: The current count value, beginning at `start`.

        - `.is_first`: Whether this is the first item.

        - `.is_last`: Whether this is the last item.

        Contrast with {py:meth}`Pipe.enumerate`.
        """
        check_int('start', start)
        def pipe_enumerate_info(pipe):
            c = start
            is_first = True
            for value, next_value in pipe.peek():
                is_last = next_value is self.peek.END
                yield (EnumerateInfo(c, is_first=is_first, is_last=is_last), value)
                is_first = False
                c += 1
        return self._with_step(pipe_enumerate_info)

    def filter(self, func=None):
        """
        {{pipe_step}} Yield items for which `func(item)` is true.

        See {external:py:func}`filter`.
        """
        def pipe_filter(res):
            return builtins.filter(func, res)
        return self._with_step(pipe_filter)

    def flatten(self, levels=_MISSING):
        """
        {{pipe_step}} Recursively yield items from within encountered sequences
        and iterators.

        `str`, `bytes`, and `bytearray` objects are special-cased and yielded
        as-is, despite being sequences.

        If `levels` is provided as a positive integer, only remove that many
        levels of nesting.

        ```{ipython}

        In [1]: P(['a', ['b', ['c', ['d', ['e']]]]]).flatten().list()
        Out[1]: ['a', 'b', 'c', 'd', 'e']

        In [1]: P(['a', ['b', ['c', ['d', ['e']]]]]).flatten(levels=1).list()
        Out[1]: ['a', 'b', ['c', ['d', ['e']]]]

        In [1]: P(['a', ['b', ['c', ['d', ['e']]]]]).flatten(levels=2).list()
        Out[1]: ['a', 'b', 'c', ['d', ['e']]]
        ```
        """
        def pipe_flatten(res):
            return flatten(res, levels=levels)
        return self._with_step(pipe_flatten)

    def intersperse(self, sep, n=1, fillvalue=_MISSING):
        """
        {{pipe_step}} Yield spans of `n` items with `sep` between them.

        If `fillvalue` is provided and the final span is shorter than `n`, pad
        it with `fillvalue`.
        """
        check_int_positive('n', n)
        def pipe_intersperse(ix):
            yield from itertools.islice(ix, n)
            chunk = collections.deque(maxlen=n)
            while True:
                try:
                    v = next(ix)
                except StopIteration:
                    break
                else:
                    chunk.append(v)
                    if len(chunk) < n:
                        continue
                    yield sep
                    yield from chunk
                    chunk.clear()
            final_chunk_len = len(chunk)
            if 0 < final_chunk_len < n:
                yield sep
                if fillvalue is not _MISSING:
                    chunk.extend((fillvalue,) * (n - final_chunk_len))
                yield from chunk
        return self._with_step(pipe_intersperse)

    def label(self, *keys, fillvalue=_MISSING, strict=False):
        """
        {{pipe_step}} Yield dicts representing each of `keys` zipped with each item.
        """
        def pipe_label(res, cls):
            for item in res:
                yield cls.zip(keys, item, fillvalue=fillvalue, strict=strict).dict()
        return self._with_step(pipe_label)

    def map(self, func):
        """
        {{pipe_step}} Yield each item mapped through `func`.

        See {external:py:func}`map`.
        """
        def pipe_map(res):
            return builtins.map(func, res)
        return self._with_step(pipe_map)

    def peek(self):
        """
        {{pipe_step}} Yield tuples of `(value, next_value)`.

        `next_value` is {py:data}`END` (bound to {py:attr}`Pipe.peek.END` as
        well) if the current value is the last one.
        """
        def pipe_peek(ix):
            try:
                last_item = next(ix)
            except StopIteration:
                return
            while True:
                try:
                    next_item = next(ix)
                except StopIteration:
                    yield (last_item, END)
                    return
                else:
                    yield (last_item, next_item)
                    last_item = next_item
        return self._with_step(pipe_peek)
    peek.END = END

    def permutations(self, k=None):
        """
        {{pipe_step}} Yield all size-`k` permutations of the source.

        `k` can also be provided as `(k_min, k_max)`, yielding permutations in
        ascending order of size between `k_min` and `k_max`.

        If `k` is `None` it defaults to the total number of items in the source.

        The source must be finite, and it will be exhausted upon
        evaluation.

        See {py:func}`itertools.permutations`.
        """
        k_min, k_max = check_k_args('k', k, default=_POOL)
        def pipe_permutations(seq):
            i_min, i_max = replace(_POOL, len(seq), k_min, k_max)
            for i in range(i_min, i_max + 1):
                yield from itertools.permutations(seq, i)
        return self._with_step(pipe_permutations)

    def precat(self, *iterables):
        """
        {{pipe_step}} Yield all items from each of `iterables` in order, and
        then yield each of the source's items.

        Compare with {py:meth}`Pipe.concat`, which yields the source's items
        first, and then yields from each of iterables.

        Contrast with {py:meth}`Pipe.chain`, which treats each source item as a
        sub-iterable to yield items from.
        """
        def pipe_precat(res):
            return itertools.chain(*iterables, res)
        return self._with_step(pipe_precat)

    def prepend(self, *items):
        """
        {{pipe_step}} Yield each of `items`, and then yield each of the source's
        items.

        Compare with {py:meth}`Pipe.append`, which yields the source's items
        first, and then yields the `items`.
        """
        def pipe_prepend(res):
            return itertools.chain(items, res)
        return self._with_step(pipe_prepend)

    def reject(self, func=None):
        """
        {{pipe_step}} Yield items for which `func(item)` is false.

        See {external:py:func}`itertools.filterfalse`.
        """
        def pipe_reject(res):
            return itertools.filterfalse(func, res)
        return self._with_step(pipe_reject)

    def remap(self, *args, **kwargs):
        """
        {{pipe_step}} Yield transformed mappings using the supplied expressions.

        Each input must be a mapping.

        By default, all key-value pairs are dropped from the output mapping unless
        explicitly selected. Pass `...` (see below) to toggle this behavior.

        For each `arg` in `args`, input mapping `input`, and output mapping
        `output`:

        - If `arg` is an {py:data}`Ellipsis` (`...`), `remap` will keep key-value
          pairs by default in the output mapping, instead of dropping them.
        - If `arg` is a string: `output[arg] = input[arg]`
        - If `arg` is a tuple `(key, default)`: `output[key] = input.get(key,
          default)`
        - If `arg` is a callable: `output.update(arg(input))`
        - If `arg` is a mapping, for each `key`-`value` pair of `arg`:
          - If `key in input`:
            - If `value` is a string: `output[key] = input[value]`
            - If `value` is a tuple `(value_key, default)`: `output[key] =
              input.get(value_key, default)`
            - If `value` is {py:attr}`Pipe.KEEP`: `output[key] = input[key]`
            - If `value` is {py:attr}`Pipe.DROP`, the output mapping will *not*
              include that key-value pair from the input mapping.
            - If `value` is a callable, for `value_ret = value(input[key])`:
              - If `value_ret` is {py:attr}`Pipe.KEEP` or {py:attr}`Pipe.DROP`, it will
                be handled the same way as above.
              - If `value_ret` is any other value: `output[key] = value_ret`
            - If `value` is of any other type, raise a {py:exc}`TypeError`.
          - If `key not in input`:
            - If `value` is {py:attr}`Pipe.KEEP`, raise a {py:exc}`TypeError` (because
              there's no existing key to keep).
            - If `value` is {py:attr}`Pipe.DROP`, no action will be taken (because
              there's no existing key to drop).
            - If `value` is a callable, for `value_ret = value(input)`:
              - If `value_ret` is {py:attr}`Pipe.KEEP`, raise a {py:exc}`TypeError`
                (because there's no existing key to keep).
              - If `value_ret` is {py:attr}`Pipe.DROP`, no action will be taken (because
                there's no existing key to drop).
              - If `value_ret` is anything else: `output[key] = value_ret`
            - If `value` is of any other kind, raise a {py:exc}`TypeError`.
        - If `arg` is of any other type, raise a {py:exc}`TypeError`.

        For any `kwargs` provided, act as if `kwargs` was a mapping passed as an
        `arg` above.
        """
        p = self.clone()
        def pipe_remap(res):
            keep_by_default = False
            for item in res:
                if not isinstance(item, Mapping):
                    raise TypeError(f"Input item was not a mapping; got {item!r} of type {type(item)!r}")
                ret = {}
                dropped_keys = set()
                def _mapping_handler(mapping):
                    for m_k, m_v in mapping.items():
                        match m_v:
                            case _ if m_v is DROP:
                                dropped_keys.add(m_k)
                            case _ if m_v is KEEP:
                                ret[m_k] = item[m_k]
                            case str():
                                ret[m_k] = item[m_v]
                            case (str() as key, default):
                                ret[m_k] = item.get(key, default)
                            case Callable():
                                try:
                                    item_v = item[m_k]
                                except KeyError:
                                    item_v = m_v(item)
                                    match item_v:
                                        case _ if item_v is KEEP:
                                            raise TypeError(
                                                f"KEEP cannot be returned for key {m_k!r}"
                                                " which is not present in the original item"
                                            )
                                        case _ if item_v is DROP:
                                            pass
                                        case _:
                                            ret[m_k] = item_v
                                else:
                                    match (item_v_ret := m_v(item_v)):
                                        case _ if item_v_ret is DROP:
                                            dropped_keys.add(m_k)
                                        case _ if item_v_ret is KEEP:
                                            ret[m_k] = item_v
                                        case _:
                                            ret[m_k] = item_v_ret
                            case _:
                                raise TypeError(
                                    f"Invalid type for remap key {m_k!r}: {m_v!r} of type {type(m_v)!r}"
                                )
                for arg in args:
                    match arg:
                        case EllipsisType():
                            keep_by_default = True
                        case str():
                            ret[arg] = item[arg]
                        case (str() as key, default):
                            ret[key] = item.get(key, default)
                        case Callable():
                            ret.update(arg(item))
                        case Mapping():
                            _mapping_handler(arg)
                        case _:
                            raise TypeError(f"Invalid type for remap arg {arg!r} of type {type(arg)!r}")
                _mapping_handler(kwargs)
                if keep_by_default:
                    ret.update({k: item[k] for k in (item.keys() - ret.keys() - dropped_keys)})
                yield ret
        p._steps.append(pipe_remap)
        return p

    def reverse(self):
        """
        {{pipe_step}} Yield the source values in reversed order.

        The source must be finite, and it will be exhausted upon
        evaluation.

        See {external:py:func}`reversed`.
        """
        def pipe_reverse(seq):
            return reversed(seq)
        return self._with_step(pipe_reverse)

    def sample(self, k=None, *, replacement=False):
        """
        {{pipe_step}} Yield a `k` length list of randomly chosen source values.

        `k` can also be provided as `(k_min, k_max)`, causing the size of each
        sample to randomly vary between `k_min` and `k_max`.

        If `k` is `None` it defaults to the total number of items in the source.

        If `replacement` is true, the selection will be done with replacement,
        meaning a value may be yielded more times in a sample than it shows up
        in the source.

        If `replacement` is false, this behaves effectively the same as a random
        permutation generator; compare with {py:meth}`Pipe.permutations`.

        The source must be finite, and it will be cached and exhausted upon
        evaluation.

        See {external:py:func}`random.sample`.
        """
        k_min, k_max = check_k_args('k', k, default=_POOL)
        def pipe_sample(seq, rng):
            func = rng.choices if replacement else rng.sample
            i_min, i_max = replace(_POOL, len(seq), k_min, k_max)
            while True:
                i = i_min if i_min == i_max else rng.randint(i_min, i_max)
                yield tuple(func(seq, k=i))
        return self._with_step(pipe_sample)

    def scan(self, func, *, initial=None):
        """
        {{pipe_step}} Yield accumulated results of applying binary `func` to the source items.

        Akin to a `fold` that yields each intermediate result.

        See {py:func}`itertools.accumulate`.
        """
        def pipe_scan(res):
            return itertools.accumulate(res, func, initial=initial)
        return self._with_step(pipe_scan)

    def slice(self, *args, **kwargs):
        """
        {{pipe_step}} Yield the sliced range of items.

        ```
        .slice(stop) --> source[:stop]
        .slice(start, stop[, step]) --> source[start:stop:step]
        ```

        See {py:func}`itertools.islice`.
        """
        start, stop, step = check_slice_args('slice', args, kwargs)
        def pipe_slice(res):
            return itertools.islice(res, start, stop, step)
        return self._with_step(pipe_slice)

    def sort(self, *, key=None, reverse=False):
        """
        {{pipe_step}} Yield the source items, sorted.

        The source must be finite, and it will be exhausted upon
        evaluation.

        `key` can either be provided as a callable, or a string

        See {external:py:func}`sorted`.
        """
        def pipe_sort(res):
            return sorted(res, key=key, reverse=reverse)
        return self._with_step(pipe_sort)

    def split(self, *, index=_MISSING, value=_MISSING):
        """
        {{pipe_step}} Yield lists representing the source items split at certain
        points.

        For `index`:

        - If `index` is an `int`, create a new split before the item with the
          matching index.
        - If `index` is a sequence of `int`, create a new split before each
          matching item index.
        - If `index` is a callable, it will be called as `index(i)` for each item
          index `i`. If it returns true, a new split will be started before the
          item.

        For `value`:

        - If `value` is a callable, it will be called as `value(item)` for each
          item. If it returns true, a new split will be started before the item.
        - If `value` is a sequence of objects, create a new split if `item in
          value`.
        - If `value` is any other object, a new split will be started if `item ==
          value`.
        """
        def pipe_split(res):
            target = []
            last = None
            match index:
                case _ if index is _MISSING:
                    split_indexes = set()
                case int():
                    split_indexes = {index}
                case NonStrSequence():
                    split_indexes = set(index)
                case Set():
                    split_indexes = index
                case Callable():
                    split_indexes = set()
                case _:
                    raise TypeError(f"Unknown 'index' {index!r} of type {type(index)!r}")
            match value:
                case _ if value is _MISSING:
                    split_values = set()
                case NonStrSequence():
                    split_values = set(value)
                case Set():
                    split_values = value
                case Callable():
                    split_values = set()
                case _:
                    split_values = {value}
            for i, v in enumerate(res):
                should_split = (
                    (i in split_indexes)
                    or (v in split_values)
                    or (callable(index) and index(i))
                    or (callable(value) and value(v))
                )
                if should_split:
                    if target:
                        yield target
                    target = []
                target.append(v)
            if target:
                yield target
        return self._with_step(pipe_split)

    def sponge(self, sink):
        """
        {{pipe_step}} Evaluate the Pipe up to this point using `sink`, and
        continue the pipe yielding its single result.

        `sink` can either be a `Pipe` sink method called as a classmethod (e.g.,
        `Pipe.sum()`), or any function that accepts an iterable and returns a
        single result (e.g., `sum`).
        """
        def pipe_sponge(res):
            yield sink(res)
        return self._with_step(pipe_sponge)

    def starmap(self, func):
        """
        {{pipe_step}} For each item, yield `func(*item)`.

        See {py:func}`itertools.starmap`.
        """
        def pipe_starmap(res):
            return itertools.starmap(func, res)
        return self._with_step(pipe_starmap)

    def take(self, n):
        """
        {{pipe_step}} Yield the first `n` items and skip the rest.

        ```{marble}
        -1-2-3-4-5-6-7-8-9->
        [ take(4)          ]
        -1-2-3-4-|
        ```
        """
        check_int_zero_or_positive('n', n)
        def pipe_take(res):
            return itertools.islice(res, None, n)
        return self._with_step(pipe_take)

    def takewhile(self, pred):
        """
        {{pipe_step}} Yield items until `pred(item)` is false, then skip that
        item and all following items without testing them.

        See {py:func}`itertools.takewhile`.
        """
        def pipe_takewhile(res):
            return itertools.takewhile(pred, res)
        return self._with_step(pipe_takewhile)

    def tap(self, func):
        """
        {{pipe_step}} For each item, call `func(item)` as a side effect
        and yield the item unchanged.
        """
        def pipe_tap(res):
            for item in res:
                func(item)
                yield item
        return self._with_step(pipe_tap)

    def unique(self, /, key=_MISSING):
        """
        {{pipe_step}} Yield only items that have not been yielded already.

        Contrast with {py:meth}`Pipe.depeat`

        ```{ipython}

        In [1]: Pipe('abbcccacbba').unique().list()
        Out[1]: ['a', 'b', 'c']
        ```

        ```{marble}
        -a-b-b-c-c-c-a-c-b-d-a->
        [ unique()             ]
        -a-b---c-----------d--->
        ```
        """
        match key:
            case Callable() | Sentinel():
                pass
            case _:
                raise TypeError("'key' must be a callable")
        seen = Seen()
        if key is not _MISSING:
            def pipe_unique(res):
                for v in res:
                    v_keyed = key(v)
                    if v_keyed not in seen:
                        yield v
        else:
            def pipe_unique(res):
                for v in res:
                    if v not in seen:
                        yield v
        return self._with_step(pipe_unique)

    ##############################################################
    # Sinks: non-container results

    @partialclassmethod
    def all(self, pred=_MISSING):
        """
        {{pipe_sink}} Return `True` if `pred(item)` is true for all items.

        If `pred` is missing, `bool(item)` will be used instead.

        Contrast with {py:meth}`Pipe.any` and {py:meth}`Pipe.none`.

        See {external:py:func}`all`.
        """
        def pipe_all(res):
            if pred is _MISSING:
                return builtins.all(res)
            for item in res:
                if not pred(item):
                    return False
            return True
        return self._evaluate(sink=pipe_all)

    @partialclassmethod
    def any(self, pred=_MISSING):
        """
        {{pipe_sink}} Return `True` if `pred(item)` is true for any item.

        If `pred` is missing, `bool(item)` will be used instead.

        Contrast with {py:meth}`Pipe.all` and {py:meth}`Pipe.none`.

        See {external:py:func}`any`.
        """
        def pipe_any(res):
            if pred is _MISSING:
                return builtins.any(res)
            for item in res:
                if pred(item):
                    return True
            return False
        return self._evaluate(sink=pipe_any)

    @partialclassmethod
    def contains(self, value):
        """
        {{pipe_sink}} Return `True` if any of this Pipe's items equals `value`.
        """
        def pipe_contains(res):
            match res:
                case Container():
                    return value in res
                case _:
                    return builtins.any(item == value for item in res)
        return self._evaluate(sink=pipe_contains)

    @partialclassmethod
    def count(self):
        """
        {{pipe_sink}} Return the number of values in this Pipe.
        """
        def pipe_count(res):
            match res:
                case Sized():
                    return len(res)
                case _:
                    return builtins.sum(1 for value in res)
        return self._evaluate(sink=pipe_count)

    @partialclassmethod
    def equal(self, default=_MISSING):
        """
        {{pipe_sink}} Return `True` if all items compare equal (`a == b`).

        If there are no items, return `default` if it is provided; otherwise,
        raise `ValueError`.

        Contrast with {py:meth}`Pipe.identical`, returns true of all items
        compare equal (`a is b`).
        """
        def pipe_equal(ix):
            try:
                first_item = next(ix)
            except StopIteration as exc:
                if default is _MISSING:
                    raise ValueError("equal applied to empty iterable") from exc
                return default
            for item in ix:
                if item != first_item:
                    return False
            return True
        return self._evaluate(sink=pipe_equal)

    @partialclassmethod
    def exhaust(self):
        """
        {{pipe_sink}} Immediately exhaust the pipe and return `None`.
        """
        def pipe_exhaust(res):
            collections.deque(res, maxlen=0)
        return self._evaluate(sink=pipe_exhaust)

    @partialclassmethod
    def fold(self, func, initial=_MISSING):
        """
        {{pipe_sink}} Apply binary `func` to this Pipe, reducing it to a single
        value.

        `func` should be a function of two arguments.

        See {external:py:func}`functools.reduce`.
        """
        def pipe_fold(res):
            if initial is _MISSING:
                return functools.reduce(func, res)
            return functools.reduce(func, res, initial)
        return self._evaluate(sink=pipe_fold)

    @partialclassmethod
    def frequencies(self):
        """
        {{pipe_sink}} Return a {py:class}`collections.Counter` for this Pipe's
        items.
        """
        def pipe_frequencies(res):
            return collections.Counter(res)
        return self._evaluate(sink=pipe_frequencies)

    @partialclassmethod
    def groupby(self, key):
        """
        {{pipe_sink}} Return a {py:class}`dict` grouping together elements under
        the same `key` function result.

        Contrast with {py:meth}`Pipe.chunkby`, which is a step that yields
        groups of matching adjacent elements.
        """
        def pipe_groupby(res):
            ret = collections.defaultdict(list)
            for item in res:
                ret[key(item)].append(item)
            return dict(ret)
        return self._evaluate(sink=pipe_groupby)

    @partialclassmethod
    def identical(self, default=_MISSING):
        """
        {{pipe_sink}} Return `True` if all items are the same object (`a is b`).

        If there are no items, return `default` if it is provided; otherwise,
        raise `ValueError`.

        Contrast with {py:meth}`Pipe.equal`, returns true of all items compare
        equal (`a == b`).
        """
        def pipe_identical(ix):
            try:
                first_item = next(ix)
            except StopIteration as exc:
                if default is _MISSING:
                    raise ValueError("identical applied to empty iterable") from exc
                return default
            for item in ix:
                if item is not first_item:
                    return False
            return True
        return self._evaluate(sink=pipe_identical)

    @partialclassmethod
    def max(self, *, default=_MISSING, key=None):
        """
        {{pipe_sink}} Return the maximum value for this Pipe.

        If `default` is provided, return it if the iterable is empty.

        If `key` is provided, use it to determine the comparison value for each item.

        See {external:py:func}`max`.
        """
        def pipe_max(res):
            if default is _MISSING:
                return builtins.max(res, key=key)
            return builtins.max(res, default=default, key=key)
        return self._evaluate(sink=pipe_max)

    @partialclassmethod
    def mean(self, *, default=_MISSING):
        """
        {{pipe_sink}} Return the mean (average value) of this Pipe's items.

        If `default` is provided, return it if the iterable is empty.

        Contrast with {py:meth}`Pipe.median` and {py:meth}`Pipe.mode`.

        See {external:py:func}`statistics.mean`.
        """
        def pipe_mean(seq):
            try:
                return statistics.mean(seq)
            except statistics.StatisticsError:
                if default is not _MISSING:
                    return default
                raise
        return self._evaluate(sink=pipe_mean)

    @partialclassmethod
    def median(self, *, default=_MISSING):
        """
        {{pipe_sink}} Return the median (middle value) of this Pipe's items.

        If `default` is provided, return it if the iterable is empty.

        Contrast with {py:meth}`Pipe.mean` and {py:meth}`Pipe.mode`.

        See {external:py:func}`statistics.median`.
        """
        def pipe_median(res):
            try:
                return statistics.median(res)
            except statistics.StatisticsError:
                if default is not _MISSING:
                    return default
                raise
        return self._evaluate(sink=pipe_median)

    @partialclassmethod
    def merge(self, /, *, sequence='replace'):
        """
        {{pipe_sink}} Recursively merge this Pipe's mapping items into a single
        mapping.

        All collections in the resulting mapping are deep-copied and thus safe
        to mutate without affecting the original arguments.

        Values are handled as follows:

        - Mappings are merged with mappings, with identical keys being
          overwritten.

        - A mapping is entirely replaced by a non-mapping, and vice-versa.

        - A sequence with the same path as an existing sequence uses the
          `sequence` argument to determine how to handle it:

          - `'replace'` (the default) replaces the old sequence with the new
            sequence.

          - `'keep'` keeps the old sequence and discards the new sequence.

          - `'extend-old-new'` replaces the old sequence with a concatenation of the
            old sequence followed by the new sequence.

          - `'extend-new-old'` replaces the old sequence with a concatenation of the
            new sequence followed by the old sequence.

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
            new_sequence`, and return an appropriate item. (It is safe to return an
            argument from a `sequence` callable unchanged or mutated.)
        """
        def pipe_merge(res):
            return merge(res, sequence=sequence)
        return self._evaluate(sink=pipe_merge)

    @partialclassmethod
    def min(self, *, default=_MISSING, key=None):
        """
        {{pipe_sink}} Return the minimum value for this Pipe.

        If `default` is provided, return it if the iterable is empty.

        If `key` is provided, use it to determine the comparison value for each item.

        See {external:py:func}`min`.
        """
        def pipe_min(res):
            if default is _MISSING:
                return builtins.min(res, key=key)
            return builtins.min(res, default=default, key=key)
        return self._evaluate(sink=pipe_min)

    @partialclassmethod
    def minmax(self, *, default=_MISSING, key=None):
        """
        {{pipe_sink}} Return a tuple of `(min_value, max_value)` for this Pipe.

        If `default` is provided, return `(default, default)` if the iterable is empty.

        If `key` is provided, use it to determine the comparison value for each item.

        See {external:py:func}`min` and {external:py:func}`max`.
        """
        def pipe_minmax(ix):
            try:
                first_item = next(ix)
            except StopIteration as exc:
                if default is _MISSING:
                    raise ValueError("minmax applied to empty iterable") from exc
                return (default, default)
            def _minmax_fold(a, b):
                _min, _max = a
                return (builtins.min(_min, b, key=key), builtins.max(_max, b, key=key))
            return functools.reduce(_minmax_fold, ix, (first_item, first_item))
        return self._evaluate(sink=pipe_minmax)

    @partialclassmethod
    def mode(self, *, default=_MISSING):
        """
        {{pipe_sink}} Return the modes (most common values) of this Pipe's
        items.

        If `default` is provided, return it if the iterable is empty.

        Unlike {external:py:func}`statistics.mode`, this always returns a tuple
        of all modes encountered, rather than merely the first mode; see
        {external:py:func}`statistics.multimode`.

        Contrast with {py:meth}`Pipe.mean` and {py:meth}`Pipe.median`.
        """
        def pipe_mode(res):
            modes = statistics.multimode(res)
            if not modes and default is not _MISSING:
                return default
            return tuple(modes)
        return self._evaluate(sink=pipe_mode)

    @partialclassmethod
    def none(self, pred=_MISSING):
        """
        {{pipe_sink}} Return `True` if `pred(item)` is false for all items.

        If `pred` is missing, `bool(item)` will be used instead.

        Contrast with {py:meth}`Pipe.all` and {py:meth}`Pipe.any`.
        """
        def pipe_none(res):
            if pred is _MISSING:
                return not builtins.any(res)
            for item in res:
                if pred(item):
                    return False
            return True
        return self._evaluate(sink=pipe_none)

    @partialclassmethod
    def nth(self, n, default=_MISSING):
        """
        {{pipe_sink}} Return the `n`-th item.
        """
        def pipe_nth(res):
            match res:
                case Sequence():
                    try:
                        return res[n]
                    except IndexError:
                        if default is not _MISSING:
                            return default
                        raise
                case _:
                    ix = itertools.islice(res, n, None)
                    if default is not _MISSING:
                        return next(ix, default)
                    try:
                        return next(ix)
                    except StopIteration as exc:
                        raise IndexError(f"Pipe has no item at position {n}") from exc
        return self._evaluate(sink=pipe_nth)

    @partialclassmethod
    def struct_pack(self, format_, /):
        """
        {{pipe_sink}} Return packed {external:py:class}`bytes` from this Pipe's
        items using `format`.

        See {external:py:func}`struct.pack`.
        """
        def pipe_struct_pack(pipe):
            fsize = calc_struct_input(format_)
            if not fsize:
                return b''
            ret = []
            for chunk in pipe.chunk(fsize):
                ret.append(struct.pack(format_, *chunk))
            return b''.join(ret)
        return self._evaluate(sink=pipe_struct_pack)

    @partialclassmethod
    def partition(self, func=None):
        """
        {{pipe_sink}} Return a pair of tuples: `(true_items, false_items)`

        If `func` is provided, `func(item)` will be used to determine an item's
        truth value.
        """
        def pipe_partition(res):
            ret_true = []
            ret_false = []
            if func is None:
                for value in res:
                    (ret_true if value else ret_false).append(value)
            else:
                for value in res:
                    (ret_true if func(value) else ret_false).append(value)
            return (tuple(ret_true), tuple(ret_false))
        return self._evaluate(sink=pipe_partition)

    @partialclassmethod
    def product(self):
        """
        {{pipe_sink}} Return the arithmetical multiplication of the Pipe's
        items.

        Contrast with {py:meth}`Pipe.cartesian_product`.

        See {external:py:func}`math.prod`.
        """
        def pipe_product(res):
            return math.prod(res)
        return self._evaluate(sink=pipe_product)

    @partialclassmethod
    def shuffle(self):
        """
        {{pipe_sink}} Return a new shuffled list from this Pipe's items.

        Compare with {py:meth}`Pipe.sample`, which can yield repeated shuffles.
        """
        def pipe_shuffle(mutseq, rng):
            ret = mutseq.copy()
            rng.shuffle(ret)
            return ret
        return self._evaluate(sink=pipe_shuffle)

    @partialclassmethod
    def stdev(self, sample=False, mean=None):
        """
        {{pipe_sink}} Return the standard deviation of the Pipe's items.

        If `sample` is true, calculate the *sample* standard deviation;
        otherwise, calculate the population standard deviation.

        If `mean` is provided, it should be the already-computed mean of the
        sample or population.

        See {py:func}`statistics.stdev` and {py:func}`statistics.pstdev`.
        """
        def pipe_stdev(seq):
            if sample:
                return statistics.stdev(seq, xbar=mean)
            return statistics.pstdev(seq, mu=mean)
        return self._evaluate(sink=pipe_stdev)

    @partialclassmethod
    def sum(self):
        """
        {{pipe_sink}} Return the arithmetical addition of the Pipe's items.

        See {external:py:func}`sum`.
        """
        def pipe_sum(res):
            return builtins.sum(res)
        return self._evaluate(sink=pipe_sum)

    @partialclassmethod
    def variance(self, sample=False, mean=None):
        """
        {{pipe_sink}} Return the variance of the Pipe's items.

        If `sample` is true, calculate the *sample* variance; otherwise,
        calculate the population variance.

        If `mean` is provided, it should be the already-computed mean of the
        sample or population.

        See {py:func}`statistics.variance` and {py:func}`statistics.pvariance`.
        """
        def pipe_variance(seq):
            if sample:
                return statistics.variance(seq, xbar=mean)
            return statistics.pvariance(seq, mu=mean)
        return self._evaluate(sink=pipe_variance)

    @partialclassmethod
    def width(self, *, default=_MISSING, key=None):
        """
        {{pipe_sink}} Return the difference between the maximum and minimum
        values (i.e., the statistical range).

        If `default` is provided, return it if the iterable is empty.

        If `key` is provided, use it to determine the comparison value for each item.

        See {external:py:func}`min`.
        """
        def pipe_width(pipe):
            min_value, max_value = pipe.minmax(default=default, key=key)
            return max_value - min_value
        return self._evaluate(sink=pipe_width)

    ##############################################################
    # Sinks: container results

    @partialclassmethod
    def array(self, typecode):
        """
        {{pipe_sink}} Return an {external:py:class}`array.array` of the Pipe's
        items, using `typecode`.
        """
        def pipe_array(ix):
            return array.array(typecode, ix)
        return self._evaluate(sink=pipe_array)

    @partialclassmethod
    def bytes(self, sep=b''):
        """
        {{pipe_sink}} Return a {external:py:class}`bytes` concatenation of the
        Pipe's items.
        """
        def pipe_bytes(res):
            return sep.join(res)
        return self._evaluate(sink=pipe_bytes)

    @partialclassmethod
    def deque(self):
        """
        {{pipe_sink}} Return a {external:py:class}`collections.deque` of the
        Pipe's items.
        """
        def pipe_deque(res):
            return collections.deque(res)
        return self._evaluate(sink=pipe_deque)

    @partialclassmethod
    def dict(self):
        """
        {{pipe_sink}} Return a {external:py:class}`dict` of the Pipe's items,
        treating each item as a `(key, value)` pair.
        """
        def pipe_dict(res):
            return builtins.dict(res)
        return self._evaluate(sink=pipe_dict)

    @partialclassmethod
    def list(self):
        """
        {{pipe_sink}} Return a {external:py:class}`list` of the Pipe's items.
        """
        def pipe_list(res):
            return builtins.list(res)
        return self._evaluate(sink=pipe_list)

    @partialclassmethod
    def set(self):
        """
        {{pipe_sink}} Return a {external:py:class}`set` of the Pipe's items.
        """
        def pipe_set(res):
            return builtins.set(res)
        return self._evaluate(sink=pipe_set)

    @partialclassmethod
    def str(self, sep=''):
        """
        {{pipe_sink}} Return a {external:py:class}`str` concatenation of the
        Pipe's items.
        """
        def pipe_str(res):
            return sep.join(res)
        return self._evaluate(sink=pipe_str)

    @partialclassmethod
    def tuple(self):
        """
        {{pipe_sink}} Return a {external:py:class}`tuple` of the Pipe's items.
        """
        def pipe_tuple(res):
            return builtins.tuple(res)
        return self._evaluate(sink=pipe_tuple)
