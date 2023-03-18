from seittik.utils.structutils import calc_struct_input


def test_calc_struct_input():
    assert calc_struct_input('4i6sxx') == 10
