from collections.abc import Callable

from .sentinels import _MISSING


def conjoin_phrases(phrases, conj='or', fmt=_MISSING):
    """
    Given `phrases` as an iterable of strings, return an appropriate string
    conjunction of those phrases.

    - If `fmt` is supplied:
      - If `fmt` is a format string, use it to format each phrase.
      - If `fmt` is a callable, pass each phrase through it.

    - Given a particular number of phrases:
        - If no phrases are supplied, return an empty string.
        - If one phrase is supplied, return it as-is.
        - If two phrases are supplied:
          - If `conj` is not false/empty, return them as `{first} {conj}
            {second}`.
          - Otherwise, return `{first}, {second}`.
        - If three or more phrases are supplied, suffix all but the last with
          commas, and:
          - If `conj` is not false/empty, return, e.g., `{first}, {second},
            {conj} {third}`.
          - Otherwise return, e.g., `{first}, {second}, {third}`.

    ```{ipython}

    In [1]: conjoin_phrases([])
    Out[1]: ''

    In [1]: conjoin_phrases(['a'])
    Out[1]: 'a'

    In [1]: conjoin_phrases(['a', 'b'])
    Out[1]: 'a or b'

    In [1]: conjoin_phrases(['a', 'b'], conj='and')
    Out[1]: 'a and b'

    In [1]: conjoin_phrases(['a', 'b'], conj='')
    Out[1]: 'a, b'

    In [1]: conjoin_phrases(['a', 'b', 'c'])
    Out[1]: 'a, b, or c'

    In [1]: conjoin_phrases(['a', 'b', 'c'], conj='and')
    Out[1]: 'a, b, and c'

    In [1]: conjoin_phrases(['a', 'b', 'c'], conj='')
    Out[1]: 'a, b, c'

    In [1]: conjoin_phrases(['a', 'b', 'c', 'd'])
    Out[1]: 'a, b, c, or d'

    In [1]: conjoin_phrases(['a', 'b'], fmt=repr)
    Out[1]: "'a' or 'b'"

    In [1]: conjoin_phrases(['a', 'b'], fmt='{!r}')
    Out[1]: "'a' or 'b'"

    In [1]: conjoin_phrases(['a', 'b'], fmt='FOO{}BAR')
    Out[1]: "'FOOaBAR' or 'FOObBAR'"

    In [1]: conjoin_phrases(['a', 'b', 'c', 'd'], conj='and', fmt=repr)
    Out[1]: "'a', 'b', 'c', and 'd'"
    ```
    """
    match fmt:
        case str():
            phrases = [fmt.format(phrase) for phrase in phrases]
        case Callable():
            phrases = [fmt(phrase) for phrase in phrases]
        case _ if fmt is _MISSING:
            pass
        case _:
            raise TypeError(f"'fmt' must be a string or a callable; got {fmt!r} of type {type(fmt)!r}")
    match phrases:
        case []:
            return ''
        case [x]:
            return x
        case [x, y]:
            return ' '.join([f"{x}{'' if conj else ','}", *([conj] if conj else []), y])
        case [*xs, y]:
            return ' '.join([*(f'{x},' for x in xs), *([conj] if conj else []), y])
        case _:
            raise TypeError(f"'phrases' must be an iterable; got {phrases!r} of type {type(phrases)!r}")
