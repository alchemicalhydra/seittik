import pytest

from seittik.utils.compareutils import Maximum, Minimum

def test_minimum_vs_maximum():
    minimum = Minimum()
    maximum = Maximum()
    assert minimum < maximum
    assert maximum > minimum
    assert minimum != maximum
    assert maximum != minimum


def test_maximum():
    import math
    maximum = Maximum()
    assert maximum > math.inf


def test_minimum():
    import math
    minimum = Minimum()
    assert minimum < -math.inf


def test_maximum_repr():
    maximum = Maximum()
    assert repr(maximum) == '<MAXIMUM>'


def test_minimum_repr():
    minimum = Minimum()
    assert repr(minimum) == '<MINIMUM>'
