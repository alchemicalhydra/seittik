"""
Utilities for checking and processing function arguments at runtime.
"""

from .sentinels import _MISSING


__all__ = ()


def replace(sentinel, replacement, *values):
    """
    For each of `values`, return it unchanged if it isn't identical to
    `sentinel`; otherwise, return `replacement`.

    `sentinel` is checked via identity, not equality.

    If the length of `values` is greater than 1, return a tuple of results.
    """
    ret = tuple((v if v is not sentinel else replacement) for v in values)
    match len(ret):
        case 0:
            raise TypeError("'replace' missing at least one 'values' argument")
        case 1:
            return ret[0]
        case _:
            return ret


def check_int(name, value):
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer; got {value!r}")


def check_int_or_none(name, value):
    if value is None:
        return
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer or None; got {value!r}")


def check_int_positive(name, value):
    match value:
        case int():
            if value <= 0:
                raise ValueError(f"{name} must be an integer > 0; got {value!r}")
        case _:
            raise TypeError(f"{name} must be an integer; got {value!r}")


def check_int_zero_or_positive(name, value):
    match value:
        case int():
            if value < 0:
                raise ValueError(f"{name} must be an integer >= 0; got {value!r}")
        case _:
            raise TypeError(f"{name} must be an integer; got {value!r}")


def check_int_positive_or_none(name, value):
    if value is None:
        return
    check_int_positive(name, value)


def check_k_args(name, k, default=_MISSING):
    """
    Check `k` for a non-negative integer range.

    `k` may be a non-negative integer, representing both `k_min` and
    `k_max`, or a `(k_min, k_max)` tuple.

    If `k` is `None` and `default` is provided as a non-negative integer,
    `default` will be used in place of `k`.

    Return `(k_min, k_max)`.

    (The variable name `k` comes from statistics and set theory.)
    """
    match k:
        case int():
            check_int_zero_or_positive(name, k)
            return (k, k)
        case (int() as a, int() as b) if b >= a:
            check_int_zero_or_positive(f"{name}[0]", a)
            check_int_zero_or_positive(f"{name}[1]", b)
            return (a, b)
        case (int() as a, int() as b):
            raise ValueError(
                f"{name!r} was provided as a descending pair of integers; must be ascending; got {k!r}"
            )
        case (int() as a,) | (int() as a, None) if default is not _MISSING:
            check_int_zero_or_positive(f"{name}[0]", a)
            return (a, default)
        case None if default is not _MISSING:
            return (default, default)
        case _:
            raise TypeError(
                f"{name!r} must be a non-negative integer,"
                f" a pair of ascending non-negative integers, or None; got {k!r}"
            )


def check_slice_args(func_name, args, kwargs):
    """
    For the given slice-style positional and keyword arguments, return a
    tuple of `(start, stop, step)`

    "Slice-style" for positional arguments means:
    - `func() -> (0, None, 1)`
    - `func(stop) -> (0, stop, 1)`
    - `func(start, stop) -> (start, stop, 1)`
    - `func(start, stop, step) -> (start, stop, step)`

    Providing a keyword argument for a positional argument will raise a
    `TypeError`.

    Providing a `step` of 0 will raise a `ValueError`.

    Errors will use the provided `func_name`.
    """
    match (args, kwargs):
        # Step errors
        case ([_, _, _], {'step': _}):
            raise TypeError(f"{func_name} got multiple values for argument 'step'")
        case (([_, _, step], _) | (_, {'step': step})) if step == 0:
            raise ValueError(f"{func_name} cannot have a 'step' of 0")
        # Start errors
        case ([_, _, *_], {'start': _}):
            raise TypeError(f"{func_name} got multiple values for argument 'start'")
        # Stop errors
        case ([_, *_], {'stop': _}):
            raise TypeError(f"{func_name} got multiple values for argument 'stop'")
        # Legal cases
        case ([(int() | None) as stop], _):
            return (kwargs.get('start', 0), stop, kwargs.get('step', 1))
        case ([(int() | None) as start, (int() | None) as stop], _):
            if start is None:
                start = 0
            return (start, stop, kwargs.get('step', 1))
        case ([(int() | None) as start, (int() | None) as stop, (int() | None) as step], _):
            if start is None:
                start = 0
            if step is None:
                step = 1
            return (start, stop, step)
        case ([], _):
            return (kwargs.get('start', 0), kwargs.get('stop', None), kwargs.get('step', 1))
        # Incorrect positional arguments
        case _:
            raise TypeError(f"{func_name} takes 0-3 positional arguments but {len(args)} were given")


def check_n_args(func_name, n, args):
    if len(args) != n:
        raise TypeError(f"{func_name} takes {n} positional arguments but {len(args)} were given")
