"""
Test setters on instruction class
"""
import pytest
from eightdad.core.bytecode import Chip8Instruction as Instruction

dict_to_argtuples = pytest.helpers.dict_to_argtuples
ATTR_NAMES = ("nnn", "x", "y", "kk", "n")


@pytest.mark.parametrize("attr_name", ATTR_NAMES)
def test_setters_raise_typeerror_on_bad_type(
    attr_name,
):
    """Setting non-int types results in errors"""
    i = Instruction()

    with pytest.raises(TypeError):
        setattr(i, attr_name, 2.0)


BIGGER_THAN_4_BIT = (0x10, 0xF0)


@pytest.mark.parametrize(
    "attr_name,too_big_value",
    dict_to_argtuples({
        ("nnn",): (0xFFFF, 0xFFFFFF),
        ("n",):  BIGGER_THAN_4_BIT,
        ("x",): BIGGER_THAN_4_BIT,
        ("y",): BIGGER_THAN_4_BIT,
        ("kk",): (0x100, 0xF00, 0xFFF)
    })
)
def test_setters_raise_valueerror_on_too_big(
    attr_name,
    too_big_value
):
    """Raises ValueError on attempts to set values that are too high"""
    i = Instruction()

    with pytest.raises(ValueError):
        setattr(i, attr_name, too_big_value)


LESS_THAN_ZERO = (-1, -5)


@pytest.mark.parametrize('attr_name', ATTR_NAMES)
@pytest.mark.parametrize('too_small_value', LESS_THAN_ZERO)
def test_setters_raise_valueerror_on_too_small(
    attr_name,
    too_small_value
):
    """Raises ValueError on attempts to set values that are too low"""
    i = Instruction()

    with pytest.raises(ValueError):
        setattr(i, attr_name, too_small_value)


VALID_4BIT = (0x0, 0x1, 0xF)
VALID_8BIT = VALID_4BIT + (0x10, 0xFF)
VALID_12BIT = VALID_4BIT + (0xAAA, 0xFFF)


@pytest.mark.parametrize(
    "attr_name,template,valid_value",
    dict_to_argtuples(
        {
            ("x", 0xE09E): VALID_4BIT,
            ("y", 0x8006): VALID_4BIT,
            ("n", 0xD000): VALID_4BIT,
            ("kk", 0x3000): VALID_8BIT,
            ("nnn", 0x1000): VALID_12BIT
        }
    )
)
def test_valid_values_set_ok(attr_name, template, valid_value):
    """Sets values correctly"""
    i = Instruction(template)

    assert getattr(i, attr_name) == 0
    setattr(i, attr_name, valid_value)
    assert getattr(i, attr_name) == valid_value

