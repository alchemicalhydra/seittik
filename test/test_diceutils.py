import pytest


from seittik.utils.diceutils import blunt_roll_result, DiceRoll, parse_dice_str


# blunt_roll_result

def test_blunt_roll_result():
    assert blunt_roll_result(0) == 0
    assert blunt_roll_result(1) == 0
    assert blunt_roll_result(2) == 1
    assert blunt_roll_result(3) == 1
    assert blunt_roll_result(4) == 1
    assert blunt_roll_result(5) == 1
    assert blunt_roll_result(6) == 2
    assert blunt_roll_result(7) == 2
    assert blunt_roll_result(8) == 2
    assert blunt_roll_result(9) == 2
    assert blunt_roll_result(10) == 4
    assert blunt_roll_result(15) == 4
    assert blunt_roll_result(100) == 4


# parse_dice_str

def test_parse_dice_str():
    assert parse_dice_str('3d6') == (3, 6, 0)
    assert parse_dice_str('1d4-1') == (1, 4, -1)
    assert parse_dice_str('2d12+4') == (2, 12, 4)

def test_parse_dice_str_fail():
    with pytest.raises(ValueError):
        parse_dice_str('meow')


# DiceRoll

def test_diceroll_init_args_str():
    dr = DiceRoll('3d6+2')
    assert dr.num == 3
    assert dr.size == 6
    assert dr.modifier == 2


def test_diceroll_init_args_single_int():
    dr = DiceRoll(6)
    assert dr.num == 1
    assert dr.size == 6
    assert dr.modifier == 0


def test_diceroll_init_args_pair_ints():
    dr = DiceRoll(3, 6)
    assert dr.num == 3
    assert dr.size == 6
    assert dr.modifier == 0


def test_diceroll_init_args_triple_ints():
    dr = DiceRoll(3, 6, 2)
    assert dr.num == 3
    assert dr.size == 6
    assert dr.modifier == 2


def test_diceroll_init_args_bad():
    with pytest.raises(TypeError):
        dr = DiceRoll(3, 6, 8, 3)
    with pytest.raises(TypeError):
        dr = DiceRoll(None)
    with pytest.raises(TypeError):
        dr = DiceRoll()


def test_diceroll_repr():
    dr = DiceRoll(8, 12)
    assert repr(dr) == '<DiceRoll 8d12>'
    dr = DiceRoll(8, 12, 0)
    assert repr(dr) == '<DiceRoll 8d12>'
    dr = DiceRoll(3, 6, 2)
    assert repr(dr) == '<DiceRoll 3d6+2>'
    dr = DiceRoll(4, 3, -1)
    assert repr(dr) == '<DiceRoll 4d3-1>'


def test_diceroll_roll(random_seed_0):
    dr = DiceRoll(3, 6)
    assert dr.roll() == 9
    assert dr.roll() == 12
    assert dr.roll() == 11
    assert dr.roll() == 10
    assert dr.roll() == 10
    assert dr.roll() == 8


def test_diceroll_roll_blunted(random_seed_0):
    dr = DiceRoll(12)
    assert dr.roll(blunt=True) == 2
    assert dr.roll(blunt=True) == 2
    assert dr.roll(blunt=True) == 0
    assert dr.roll(blunt=True) == 1
    assert dr.roll(blunt=True) == 2
    assert dr.roll(blunt=True) == 2
    assert dr.roll(blunt=True) == 2
    assert dr.roll(blunt=True) == 1
    assert dr.roll(blunt=True) == 2
    assert dr.roll(blunt=True) == 2
    assert dr.roll(blunt=True) == 4
    assert dr.roll(blunt=True) == 1
