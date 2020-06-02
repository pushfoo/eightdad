"""

Test ValidateInt decorator class.

"""
import pytest

from eightdad.core.util import ValidateInt


@pytest.mark.parametrize(
    "lower_bound,value_outside_of_it",
    (
        (2, 1),
        (0, -5)
    )
)
def test_valuerror_when_below_valid_range(lower_bound, value_outside_of_it):
    """
    Raises ValueError on attempts to set a value below the allowed range
    """

    class Foo:
        def __init__(self, bar: int = 0):
            self._bar = bar

        @property
        def bar(self):
            return self._bar

        @bar.setter
        @ValidateInt(lower_bound, 16)
        def bar(self, value):
            self._bar = value

    foo = Foo()
    with pytest.raises(ValueError):
        foo.bar = value_outside_of_it


@pytest.mark.parametrize(
    "upper_bound,value_outside_of_it",
    (
        (16, 18),
        (0xFFF, 0xFFFF)
    )
)
def test_valuerror_when_above_valid_range(
        upper_bound,
        value_outside_of_it
):
    """
    Raises ValueError on attempts to set a value above the allowed range
    """

    class Foo:
        def __init__(self, bar: int = 0):
            self._bar = bar

        @property
        def bar(self):
            return self._bar

        @bar.setter
        @ValidateInt(0, upper_bound)
        def bar(self, value):
            self._bar = value

    foo = Foo()
    with pytest.raises(ValueError):
        foo.bar = value_outside_of_it


@pytest.mark.parametrize("bad_type", (2.0, "bad", b"bad"))
def test_typerror_when_wrong_type(bad_type):
    """
    Raises ValueError on attempts to set a non-int value
    """

    class Foo:
        def __init__(self, bar: int = 0):
            self._bar = bar

        @property
        def bar(self):
            return self._bar

        @bar.setter
        @ValidateInt(0, 16)
        def bar(self, value):
            self._bar = value

    foo = Foo()
    with pytest.raises(TypeError):
        foo.bar = bad_type


@pytest.mark.parametrize(
    "good_value,upper,lower"
)
def no_error_on_correct_values(good_value, upper, lower):
    """
    Sets good values correctly without error
    """
    class Foo:
        def __init__(self, bar: int = 0):
            self._bar = bar

        @property
        def bar(self):
            return self._bar

        @bar.setter
        @ValidateInt(lower, upper)
        def bar(self, value):
            self._bar = value

    instance = Foo()
    instance.bar = good_value
    assert instance.bar == good_value
