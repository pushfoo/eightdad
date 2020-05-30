"""
Test setters on instruction class
"""

import pytest
from eightdad.core.bytecode import Chip8Instruction as Instruction


@pytest.mark.parametrize(
    "attr_name",
    ("nnn", "x", "y", "kk", "n")
)
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
