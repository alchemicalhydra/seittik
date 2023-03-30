import itertools
import operator
import re

import pytest

from seittik.shears import ShearUnOp, ShearBinOp, X, Y, Z


class MatMulMock(int):
    def __matmul__(self, other):
        return self * other

    def __rmatmul__(self, other):
        return self * other


_RE_FUNC = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
_SPECIAL_BINARY_OPERATORS = (
    {
        'name': 'add',
        'op': operator.add,
        'symbol': '+',
        'commutative': True,
        'identity': 0,
        'test': (
            (0, 0),
            (-0.5, -1),
            (0.5, 1),
            (1, 2),
            (-1, -2),
            (2, 4),
            (-2, -4),
            (3, 6),
            (-3, -6),
            (7, 14),
            (-7, -14),
            (0, 0, 0),
            (0, 1, 1),
            (2, 3, 5),
            (3, 5, 8),
            (-2, -3, -5),
            (-3, -5, -8),
            (0, 0, 0, 0),
            (0, 1, 1, 2),
            (2, 3, 5, 10),
            (3, 5, 8, 16),
            (-2, -3, -5, -10),
            (-3, -5, -8, -16),
        ),
    },
    {
        'name': 'sub',
        'op': operator.sub,
        'symbol': '-',
        'commutative': False,
        'identity': 0,
        'test': (
            (0, 0),
            (-0.5, 0),
            (0.5, 0),
            (1, 0),
            (-1, 0),
            (2, 0),
            (-2, 0),
            (3, 0),
            (-3, 0),
            (7, 0),
            (-7, 0),
            (0, 0, 0),
            (0, 1, -1),
            (1, 0, 1),
            (2, 3, -1),
            (3, 2, 1),
            (3, 5, -2),
            (5, 3, 2),
            (-2, 3, -5),
            (-3, 2, -5),
            (-3, 5, -8),
            (-5, 3, -8),
            (2, -3, 5),
            (3, -2, 5),
            (3, -5, 8),
            (5, -3, 8),
            (-2, -3, 1),
            (-3, -2, -1),
            (-3, -5, 2),
            (-5, -3, -2),
            (0, 0, 0, 0),
            (1, 0, 0, 1),
            (0, 1, 0, -1),
            (0, 0, 1, -1),
            (2, 3, 5, -6),
        ),
    },
    {
        'name': 'mul',
        'op': operator.mul,
        'symbol': '*',
        'commutative': True,
        'identity': 1,
        'test': (
            (0, 0),
            (-0.5, 0.25),
            (0.5, 0.25),
            (1, 1),
            (-1, 1),
            (2, 4),
            (-2, 4),
            (3, 9),
            (-3, 9),
            (7, 49),
            (-7, 49),
            (0, 0, 0),
            (0, 1, 0),
            (1, 1, 1),
            (1, -1, -1),
            (-1, -1, 1),
            (2, 3, 6),
            (2, -3, -6),
            (-2, 3, -6),
            (-2, -3, 6),
            (3, 5, 15),
            (-3, 5, -15),
            (3, -5, -15),
            (-3, -5, 15),
            (0, 0, 0, 0),
            (1, 0, 0, 0),
            (2, 3, 5, 30),
        ),
    },
    {
        'name': 'matmul',
        'op': operator.matmul,
        'symbol': '@',
        'commutative': True,
        'identity': 1,
        'wrapper': MatMulMock,
        'test': (
            (0, 0),
            (1, 1),
            (-1, 1),
            (2, 4),
            (-2, 4),
            (3, 9),
            (-3, 9),
            (7, 49),
            (-7, 49),
            (0, 0, 0),
            (0, 1, 0),
            (1, 1, 1),
            (1, -1, -1),
            (-1, -1, 1),
            (2, 3, 6),
            (2, -3, -6),
            (-2, 3, -6),
            (-2, -3, 6),
            (3, 5, 15),
            (-3, 5, -15),
            (3, -5, -15),
            (-3, -5, 15),
            (0, 0, 0, 0),
            (1, 0, 0, 0),
            (2, 3, 5, 30),
        ),
    },
    {
        'name': 'truediv',
        'op': operator.truediv,
        'symbol': '/',
        'commutative': False,
        'identity': 1,
        'guard': lambda a, b: b != 0,
        'test': (
            (-0.5, 1),
            (0.5, 1),
            (1, 1),
            (-1, 1),
            (2, 1),
            (-2, 1),
            (3, 1),
            (-3, 1),
            (7, 1),
            (-7, 1),
            (0, 1, 0),
            (0.2, 10, 0.02),
            (1, 2, 0.5),
            (2, 1, 2),
            (2, 3, 2/3),
            (3, 2, 3/2),
            (3, 5, 3/5),
            (5, 1, 5),
            (5, 3, 5/3),
            (6, 2, 3),
            (6, 3, 2),
            (2, 10, 0.2),
            (10, 2, 5),
            (10, 5, 2),
            (-2, 3, -2/3),
            (-3, 2, -3/2),
            (-3, 5, -3/5),
            (-5, 3, -5/3),
            (2, -3, -2/3),
            (3, -2, -3/2),
            (3, -5, -3/5),
            (5, -3, -5/3),
            (-2, -3, 2/3),
            (-3, -2, 3/2),
            (-3, -5, 3/5),
            (-5, -3, 5/3),
            (0, 1, 1, 0),
            (1, 1, 1, 1),
            (2, 3, 5, 2/3/5),
            (15, 3, 5, 1),
        ),
    },
    {
        'name': 'floordiv',
        'op': operator.floordiv,
        'symbol': '//',
        'commutative': False,
        'identity': 1,
        'guard': lambda a, b: b != 0,
        'test': (
            (-0.5, 1),
            (0.5, 1),
            (1, 1),
            (-1, 1),
            (2, 1),
            (-2, 1),
            (3, 1),
            (-3, 1),
            (7, 1),
            (-7, 1),
            (0, 1, 0),
            (0.2, 10, 0),
            (1, 2, 0),
            (2, 1, 2),
            (2, 3, 0),
            (3, 2, 1),
            (3, 5, 0),
            (5, 1, 5),
            (5, 3, 1),
            (6, 2, 3),
            (6, 3, 2),
            (2, 10, 0),
            (10, 2, 5),
            (10, 5, 2),
            (-2, 3, -1),
            (-3, 2, -2),
            (-3, 5, -1),
            (-5, 3, -2),
            (2, -3, -1),
            (3, -2, -2),
            (3, -5, -1),
            (5, -3, -2),
            (-2, -3, 0),
            (-3, -2, 1),
            (-3, -5, 0),
            (-5, -3, 1),
            (0, 1, 1, 0),
            (1, 1, 1, 1),
            (15, 3, 5, 1),
        ),
    },
    {
        'name': 'mod',
        'op': operator.mod,
        'symbol': '%',
        'commutative': False,
        'guard': lambda a, b: b != 0,
        'test': (
            (-0.5, 0),
            (0.5, 0),
            (1, 0),
            (-1, 0),
            (2, 0),
            (-2, 0),
            (3, 0),
            (-3, 0),
            (7, 0),
            (-7, 0),
            (0, 1, 0),
            (0.2, 10, 0.2),
            (1, 2, 1),
            (2, 1, 0),
            (2, 3, 2),
            (3, 2, 1),
            (3, 5, 3),
            (5, 1, 0),
            (5, 3, 2),
            (6, 2, 0),
            (6, 3, 0),
            (2, 10, 2),
            (10, 2, 0),
            (10, 5, 0),
            (-2, 3, 1),
            (-3, 2, 1),
            (-3, 5, 2),
            (-5, 3, 1),
            (2, -3, -1),
            (3, -2, -1),
            (3, -5, -2),
            (5, -3, -1),
            (-2, -3, -2),
            (-3, -2, -1),
            (-3, -5, -3),
            (-5, -3, -2),
            (0, 1, 1, 0),
            (1, 1, 1, 0),
            (15, 3, 5, 0),
        ),
    },
    {
        'name': 'divmod',
        'op': divmod,
        'symbol': 'divmod',
        'guard': lambda a, b: b != 0,
        'test': (
            (-0.5, (1, 0)),
            (0.5, (1, 0)),
            (1, (1, 0)),
            (-1, (1, 0)),
            (2, (1, 0)),
            (-2, (1, 0)),
            (3, (1, 0)),
            (-3, (1, 0)),
            (7, (1, 0)),
            (-7, (1, 0)),
            (0, 1, (0, 0)),
            (0.2, 10, (0, 0.2)),
            (1, 2, (0, 1)),
            (2, 1, (2, 0)),
            (2, 3, (0, 2)),
            (3, 2, (1, 1)),
            (3, 5, (0, 3)),
            (5, 1, (5, 0)),
            (5, 3, (1, 2)),
            (6, 2, (3, 0)),
            (6, 3, (2, 0)),
            (2, 10, (0, 2)),
            (10, 2, (5, 0)),
            (10, 5, (2, 0)),
            (-2, 3, (-1, 1)),
            (-3, 2, (-2, 1)),
            (-3, 5, (-1, 2)),
            (-5, 3, (-2, 1)),
            (2, -3, (-1, -1)),
            (3, -2, (-2, -1)),
            (3, -5, (-1, -2)),
            (5, -3, (-2, -1)),
            (-2, -3, (0, -2)),
            (-3, -2, (1, -1)),
            (-3, -5, (0, -3)),
            (-5, -3, (1, -2)),
        ),
    },
    {
        'name': 'pow',
        'op': operator.pow,
        'symbol': '**',
        'commutative': False,
        'identity': 1,
        'test': (
            (0, 1),
            # (-0.5, 0.25),
            # (0.5, 0.25),
            (1, 1),
            (-1, -1),
            (2, 4),
            (-2, 0.25),
            (3, 27),
            (7, 823543),
            (0, 0, 1),
            (0, 1, 0),
            (1, 1, 1),
            (1, -1, 1),
            (-1, -1, -1),
            (2, 3, 8),
            (2, -3, 0.125),
            (-2, 3, -8),
            (-2, -3, -0.125),
            (3, 5, 243),
            (-3, 5, -243),
            (0, 0, 0, 1),
            (1, 0, 0, 1),
            (2, 3, 5, 32768),
        ),
    },
    {
        'name': 'bit_lshift',
        'op': operator.lshift,
        'symbol': '<<',
        'commutative': False,
        'identity': 0,
        'guard': lambda a, b: b >= 0,
        'test': (
            (0, 0),
            (1, 2),
            (2, 8),
            (3, 24),
            (7, 896),
            (0, 0, 0),
            (0, 1, 0),
            (1, 0, 1),
            (1, 1, 2),
            (2, 3, 16),
            (-2, 3, -16),
            (3, 5, 96),
            (-3, 5, -96),
            (0, 0, 0, 0),
            (1, 0, 0, 1),
            (2, 3, 5, 512),
        ),
    },
    {
        'name': 'bit_rshift',
        'op': operator.rshift,
        'symbol': '>>',
        'commutative': False,
        'identity': 0,
        'guard': lambda a, b: b >= 0,
        'test': (
            (0, 0),
            (1, 0),
            (2, 0),
            (3, 0),
            (7, 0),
            (0, 0, 0),
            (0, 1, 0),
            (1, 0, 1),
            (1, 1, 0),
            (2, 3, 0),
            (-2, 3, -1),
            (3, 5, 0),
            (-3, 5, -1),
            (128, 1, 64),
            (256, 1, 128),
            (512, 1, 256),
            (512, 2, 128),
            (512, 3, 64),
            (512, 4, 32),
            (0, 0, 0, 0),
            (1, 0, 0, 1),
            (2, 3, 5, 0),
        ),
    },
    {
        'name': 'bit_and',
        'op': operator.and_,
        'symbol': '&',
        'commutative': True,
        'test': (
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (7, 7),
            (0, 0, 0),
            (0, 1, 0),
            (1, 0, 0),
            (1, 1, 1),
            (2, 3, 2),
            (-2, 3, 2),
            (3, 5, 1),
            (-3, 5, 5),
            (127, 64, 64),
            (128, 64, 0),
            (255, 128, 128),
            (256, 128, 0),
            (511, 256, 256),
            (512, 256, 0),
            (0, 0, 0, 0),
            (1, 0, 0, 0),
            (2, 3, 5, 0),
        ),
    },
    {
        'name': 'bit_xor',
        'op': operator.xor,
        'symbol': '^',
        'commutative': True,
        'test': (
            (0, 0),
            (1, 0),
            (2, 0),
            (3, 0),
            (7, 0),
            (0, 0, 0),
            (0, 1, 1),
            (1, 1, 0),
            (2, 3, 1),
            (-2, 3, -3),
            (3, 5, 6),
            (-3, 5, -8),
            (127, 64, 63),
            (128, 64, 192),
            (255, 128, 127),
            (256, 128, 384),
            (511, 256, 255),
            (512, 256, 768),
            (0, 0, 0, 0),
            (1, 0, 0, 1),
            (2, 3, 5, 4),
        ),
    },
    {
        'name': 'bit_or',
        'op': operator.or_,
        'symbol': '|',
        'commutative': True,
        'test': (
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (7, 7),
            (0, 0, 0),
            (0, 1, 1),
            (1, 0, 1),
            (1, 1, 1),
            (2, 3, 3),
            (-2, 3, -1),
            (3, 5, 7),
            (-3, 5, -3),
            (127, 64, 127),
            (128, 64, 192),
            (255, 128, 255),
            (256, 128, 384),
            (511, 256, 511),
            (512, 256, 768),
            (0, 0, 0, 0),
            (1, 0, 0, 1),
            (2, 3, 5, 7),
        ),
    },
    {
        'name': 'lt',
        'op': operator.lt,
        'symbol': '<',
        'mirror': False,
        'commutative': False,
        'test': (
            (0, False),
            (-1, False),
            (1, False),
            (-2, False),
            (2, False),
            (-3, False),
            (3, False),
            (-7, False),
            (7, False),
            (0, 0, False),
            (0, 1, True),
            (1, 0, False),
            (1, 1, False),
            (2, 3, True),
            (3, 2, False),
            (-2, 3, True),
            (3, -2, False),
            (3, 5, True),
            (5, 3, False),
            (-3, 5, True),
            (5, -3, False),
        ),
    },
    {
        'name': 'le',
        'op': operator.le,
        'symbol': '<=',
        'mirror': False,
        'commutative': False,
        'test': (
            (0, True),
            (-1, True),
            (1, True),
            (-2, True),
            (2, True),
            (-3, True),
            (3, True),
            (-7, True),
            (7, True),
            (0, 0, True),
            (0, 1, True),
            (1, 0, False),
            (1, 1, True),
            (2, 3, True),
            (3, 2, False),
            (-2, 3, True),
            (3, -2, False),
            (3, 5, True),
            (5, 3, False),
            (-3, 5, True),
            (5, -3, False),
        ),
    },
    {
        'name': 'eq',
        'op': operator.eq,
        'symbol': '==',
        'mirror': False,
        'commutative': False,
        'test': (
            (0, True),
            (-1, True),
            (1, True),
            (-2, True),
            (2, True),
            (-3, True),
            (3, True),
            (-7, True),
            (7, True),
            (0, 0, True),
            (0, 1, False),
            (1, 0, False),
            (1, 1, True),
            (2, 3, False),
            (3, 2, False),
            (-2, 3, False),
            (3, -2, False),
            (3, 5, False),
            (5, 3, False),
            (-3, 5, False),
            (5, -3, False),
        ),
    },
    {
        'name': 'ne',
        'op': operator.ne,
        'symbol': '!=',
        'mirror': False,
        'commutative': False,
        'test': (
            (0, False),
            (-1, False),
            (1, False),
            (-2, False),
            (2, False),
            (-3, False),
            (3, False),
            (-7, False),
            (7, False),
            (0, 0, False),
            (0, 1, True),
            (1, 0, True),
            (1, 1, False),
            (2, 3, True),
            (3, 2, True),
            (-2, 3, True),
            (3, -2, True),
            (3, 5, True),
            (5, 3, True),
            (-3, 5, True),
            (5, -3, True),
        ),
    },
    {
        'name': 'gt',
        'op': operator.gt,
        'symbol': '>',
        'mirror': False,
        'commutative': False,
        'test': (
            (0, False),
            (-1, False),
            (1, False),
            (-2, False),
            (2, False),
            (-3, False),
            (3, False),
            (-7, False),
            (7, False),
            (0, 0, False),
            (0, 1, False),
            (1, 0, True),
            (1, 1, False),
            (2, 3, False),
            (3, 2, True),
            (-2, 3, False),
            (3, -2, True),
            (3, 5, False),
            (5, 3, True),
            (-3, 5, False),
            (5, -3, True),
        ),
    },
    {
        'name': 'ge',
        'op': operator.ge,
        'symbol': '>=',
        'mirror': False,
        'commutative': False,
        'test': (
            (0, True),
            (-1, True),
            (1, True),
            (-2, True),
            (2, True),
            (-3, True),
            (3, True),
            (-7, True),
            (7, True),
            (0, 0, True),
            (0, 1, False),
            (1, 0, True),
            (1, 1, True),
            (2, 3, False),
            (3, 2, True),
            (-2, 3, False),
            (3, -2, True),
            (3, 5, False),
            (5, 3, True),
            (-3, 5, False),
            (5, -3, True),
        ),
    },
)
_SPECIAL_UNARY_OPERATORS = (
    {
        'name': 'neg',
        'op': operator.neg,
        'symbol': '-',
        'test': (
            (0, 0),
            (0.5, -0.5),
            (-0.5, 0.5),
            (-1, 1),
            (1, -1),
            (-13, 13),
            (13, -13),
        ),
    },
    {
        'name': 'pos',
        'op': operator.pos,
        'symbol': '+',
        'test': (
            (0, 0),
            (0.5, 0.5),
            (-0.5, -0.5),
            (-1, -1),
            (1, 1),
            (-13, -13),
            (13, 13),
        ),
    },
    {
        'name': 'abs',
        'op': abs,
        'symbol': 'abs',
        'test': (
            (0, 0),
            (0.5, 0.5),
            (-0.5, 0.5),
            (-1, 1),
            (1, 1),
            (-13, 13),
            (13, 13),
        ),
    },
    {
        'name': 'bit_invert',
        'op': operator.invert,
        'symbol': '~',
        'test': (
            (0, -1),
            (-1, 0),
            (1, -2),
            (-13, 12),
            (13, -14),
        ),
    },
    {
        'name': 'complex',
        'op': complex,
        'symbol': 'complex',
        'magic': False,
        'test': (
            (0, 0),
            (-1, -1),
            (1, 1),
            (-13, -13),
            (13, 13),
        ),
    },
    {
        'name': 'int',
        'op': int,
        'symbol': 'int',
        'magic': False,
        'test': (
            (0, 0),
            (-1, -1),
            (1, 1),
            (-13, -13),
            (13, 13),
        ),
    },
    {
        'name': 'float',
        'op': float,
        'symbol': 'float',
        'magic': False,
        'test': (
            (0, 0),
            (-1, -1),
            (1, 1),
            (-13, -13),
            (13, 13),
        ),
    },
)


def _un_spec_params():
    for op_spec in _SPECIAL_UNARY_OPERATORS:
        for test_spec in op_spec.get('test', []):
            yield (op_spec, *test_spec)


def _bin_spec_params(test_len):
    tl = test_len + 1
    for op_spec in _SPECIAL_BINARY_OPERATORS:
        commutative = op_spec.get('commutative', False)
        wrapper = op_spec.get('wrapper', None)
        for test_spec in op_spec.get('test', []):
            if len(test_spec) != tl:
                continue
            if commutative:
                yield from ((op_spec, *(map(wrapper, test_perm) if wrapper else test_perm), test_spec[-1]) for test_perm in itertools.permutations(test_spec[:-1], test_len))
            else:
                yield (op_spec, *(map(wrapper, test_spec[:-1]) if wrapper else test_spec[:-1]), test_spec[-1])


def _samples():
    return [-13, -9, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 3, 9, 13]


########################################################################
# Vars

@pytest.mark.parametrize('shear,name', [(X, 'X'), (Y, 'Y'), (Z, 'Z')])
def test_shear_repr(shear, name):
    assert repr(shear) == f'<ShearVar {name}>'


def test_shear_attr():
    class Bar:
        t = 2
    class Foo:
        s = 1
        bar = Bar()
    foo = Foo()
    assert X.attr('s')(foo) == 1
    assert X.attr('bar.t')(foo) == 2


def test_shear_getitem():
    m = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
    assert X['a'](m) == 1
    assert X['b', 'c'](m) == 2
    assert X['b', 'd', 'e'](m) == 3


def test_shear_contains():
    s = {1}
    assert X.contains(1)(s)
    assert not X.contains(2)(s)


def test_shear_membership_raises_error():
    with pytest.raises(NotImplementedError, match=r'unsupported.*instead'):
        assert 1 in X


########################################################################
# Ops

def test_shearop_missing_arg():
    func = X + 3
    with pytest.raises(TypeError) as excinfo:
        func()
    assert """missing 1 required positional argument""" in str(excinfo.value)


def test_shearop_excess_args():
    func = X + 3
    with pytest.raises(TypeError) as excinfo:
        func(3, 4)
    assert """takes 1 positional argument but 2 were given""" in str(excinfo.value)


########################################################################
# Unary ops

def test_shearunop_repr():
    func = -X
    assert repr(func) == '<ShearUnOp -X>'


def test_shearunop_str():
    shear = ShearUnOp(int, 'int', X, repr_call=True)
    assert str(shear) == 'int(X)'


def test_shearunop_nested():
    func = -(-X)
    assert func(3) == 3


def test_shearunop_param_not_shearbase():
    with pytest.raises(TypeError) as excinfo:
        ShearUnOp(operator.neg, '-', 3)
    assert str(excinfo.value) == "ShearUnOp argument 'param' must be an instance of ShearBase"


@pytest.mark.parametrize('a', [-2, -1, 0, 1, 2, 66j, (23, 4), {'k': 3}])
def test_shearunop_identity(a):
    res = X(a)
    assert res == a
    assert res is a 


@pytest.mark.parametrize('spec,a,x', _un_spec_params())
def test_shearunop_fwd(spec, a, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    magic = spec.get('magic', True)
    eval_str = f"{symbol}(X)"
    for func in [*([eval(eval_str)] if magic else []), getattr(X, name)()]:
        assert func(a) == x


########################################################################
# Binary ops

def test_shearbinop_repr():
    func = X + 3
    assert repr(func) == '<ShearBinOp X + 3>'


def test_shearbinop_param_not_shearbase():
    with pytest.raises(TypeError) as excinfo:
        ShearBinOp(operator.neg, '-', 3, 4)
    assert str(excinfo.value) == "At least one of ShearBinOp arguments 'left' or 'right' must be an instance of ShearBase"


def test_shearbinop_nested():
    func = (X + 3) * (Y + 7)
    assert func(5, 9) == 128


def test_shearbinop_nested_str():
    func = (X + 3) * (Y + 7)
    assert str(func) == '(X + 3) * (Y + 7)'
    func = (3 + X) * (7 + Y)
    assert str(func) == '(3 + X) * (7 + Y)'
    func = divmod(X, Y)
    assert str(func) == 'divmod(X, Y)'


@pytest.mark.parametrize('spec,a,b,x', _bin_spec_params(2))
def test_shearbinop_fwd(spec, a, b, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    eval_str = f"{symbol}(X, {b})" if _RE_FUNC.search(symbol) else f"X {symbol} ({b})"
    for func in [eval(eval_str), getattr(X, name)(b)]:
        assert func(a) == x


@pytest.mark.parametrize('spec,a,b,x', _bin_spec_params(2))
def test_shearbinop_rev(spec, a, b, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    if not spec.get('mirror', True):
        return
    eval_str = f"{symbol}({a}, X)" if _RE_FUNC.search(symbol) else f"({a}) {symbol} X"
    for func in [eval(eval_str), getattr(X, f"{name}_r")(a)]:
        assert func(b) == x


@pytest.mark.parametrize('spec,a,x', _bin_spec_params(1))
def test_shearbinop_same(spec, a, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    guard = spec.get('guard', lambda a, b: True)
    if not guard(a, a):
        return
    eval_str = f"{symbol}(X, X)" if _RE_FUNC.search(symbol) else f"X {symbol} X"
    for func in [eval(eval_str), getattr(X, name)(X)]:
        assert func(a) == x


@pytest.mark.parametrize('spec,a,b,x', _bin_spec_params(2))
def test_shearbinop_diff(spec, a, b, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    eval_str = f"{symbol}(X, Y)" if _RE_FUNC.search(symbol) else f"X {symbol} Y"
    for func in [eval(eval_str), getattr(X, name)(Y)]:
        assert func(a, b) == x


# FIXME this test is broken(?)
@pytest.mark.parametrize('spec,a,x', _bin_spec_params(1))
def test_shearbinop_same_op_fwd(spec, a, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    ident = spec.get('identity', None)
    # FIXME
    if ident is None:
        return
    guard = spec.get('guard', lambda a, b: True)
    if not guard(a, a):
        return
    if spec.get('wrapper', False):
        return
    expected_str = f"{symbol}({symbol}({a}, {a}), {ident})" if _RE_FUNC.search(symbol) else f"(({a}) {symbol} ({a})) {symbol} ({ident})"
    expected = eval(expected_str)
    eval_str = f"{symbol}({symbol}(X, X), {ident})" if _RE_FUNC.search(symbol) else f"(X {symbol} X) {symbol} ({ident})"
    for func in [eval(eval_str), getattr(getattr(X, name)(X), name)(ident)]:
        assert func(a) == expected


# FIXME this test is broken(?)
@pytest.mark.parametrize('spec,a,x', _bin_spec_params(1))
def test_shearbinop_same_op_rev(spec, a, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    ident = spec.get('identity', None)
    # FIXME
    if ident is None:
        return
    guard = spec.get('guard', lambda a, b: True)
    if not guard(a, a):
        return
    if spec.get('wrapper', False):
        return
    expected_str = f"{symbol}({ident}, {symbol}({a}, {a}))" if _RE_FUNC.search(symbol) else f"({ident}) {symbol} (({a}) {symbol} ({a}))"
    expected = eval(expected_str)
    eval_str = f"{symbol}({ident}, {symbol}(X, X))" if _RE_FUNC.search(symbol) else f"({ident}) {symbol} (X {symbol} X)"
    for func in [eval(eval_str), getattr(getattr(X, f"{name}_r")(X), f"{name}_r")(ident)]:
        assert func(a) == expected


# FIXME this test is broken(?)
@pytest.mark.parametrize('spec,a,b,x', _bin_spec_params(2))
def test_shearbinop_1_same_op_fwd(spec, a, b, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    ident = spec.get('identity', None)
    # FIXME
    if ident is None:
        return
    guard = spec.get('guard', lambda a, b: True)
    if not (guard(a, b) and guard(b, a)):
        return
    if spec.get('wrapper', False):
        return
    expected_str = f"{symbol}({symbol}({a}, {b}), {a})" if _RE_FUNC.search(symbol) else f"(({a}) {symbol} ({b})) {symbol} ({a})"
    expected = eval(expected_str)
    eval_str = f"{symbol}({symbol}(X, {b}), X)" if _RE_FUNC.search(symbol) else f"(X {symbol} ({b})) {symbol} X"
    for func in [eval(eval_str), getattr(getattr(X, name)(b), name)(X)]:
        assert func(a) == expected


@pytest.mark.parametrize('spec,a,b,c,x', _bin_spec_params(3))
def test_shearbinop_1_diff_op_fwd(spec, a, b, c, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    guard = spec.get('guard', lambda a, b: True)
    if not (guard(a, b) and guard(b, c)):
        return
    eval_str = f"{symbol}({symbol}(X, {b}), Y)" if _RE_FUNC.search(symbol) else f"(X {symbol} ({b})) {symbol} Y"
    for func in [eval(eval_str), getattr(getattr(X, name)(b), name)(Y)]:
        assert func(a, c) == x


@pytest.mark.parametrize('spec,a,b,c,x', _bin_spec_params(3))
def test_shearbinop_2_diff_op_fwd(spec, a, b, c, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    guard = spec.get('guard', lambda a, b: True)
    if not (guard(a, b) and guard(b, c)):
        return
    if spec.get('wrapper', False):
        return
    eval_str = f"{symbol}({symbol}(X, Y), {c})" if _RE_FUNC.search(symbol) else f"(X {symbol} Y) {symbol} ({c})"
    for func in [eval(eval_str), getattr(getattr(X, name)(Y), name)(c)]:
        assert func(a, b) == x


@pytest.mark.parametrize('spec,a,b,c,x', _bin_spec_params(3))
def test_shearbinop_3_diff_op_fwd(spec, a, b, c, x):
    name = spec['name']
    op = spec['op']
    symbol = spec['symbol']
    guard = spec.get('guard', lambda a, b: True)
    if not (guard(a, b) and guard(b, c)):
        return
    if spec.get('wrapper', False):
        return
    eval_str = f"{symbol}({symbol}(X, Y), Z)" if _RE_FUNC.search(symbol) else f"(X {symbol} Y) {symbol} Z"
    for func in [eval(eval_str), getattr(getattr(X, name)(Y), name)(Z)]:
        assert func(a, b, c) == x
