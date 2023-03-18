# Seittik

Seittik is a functional programming library for Python that aims to
supplant Python's existing functional interfaces, offering a more
comprehensive and expressive alternative.

Put another way: If you ever wished Python's `map`, `filter`, and
`itertools` had a fluent API, or that `lambda` wasn't quite so verbose,
this is for you.

It provides:

- A fluent and extensive API for processing iterable data: *pipes*.
- A compact and expressive alternative to `lambda`: *shears*.
- A kitchen-sink, all-under-one-roof approach.
- A REPL-first philosophy.

## Examples

Something basic:

```python
from seittik import P, X, Y

# Take numbers 1 through 4, triple them, keep evens, and sum them
P([1, 2, 3, 4]).map(X * 3).filter(X % 2 == 0).fold(X + Y)
# 18

# Or, equivalently:
P.range(1, 4).map(X * 3).filter(X % 2 == 0).sum()
# 18
```

And something more amusing:

```python
import random; random.seed(0) # Get a deterministic result below
from seittik import P, X, Y

# Return 5 arrays of traditional RPG stats (rolling three six-sided dice
# for each of "Str", "Dex", "Con", "Int", "Wis", and "Cha") that have at
# least one score of 14 or better, sorted by the sum of the array, in
# descending order, providing dict labels.
(P.roll('3d6')
    .chunk(6)
    .filter(P.any(X >= 14))
    .dictmap({'sum': sum, 'scores': X})
    .take(5)
    .sort(key=X['sum'], reverse=True)
    .list())
# [{'sum': 71, 'scores': (13, 13, 9, 8, 16, 12)},
#  {'sum': 66, 'scores': (14, 10, 8, 13, 9, 12)},
#  {'sum': 66, 'scores': (8, 14, 9, 12, 13, 10)},
#  {'sum': 57, 'scores': (9, 15, 8, 6, 10, 9)},
#  {'sum': 54, 'scores': (12, 7, 5, 14, 6, 10)}]
```

(These undoubtedly look much nicer on the [documentation
site](https://seittik.com/).)

## Installation

Using [Poetry](https://python-poetry.org/) with an existing project:

```sh
poetry add seittik
```

If you're using `pip` directly (not recommended):

```sh
pip install seittik
```

## Documentation

See [seittik.com](https://seittik.com/)

## License

MIT. See [LICENSE](./LICENSE).

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).

## Like it? Support kitties!

If you're able, donations to [4 Paws Sake
PA](https://www.facebook.com/4PawsSakePA/) would be enormously
appreciated. They're an absolutely wonderful animal rescue.

("Seittik" is "kitties" spelled backwards. I'm a cat person, and I
wanted to avoid name collisions.)
