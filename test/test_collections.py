from seittik.utils.collections import defaultlist, Seen

import pytest


# defaultlist

def test_defaultlist_empty():
    assert defaultlist() == []
    assert defaultlist(list) == []
    assert defaultlist(dict) == []


def test_defaultlist_list():
    d = defaultlist(list)
    assert len(d) == 0
    d[3].append(9)
    assert len(d) == 4
    assert d[3] == [9]
    assert d == [[], [], [], [9]]
    d[1].extend([13, 21])
    assert d[1] == [13, 21]
    assert d == [[], [13, 21], [], [9]]


def test_defaultlist_missing_factory():
    d = defaultlist()
    with pytest.raises(IndexError):
        d[5]


# Seen

def test_seen_hash():
    s = Seen(hash)
    assert [x in s for x in (1, 2, 1, 2, 3)] == [False, False, True, True, False]


def test_seen_id():
    s = Seen(id)
    a, b, c = [[1], [2], [1]]
    assert [x in s for x in (a, b, c, a, b, c)] == [False, False, False, True, True, True]


def test_seen_len():
    s = Seen()
    for x in (1, 2, 1, 2, 3):
        x in s
    assert len(s) == 3


def test_seen_repr():
    s = Seen()
    for x in (1, 2, 1, 2, 3):
        x in s
    assert repr(s) == '<Seen (3)>'


def test_seen_clear():
    s = Seen()
    for x in (1, 2, 1, 2, 3):
        x in s
    s.clear()
    assert len(s) == 0
    assert repr(s) == '<Seen (0)>'


def test_seen_bool():
    s = Seen()
    for x in (1, 2, 1, 2, 3):
        x in s
    assert bool(s) == True
    s.clear()
    assert bool(s) == False
