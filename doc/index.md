# Seittik

Seittik is a functional programming library for Python that aims to
supplant Python's existing functional interfaces, offering a more
comprehensive and expressive alternative.

Put another way: If you ever wished Python's {py:func}`map`,
{py:func}`filter`, and {py:mod}`itertools` had a fluent API, or that
{term}`lambda` wasn't quite so verbose, this is for you.

It provides:

- A fluent and extensive API for processing iterable data: *pipes*.
- A compact and expressive alternative to {term}`lambda`: *shears*.
- A kitchen-sink, all-under-one-roof approach.
- A REPL-first philosophy.

## Examples

Something basic:

```{ipython}

In [1]: from seittik.pipes import Pipe as P

In [1]: from seittik.shears import X, Y

# Take numbers 1 through 4, triple them, keep evens, and sum them
In [1]: P([1, 2, 3, 4]).map(X * 3).filter(X % 2 == 0).fold(X + Y)
Out[1]: 18

# Or, equivalently:
In [1]: P.range(1, 4).map(X * 3).filter(X % 2 == 0).sum()
Out[1]: 18
```

```{marble}
[ source: range(1, 4) ]
--1--2--3--4----------|
[ step: map(X * 3)    ]
--3--6--9--12---------|
[ step: filter(even)  ]
-----6-----12---------|
[ sink: sum()         ]
-----------18---------|
```

And something more amusing:

```{ipython}

@suppress
In [1]: import random; random.seed(0)

# Return 5 arrays of traditional RPG stats (rolling three six-sided dice
# for each of "Str", "Dex", "Con", "Int", "Wis", and "Cha") that have at
# least one score of 14 or better, sorted by the sum of the array, in
# descending order, providing dict labels.
In [1]: (P.roll('3d6')
   ...: .chunk(6)
   ...: .filter(P.any(X >= 14))
   ...: .dictmap({'sum': sum, 'scores': X})
   ...: .take(5)
   ...: .sort(key=X['sum'], reverse=True)
   ...: .list())
Out[1]:
[{'sum': 71, 'scores': (13, 13, 9, 8, 16, 12)},
 {'sum': 66, 'scores': (14, 10, 8, 13, 9, 12)},
 {'sum': 66, 'scores': (8, 14, 9, 12, 13, 10)},
 {'sum': 57, 'scores': (9, 15, 8, 6, 10, 9)},
 {'sum': 54, 'scores': (12, 7, 5, 14, 6, 10)}]
```

## Table of Contents

```{warning}
Anything not documented is considered a private interface, especially
anything in `seittik.utils`.
```

```{toctree}
:maxdepth: 4

apidocs/index
```

```{toctree}
:maxdepth: 2

license
changelog
design-notes
```

{ref}`genindex`

{ref}`modindex`

{ref}`search`


## Like it? Support kitties!

If you're able, donations to [4 Paws Sake
PA](https://www.facebook.com/4PawsSakePA/) would be enormously
appreciated. They're an absolutely wonderful animal rescue.

("Seittik" is "kitties" spelled backwards. I'm a cat person, and I
wanted to avoid name collisions.)

