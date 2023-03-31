# User Guide

Seittik provides a somewhat different approach to functional programming
in Python.

There are two key concepts:

- **Shears**, which let you avoid verbose lambdas in several situations.
- **Pipes**, which provide a fluent API for iterable data processing.

Shears and pipes can work independently, but they're even more useful
when used together.

## Shears

Shears are so named for being *lambda shortcuts*. (Yes, it's an awful
pun.)

### Shear Variables

A *shear variable* is the basic building block for shears. You can
import them directly from the top-level `seittik` module:

```{ipython}

In [1]: from seittik import X, Y, Z
```

### Shear Operations

By performing operations on them, you create new *shear operations*,
which are just fancy partial functions.

```{ipython}
:doctest:

In [1]: add3 = X + 3

In [1]: add3(5)
Out[1]: 8
```

Shears support every operator that it's possible to support via the
Python object model and still return a partial function.

::::{note}
For certain magic methods, a shear can't return a partial:

```{ipython}
:verbatim:

# This doesn't work, because __contains__ always returns a boolean:
In [1]: has_meow = 'meow' in X
# NotImplementedError: `item in X` unsupported; use `X.contains(item)` instead
```

In these cases, shears provide alternate methods:

```{ipython}

# But this works:
In [1]: has_meow = X.contains('meow')

In [1]: has_meow({'meow', 'woof'})
Out[1]: True
```
::::

### Shear Comparisons

Comparisons work, too:

```{ipython}

In [1]: is_two = X == 2

In [1]: is_two(2)
Out[1]: True

In [1]: is_two(3)
Out[1]: False

In [1]: is_negative = X < 0

In [1]: is_negative(13)
Out[1]: False

In [1]: is_negative(-5)
Out[1]: True
```

### Shear Composition

Shears understand when they're being referenced multiple times in a
single operation:

```{ipython}

In [1]: double = X + X

In [1]: double(3)
Out[1]: 6

In [1]: cube = X * X * X

In [1]: cube(2)
Out[1]: 8
```

Different shears are composable, and understand ordering:

```{ipython}

In [1]: sub = X - Y

In [1]: sub(9, 5)
Out[1]: 4

In [1]: mul_then_add = X * Y + Z

In [1]: mul_then_add(3, 4, 5)
Out[1]: 17

In [1]: is_even = X % 2 == 0

In [1]: is_even(4)
Out[1]: True

In [1]: is_even(9)
Out[1]: False
```

## Pipes

Pipes let you query and manipulate iterable data in a multitude of ways,
all using a fluent API.

```{ipython}

In [1]: from seittik import P
```

Pipes are built out of three kinds of **stages**:

- **Sources** define the initial iterable input for the pipe.
  - Pipes have one source.
- **Steps** define intermediate transformations of the pipe.
  - Pipes can have any number of steps, including zero.
- **Sinks** evaluate a pipe's contents.
  - Pipes can have a single sink, or they can be iterated upon directly
    without a sink.

:::{note}
As an iterable traverses the stages of a pipe, the pipe attempts to
intelligently avoid switching between iterators and collections unless
absolutely necessary.

This saves CPU and memory, and allows the processing of infinite
iterators as long as a stage doesn't require coercion to a collection.
:::

### Starting a Pipe: Sources

Pipes are started by invoking a *source*.

The simplest way to build a pipe is to pass an iterable to the Pipe
class:

```{ipython}

In [1]: P([1, 2, 3, 4, 5])
Out[1]: <Pipe [1, 2, 3, 4, 5]>
```

There are also alternate sources for pipes:

```{ipython}

In [1]: P.range(10)
Out[1]: <Pipe range>
```

:::{warning}
If the pipe source is an *iterator*, the pipe can only be evaluated
*once*, since the iterator will be consumed.

If the pipe source is an iterable container that returns fresh iterables
(like a sequence), the pipe can be evaluated multiple times.
:::

### Evaluating a Pipe: Sinks

Pipes are evaluated either by directly iterating over them, or invoking
a *sink*.

#### Direct Evaluation

Direct evaluation is simple:

```{ipython}

In [1]: p = P([1, 2, 3, 4, 5])

In [1]: for item in p:
   ...:     print(item)
1
2
3
4
5
```

#### Sink Methods

##### Collection Sinks

There are several sink methods that simply return the pipe's items as a
collection:

```{ipython}

In [1]: p = P([1, 2, 3, 4, 5])

In [1]: p.list()
Out[1]: [1, 2, 3, 4, 5]

In [1]: p.tuple()
Out[1]: (1, 2, 3, 4, 5)

In [1]: p.set()
Out[1]: {1, 2, 3, 4, 5}
```

Mappings work, too:

```{ipython}

In [1]: p_kv = P([('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)])

In [1]: p_kv.dict()
Out[1]: {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
```

##### Aggregation Sinks

There are also a variety of sinks that aggregate the pipe's items
somehow:

```{ipython}

In [1]: p = P([1, 2, 3, 4, 5])

In [1]: p.sum()
Out[1]: 15

In [1]: p.product()
Out[1]: 120

In [1]: p.median()
Out[1]: 3

In [1]: p.fold(X - Y)
Out[1]: -13
```

(Yes, we used a shear in that last example.)

### Transforming a Pipe: Steps

Steps offer intermediate transformations of a pipe before its final
evaluation.

:::{note}
Pipes are fundamentally *lazy*: they are not evaluated until a sink is
invoked, no matter how many steps you add to them.
:::

```{ipython}

In [1]: p = P([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).map(X * 3).filter(X % 2 == 0)

In [1]: p
In [1]: <Pipe [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] => map => filter>

In [1]: p.list()
Out[1]: [6, 12, 18, 24, 30]
```

### Pipes as Partials

Pipes can be invoked as partial functions, enabling their use wherever
an appropriate partial would be helpful.

#### Empty Sources

Any Pipe instance created without a source (`P()`) will cause any sink
method terminating it to return a partial; this partial can be passed a
source, which will then cause the entire pipe to evaluate.

```{ipython}

In [1]: p = P().map(X * 3).filter(X % 2 == 0).list()

In [1]: p([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
Out[1]: [6, 12, 18, 24, 30]

In [1]: p([33, 44, 55, 66, 77, 88])
Out[1]: [132, 198, 264]
```

#### Sink Class Methods

All sinks can be invoked directly as class methods, which will return a
partial function accepting a new source and immediately evaluating.


```{ipython}

In [1]: any_greater_than_3 = P.any(X > 3)

In [1]: any_greater_than_3([1, 2, 3, 4, 5])
Out[1]: True

In [1]: P.minmax()([3, 7, 2, 9, 6, 8])
Out[1]: (2, 9)
```

### Further Reading

The <project:apidocs/index.md> has an overview of all the various Pipe
stages, with links to detailed signatures.
