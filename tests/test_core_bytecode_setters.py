"""
Test setters on instruction class
"""
from itertools import product

import pytest
from eightdad.core.bytecode import Chip8Instruction as Instruction
from tests.util import src_to_pairs, dict_to_argtuples

ATTR_NAMES = ("nnn", "x", "y", "kk", "n")


@pytest.mark.parametrize( "attr_name",ATTR_NAMES)
def test_setters_raise_typeerror_on_bad_type(
        attr_name,
):
    i = Instruction()

    with pytest.raises(TypeError):
        setattr(i, attr_name, 2.0)


BIGGER_THAN_4_BIT = (0x10, 0xF0)
@pytest.mark.parametrize(
    "attr_name,too_big_values",
    (
        ("nnn", (0xFFFF, 0xFFFFFF)),
        ("n", BIGGER_THAN_4_BIT),
        ("x", BIGGER_THAN_4_BIT),
        ("y", BIGGER_THAN_4_BIT),
        ("kk", (0x100, 0xF00, 0xFFF))
    )
)
def test_setters_raise_valueerror_on_too_big(
    attr_name,
    too_big_values
):
    i = Instruction()

    for value in too_big_values:
        with pytest.raises(ValueError):
            setattr(i, attr_name, value)


LESS_THAN_ZERO = (-1, -5)


@pytest.mark.parametrize(
    "attr_name,too_small_value",
    product(
        ATTR_NAMES,
        LESS_THAN_ZERO
    )
)
def test_setters_raise_valueerror_on_too_small(
    attr_name,
    too_small_value
):
    i = Instruction()


    with pytest.raises(ValueError):
        setattr(i, attr_name, too_small_value)


VALID_4BIT = (0x0, 0x1, 0xF)
VALID_8BIT = VALID_4BIT + (0x10, 0xFF)


@pytest.mark.parametrize(
    "attr_name,template,valid_value",
    dict_to_argtuples(
        {
            ("x", 0xE09E): VALID_4BIT,
            ("y", 0x8006): VALID_4BIT,
            ("n", 0xD000): VALID_4BIT,
            ("kk", 0x3000): VALID_8BIT,
            ("nnn", 0x1000): VALID_8BIT + (0xAAA, 0xFFF)
        }
    )
)
def test_valid_values_set_ok(attr_name, template, valid_value):
    i = Instruction(template)

    assert getattr(i, attr_name) == 0
    setattr(i, attr_name, valid_value)
    assert getattr(i, attr_name) == valid_value

