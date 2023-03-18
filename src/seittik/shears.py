"""
Shears: lambda shortcuts.

A *shear* is an object that creates a partial function when any operator
is applied to it.

A shear can be used to succinctly replace `lambda` in many cases.

```{eval-rst}
.. ipython::
    :reset_history:

    In [1]: from seittik.shears import ShearVar

    In [1]: X = ShearVar('X')

    In [1]: X
    Out[1]: <ShearVar X>

    In [1]: list(map(X * 3, [1, 2, 3, 4, 5]))
    Out[1]: [3, 6, 9, 12, 15]
```

Shears compose with one another as well, to arbitrary depth.

Any shear created with the same name is treated identically; otherwise
they are treated as separate parameters to a partial function.

```{eval-rst}
.. ipython::
    :reset_history:

    In [1]: from functools import reduce

    In [1]: from seittik.shears import ShearVar

    In [1]: X = ShearVar('X')

    In [1]: X
    Out[1]: <ShearVar X>

    In [1]: double = X + X

    In [1]: double
    Out[1]: <ShearBinOp X + X>

    In [1]: double(5)
    Out[1]: 10

    In [1]: Y = ShearVar('Y')

    In [1]: Y
    Out[1]: <ShearVar Y>

    In [1]: reduce(X + Y, [1, 2, 3, 4, 5])
    Out[1]: 15

    In [1]: f = X + X / Y + Y

    In [1]: f
    Out[1]: <ShearBinOp (X + (X / Y)) + Y>

    In [1]: f(6, 3)
    Out[1]: 11.0
```

Shears are much more powerful when combined with *pipes*; see
{py:mod}`seittik.pipes`.
"""
import operator


__all__ = ('ShearVar', 'X', 'Y', 'Z')


def shear_names(*objs):
    ret = []
    for obj in objs:
        ret.extend((n for n in obj.names if n not in ret) if isinstance(obj, ShearBase) else [])
    return tuple(ret)


class ShearBase:
    ####################################################################
    # Numeric binary ops

    def __add__(self, other):
        return ShearBinOp(operator.add, '+', self, other, repr_call=False)

    def add(self, other):
        return ShearBinOp(operator.add, '+', self, other, repr_call=False)

    def __radd__(self, other):
        return ShearBinOp(operator.add, '+', other, self, repr_call=False)

    def add_r(self, other):
        return ShearBinOp(operator.add, '+', other, self, repr_call=False)

    def __sub__(self, other):
        return ShearBinOp(operator.sub, '-', self, other, repr_call=False)

    def sub(self, other):
        return ShearBinOp(operator.sub, '-', self, other, repr_call=False)

    def __rsub__(self, other):
        return ShearBinOp(operator.sub, '-', other, self, repr_call=False)

    def sub_r(self, other):
        return ShearBinOp(operator.sub, '-', other, self, repr_call=False)

    def __mul__(self, other):
        return ShearBinOp(operator.mul, '*', self, other, repr_call=False)

    def mul(self, other):
        return ShearBinOp(operator.mul, '*', self, other, repr_call=False)

    def __rmul__(self, other):
        return ShearBinOp(operator.mul, '*', other, self, repr_call=False)

    def mul_r(self, other):
        return ShearBinOp(operator.mul, '*', other, self, repr_call=False)

    def __matmul__(self, other):
        return ShearBinOp(operator.matmul, '@', self, other, repr_call=False)

    def matmul(self, other):
        return ShearBinOp(operator.matmul, '@', self, other, repr_call=False)

    def __rmatmul__(self, other):
        return ShearBinOp(operator.matmul, '@', other, self, repr_call=False)

    def matmul_r(self, other):
        return ShearBinOp(operator.matmul, '@', other, self, repr_call=False)

    def __truediv__(self, other):
        return ShearBinOp(operator.truediv, '/', self, other, repr_call=False)

    def truediv(self, other):
        return ShearBinOp(operator.truediv, '/', self, other, repr_call=False)

    def __rtruediv__(self, other):
        return ShearBinOp(operator.truediv, '/', other, self, repr_call=False)

    def truediv_r(self, other):
        return ShearBinOp(operator.truediv, '/', other, self, repr_call=False)

    def __floordiv__(self, other):
        return ShearBinOp(operator.floordiv, '//', self, other, repr_call=False)

    def floordiv(self, other):
        return ShearBinOp(operator.floordiv, '//', self, other, repr_call=False)

    def __rfloordiv__(self, other):
        return ShearBinOp(operator.floordiv, '//', other, self, repr_call=False)

    def floordiv_r(self, other):
        return ShearBinOp(operator.floordiv, '//', other, self, repr_call=False)

    def __mod__(self, other):
        return ShearBinOp(operator.mod, '%', self, other, repr_call=False)

    def mod(self, other):
        return ShearBinOp(operator.mod, '%', self, other, repr_call=False)

    def __rmod__(self, other):
        return ShearBinOp(operator.mod, '%', other, self, repr_call=False)

    def mod_r(self, other):
        return ShearBinOp(operator.mod, '%', other, self, repr_call=False)

    def __divmod__(self, other):
        return ShearBinOp(divmod, 'divmod', self, other, repr_call=True)

    def divmod(self, other):
        return ShearBinOp(divmod, 'divmod', self, other, repr_call=True)

    def __rdivmod__(self, other):
        return ShearBinOp(divmod, 'divmod', other, self, repr_call=True)

    def divmod_r(self, other):
        return ShearBinOp(divmod, 'divmod', other, self, repr_call=True)

    def __pow__(self, other):
        return ShearBinOp(operator.pow, '**', self, other, repr_call=False)

    def pow(self, other):
        return ShearBinOp(operator.pow, '**', self, other, repr_call=False)

    def __rpow__(self, other):
        return ShearBinOp(operator.pow, '**', other, self, repr_call=False)

    def pow_r(self, other):
        return ShearBinOp(operator.pow, '**', other, self, repr_call=False)

    # Bit ops

    def __lshift__(self, other):
        return ShearBinOp(operator.lshift, '<<', self, other, repr_call=False)

    def bit_lshift(self, other):
        return ShearBinOp(operator.lshift, '<<', self, other, repr_call=False)

    def __rlshift__(self, other):
        return ShearBinOp(operator.lshift, '<<', other, self, repr_call=False)

    def bit_lshift_r(self, other):
        return ShearBinOp(operator.lshift, '<<', other, self, repr_call=False)

    def __rshift__(self, other):
        return ShearBinOp(operator.rshift, '>>', self, other, repr_call=False)

    def bit_rshift(self, other):
        return ShearBinOp(operator.rshift, '>>', self, other, repr_call=False)

    def __rrshift__(self, other):
        return ShearBinOp(operator.rshift, '>>', other, self, repr_call=False)

    def bit_rshift_r(self, other):
        return ShearBinOp(operator.rshift, '>>', other, self, repr_call=False)

    def __and__(self, other):
        return ShearBinOp(operator.and_, '&', self, other, repr_call=False)

    def bit_and(self, other):
        return ShearBinOp(operator.and_, '&', self, other, repr_call=False)

    def __rand__(self, other):
        return ShearBinOp(operator.and_, '&', other, self, repr_call=False)

    def bit_and_r(self, other):
        return ShearBinOp(operator.and_, '&', other, self, repr_call=False)

    def __xor__(self, other):
        return ShearBinOp(operator.xor, '^', self, other, repr_call=False)

    def bit_xor(self, other):
        return ShearBinOp(operator.xor, '^', self, other, repr_call=False)

    def __rxor__(self, other):
        return ShearBinOp(operator.xor, '^', other, self, repr_call=False)

    def bit_xor_r(self, other):
        return ShearBinOp(operator.xor, '^', other, self, repr_call=False)

    def __or__(self, other):
        return ShearBinOp(operator.or_, '|', self, other, repr_call=False)

    def bit_or(self, other):
        return ShearBinOp(operator.or_, '|', self, other, repr_call=False)

    def __ror__(self, other):
        return ShearBinOp(operator.or_, '|', other, self, repr_call=False)

    def bit_or_r(self, other):
        return ShearBinOp(operator.or_, '|', other, self, repr_call=False)

    ####################################################################
    # Comparison ops

    def __lt__(self, other):
        return ShearBinOp(operator.lt, '<', self, other, repr_call=False)

    def lt(self, other):
        return ShearBinOp(operator.lt, '<', self, other, repr_call=False)

    def __le__(self, other):
        return ShearBinOp(operator.le, '<=', self, other, repr_call=False)

    def le(self, other):
        return ShearBinOp(operator.le, '<=', self, other, repr_call=False)

    def __eq__(self, other):
        return ShearBinOp(operator.eq, '==', self, other, repr_call=False)

    def eq(self, other):
        return ShearBinOp(operator.eq, '==', self, other, repr_call=False)

    def __ne__(self, other):
        return ShearBinOp(operator.ne, '!=', self, other, repr_call=False)

    def ne(self, other):
        return ShearBinOp(operator.ne, '!=', self, other, repr_call=False)

    def __gt__(self, other):
        return ShearBinOp(operator.gt, '>', self, other, repr_call=False)

    def gt(self, other):
        return ShearBinOp(operator.gt, '>', self, other, repr_call=False)

    def __ge__(self, other):
        return ShearBinOp(operator.ge, '>=', self, other, repr_call=False)

    def ge(self, other):
        return ShearBinOp(operator.ge, '>=', self, other, repr_call=False)

    ####################################################################
    # Numeric unary ops

    def __neg__(self):
        return ShearUnOp(operator.neg, '-', self, repr_call=False)

    def neg(self):
        return ShearUnOp(operator.neg, '-', self, repr_call=False)

    def __pos__(self):
        return ShearUnOp(operator.pos, '+', self, repr_call=False)

    def pos(self):
        return ShearUnOp(operator.pos, '+', self, repr_call=False)

    def __abs__(self):
        return ShearUnOp(abs, 'abs', self, repr_call=True)

    def abs(self):
        return ShearUnOp(abs, 'abs', self, repr_call=True)

    def __invert__(self):
        return ShearUnOp(operator.invert, '~', self, repr_call=False)

    def bit_invert(self):
        return ShearUnOp(operator.invert, '~', self, repr_call=False)

    ####################################################################
    # Numeric types

    def complex(self):
        return ShearUnOp(complex, 'complex', self, repr_call=True)

    def int(self):
        return ShearUnOp(int, 'int', self, repr_call=True)

    def float(self):
        return ShearUnOp(float, 'float', self, repr_call=True)

    ####################################################################
    # Attribute access

    def attr(self, *args):
        argstr = '.'.join(args)
        return ShearUnOp(operator.attrgetter(argstr), 'attr', self, repr_call=True)

    ####################################################################
    # Containers

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        itemstr = ''.join(f'[{x!r}]' for x in item)
        def shear_getitem(v):
            ret = v
            for x in item:
                ret = ret[x]
            return ret
        shear_getitem.__doc__ = f"""Return v{itemstr}"""
        return shear_getitem

    # __contains__ coerces its output to a boolean, so we can't create a
    # magic `item in X`
    def contains(self, item):
        def shear_contains(v):
            return item in v
        shear_contains.__doc__ = f'Return {item!r} in v'
        return shear_contains


class ShearVar(ShearBase):
    """
    A shear for creating partial functions.

    See the module docstring for full details.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    def __str__(self):
        return self.name

    def __call__(self, v):
        """
        Identity: return the argument unchanged.
        """
        return v

    @property
    def names(self):
        return (self.name,)


class ShearOp(ShearBase):
    def _process_args(self, args, kwargs):
        ret = kwargs.copy()
        arg_iter = iter(args)
        names = self.names
        for name in names:
            if name in ret:
                continue
            try:
                ret[name] = next(arg_iter)
            except StopIteration as exc:
                raise TypeError(f"{self!r}() missing 1 required positional argument: {name!r}") from exc
        arg_leftover = list(arg_iter)
        if arg_leftover:
            arg_total = len(ret) + len(arg_leftover)
            raise TypeError(
                    f"{self!r}() takes {len(names)} positional argument{'' if len(names) == 1 else 's'}"
                    f" but {arg_total} {'was' if arg_total == 1 else 'were'} given"
            )
        return ret


class ShearUnOp(ShearOp):
    """
    A shear representing a partial unary operation.

    See the module docstring for full details.
    """
    def __init__(self, op, op_str, param, repr_call=False):
        if not isinstance(param, ShearBase):
            raise TypeError("ShearUnOp argument 'param' must be an instance of ShearBase")
        self.op = op
        try:
            self.op_name = op.__name__
        except AttributeError:
            self.op_name = op.__class__.__name__
        self.op_str = op_str
        self.param = param
        self.repr_call = repr_call

    def __repr__(self):
        return f"<{self.__class__.__name__} {self}>"

    def __str__(self):
        if self.repr_call or isinstance(self.param, ShearOp):
            return f'{self.op_str}({self.param})'
        return f'{self.op_str}{self.param}'

    def __call__(self, *args, **kwargs):
        processed_args = self._process_args(args, kwargs)
        match self.param:
            case ShearOp():
                ret = self.param(**processed_args)
            case ShearVar():
                ret = processed_args[self.param.name]
            case _: # pragma: no cover
                # This should be unreachable if we were constructed
                # correctly and `param` was never modified
                raise TypeError("ShearUnOp attribute 'param' is not an instance of ShearBase")
        return self.op(ret)

    @property
    def names(self):
        return self.param.names


class ShearBinOp(ShearOp):
    """
    A shear representing a partial binary operation.

    See the module docstring for full details.
    """
    def __init__(self, op, op_str, left, right, repr_call=False):
        if not isinstance(left, ShearBase) and not isinstance(right, ShearBase):
            raise TypeError(
                    f"At least one of {self.__class__.__name__} arguments"
                    " 'left' or 'right' must be an instance of ShearBase"
            )
        self.op = op
        self.op_name = op.__name__
        self.op_str = op_str
        self.left = left
        self.right = right
        self.repr_call = repr_call

    def __repr__(self):
        return f"<{self.__class__.__name__} {self}>"

    def __str__(self):
        match self.left:
            case ShearOp():
                left = f'({self.left})'
            case ShearVar():
                left = str(self.left)
            case _:
                left = repr(self.left)
        match self.right:
            case ShearOp():
                right = f'({self.right})'
            case ShearVar():
                right = str(self.right)
            case _:
                right = repr(self.right)
        if self.repr_call:
            return f'{self.op_str}({left}, {right})'
        return f'{left} {self.op_str} {right}'

    def __call__(self, *args, **kwargs):
        processed_args = self._process_args(args, kwargs)
        match self.left:
            case ShearOp():
                ret_left = self.left(**processed_args)
            case ShearVar():
                ret_left = processed_args[self.left.name]
            case _:
                ret_left = self.left
        match self.right:
            case ShearOp():
                ret_right = self.right(**processed_args)
            case ShearVar():
                ret_right = processed_args[self.right.name]
            case _:
                ret_right = self.right
        return self.op(ret_left, ret_right)

    @property
    def names(self):
        return shear_names(self.left, self.right)


X = ShearVar('X')
"""
A shortcut for `ShearVar('X')`
"""

Y = ShearVar('Y')
"""
A shortcut for `ShearVar('Y')`
"""

Z = ShearVar('Z')
"""
A shortcut for `ShearVar('Z')`
"""
