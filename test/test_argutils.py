import pytest


from seittik.utils.argutils import (
    check_int, check_int_or_none, check_int_positive,
    check_int_positive_or_none, check_int_zero_or_positive,
    check_n_args, check_r_args, check_slice_args, replace,
)
from seittik.utils.sentinels import _MISSING


# replace

def test_replace_missing_values():
    x = 1
    with pytest.raises(TypeError):
        x = replace(_MISSING, 2)


def test_replace_one():
    x = _MISSING
    x = replace(_MISSING, 2, x)
    assert x == 2


def test_replace_two():
    x = _MISSING
    y = _MISSING
    x, y = replace(_MISSING, 2, x, y)
    assert x == 2
    assert y == 2


# check_int

def test_check_int_pass():
    x = 5
    assert check_int('x', x) is None


def test_check_int_fail():
    x = 'meow'
    with pytest.raises(TypeError):
        check_int('x', x)


# check_int_or_none

def test_check_int_or_none_pass():
    x = 5
    assert check_int_or_none('x', x) is None
    y = None
    assert check_int_or_none('x', None) is None


def test_check_int_or_none_fail():
    x = 'meow'
    with pytest.raises(TypeError):
        check_int_or_none('x', x)


# check_int_positive

def test_check_int_positive_pass():
    x = 3
    assert check_int_positive('x', x) is None


def test_check_int_positive_fail_nonpos():
    x = 0
    with pytest.raises(ValueError):
        check_int_positive('x', x)
    x = -3
    with pytest.raises(ValueError):
        check_int_positive('x', x)


def test_check_int_positive_fail_nonint():
    x = 'meow'
    with pytest.raises(TypeError):
        check_int_positive('x', x)


# check_int_positive_or_none

def test_check_int_positive_or_none_pass():
    x = 3
    assert check_int_positive_or_none('x', x) is None
    x = None
    assert check_int_positive_or_none('x', x) is None


def test_check_int_positive_or_none_fail_nonpos():
    x = 0
    with pytest.raises(ValueError):
        check_int_positive_or_none('x', x)
    x = -3
    with pytest.raises(ValueError):
        check_int_positive_or_none('x', x)


def test_check_int_positive_or_none_fail_nonint():
    x = 'meow'
    with pytest.raises(TypeError):
        check_int_positive_or_none('x', x)


# check_int_zero_or_positive

def test_check_int_zero_or_positive_pass():
    x = 0
    assert check_int_zero_or_positive('x', x) is None
    x = 3
    assert check_int_zero_or_positive('x', x) is None


def test_check_int_zero_or_positive_fail_nonpos():
    x = -3
    with pytest.raises(ValueError):
        check_int_zero_or_positive('x', x)


def test_check_int_zero_or_positive_fail_nonint():
    x = 'meow'
    with pytest.raises(TypeError):
        check_int_zero_or_positive('x', x)


# check_r_args

def test_check_r_args_single_int():
    r = 3
    assert check_r_args('r', r) == (3, 3)


def test_check_r_args_pair_ints():
    r = (3, 9)
    assert check_r_args('r', r) == (3, 9)


def test_check_r_args_tuple_missing_max():
    r = (3,)
    assert check_r_args('r', r, default=5) == (3, 5)
    r = (3, None)
    assert check_r_args('r', r, default=5) == (3, 5)


def test_check_r_args_tuple_missing():
    r = None
    assert check_r_args('r', r, default=5) == (5, 5)


def test_check_r_args_tuple_fail_descending():
    r = (9, 3)
    with pytest.raises(ValueError):
        check_r_args('r', r)


def test_check_r_args_tuple_fail_badtype():
    r = 'meow'
    with pytest.raises(TypeError):
        check_r_args('r', r)


# check_slice_args

def test_slice_args_empty():
    assert check_slice_args('func', [], {}) == (0, None, 1)


def test_slice_args_fail_multi_step():
    with pytest.raises(TypeError):
        check_slice_args('func', [0, 5, 1], {'step': 1})


def test_slice_args_fail_step_zero():
    with pytest.raises(ValueError):
        check_slice_args('func', [0, 5, 0], {})


def test_slice_args_fail_multi_start():
    with pytest.raises(TypeError):
        check_slice_args('func', [0, 5, 1], {'start': 0})


def test_slice_args_fail_multi_stop():
    with pytest.raises(TypeError):
        check_slice_args('func', [0, 5, 1], {'stop': 5})


def test_slice_args_positional_stop():
    assert check_slice_args('func', [3], {}) == (0, 3, 1)


def test_slice_args_positional_start_none():
    assert check_slice_args('func', [None, 3], {}) == (0, 3, 1)


def test_slice_args_positional_start_explicit():
    assert check_slice_args('func', [0, 3], {}) == (0, 3, 1)


def test_slice_args_positional_step_explicit():
    assert check_slice_args('func', [None, 3, 2], {}) == (0, 3, 2)
    assert check_slice_args('func', [0, None, 2], {}) == (0, None, 2)
    assert check_slice_args('func', [0, 3, None], {}) == (0, 3, 1)
    assert check_slice_args('func', [0, 3, 2], {}) == (0, 3, 2)


def test_slice_args_fail_too_many_positional_args():
    with pytest.raises(TypeError):
        check_slice_args('func', [0, 5, 1, 7], {})


# check_n_args

def test_check_n_args_pass():
    assert check_n_args('func', 3, [1, 2, 3]) is None


def test_check_n_args_fail():
    with pytest.raises(TypeError):
        check_n_args('func', 3, [1, 2, 3, 4])
