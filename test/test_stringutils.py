import pytest

from seittik.utils.sentinels import _MISSING
from seittik.utils.stringutils import conjoin_phrases


@pytest.mark.parametrize(
    ['phrases', 'conj', 'fmt', 'ret'],
    [
        [[], 'or', _MISSING, ''],
        [['a'], 'or', _MISSING, 'a'],
        [['a', 'b'], 'or', _MISSING, 'a or b'],
        [['a', 'b'], 'and', _MISSING, 'a and b'],
        [['a', 'b'], '', _MISSING, 'a, b'],
        [['a', 'b'], None, _MISSING, 'a, b'],
        [['a', 'b'], 'or', repr, "'a' or 'b'"],
        [['a', 'b'], 'or', '{!r}', "'a' or 'b'"],
        [['a', 'b'], 'and', repr, "'a' and 'b'"],
        [['a', 'b'], 'and', '{!r}', "'a' and 'b'"],
        [['a', 'b'], 'or', 'FOO{}BAR', "FOOaBAR or FOObBAR"],
        [['a', 'b', 'c'], 'or', _MISSING, 'a, b, or c'],
        [['a', 'b', 'c'], 'and', _MISSING, 'a, b, and c'],
        [['a', 'b', 'c'], '', _MISSING, 'a, b, c'],
        [['a', 'b', 'c'], None, _MISSING, 'a, b, c'],
        [['a', 'b', 'c', 'd'], 'or', _MISSING, 'a, b, c, or d'],
        [['a', 'b', 'c', 'd'], 'and', _MISSING, 'a, b, c, and d'],
        [['a', 'b', 'c', 'd'], 'and', repr, "'a', 'b', 'c', and 'd'"],
    ],
)
def test_conjoin_phrases(phrases, conj, fmt, ret):
    assert conjoin_phrases(phrases, conj=conj, fmt=fmt) == ret


def test_conjoin_phrases_bad_fmt():
    with pytest.raises(TypeError):
        conjoin_phrases(['a'], fmt=13)


def test_conjoin_phrases_bad_phrases():
    with pytest.raises(TypeError):
        conjoin_phrases(13)
