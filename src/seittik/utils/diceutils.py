import re

from .randutils import SharedRandom
from .sentinels import _MISSING


__all__ = ()


def blunt_roll_result(n):
    """
    Blunt a die result according to Stars Without Number's "Counting Heroic
    Damage" table.
    """
    match n:
        case n if n < 2:
            return 0
        case n if n < 6:
            return 1
        case n if n < 10:
            return 2
        case _:
            return 4


def parse_dice_str(s):
    m = re.search(r'^\s*(\d+)[dD](\d+)(?:\s*([+-]\d+))?\s*$', s)
    if not m:
        raise ValueError(f"{s!r} is not valid dice notation; try `NUMdSIZE` or `NUMdSIZE+MOD` instead")
    return tuple(map(lambda v: int(v) if v is not None else 0, m.groups()))


class DiceRoll:
    def __init__(self, *args, rng=_MISSING):
        self._rng = SharedRandom() if rng is _MISSING else rng
        match args:
            case [str() as s]:
                self.num, self.size, self.modifier = parse_dice_str(s)
            case [int() as size]:
                self.num = 1
                self.size = size
                self.modifier = 0
            case [int(), int()]:
                self.num, self.size = args
                self.modifier = 0
            case [int(), int(), int()]:
                self.num, self.size, self.modifier = args
            case _:
                raise TypeError("Provide a string or 1-3 integers")

    def __repr__(self):
        mod = f"{self.modifier:+}" if self.modifier != 0 else ''
        return f"<DiceRoll {self.num}d{self.size}{mod}>"

    def roll(self, blunt=False):
        ret = 0
        for _ in range(self.num):
            roll_result = self._rng.randint(1, self.size)
            if blunt:
                roll_result = blunt_roll_result(roll_result)
            ret += roll_result
        ret += self.modifier
        return ret
