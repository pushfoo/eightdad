import functools
from typing import Callable, Any


class ValidateInt:
    """

    Decorator class that validates integers passed to setters.

    It's intended to be used before they are set as properties,
    but in the future condensing the property marker into this
    would be worthwhile. Not quite sure how to do that.

    """
    def __init__(
        self,
        lower_bound: int,
        upper_bound: int
    ):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __call__(self, f: Callable[[Any, int], None]) -> None:
        """

        :param f:
        :return:
        """

        @functools.wraps(f)
        def wrapper(wrapped_self, value):

            if not isinstance(value, int):
                raise TypeError(
                    f"{f.__name__} must be an int, not a {value}"
                )

            if value < self.lower_bound or self.upper_bound < value:
                raise ValueError(
                    f"{f.__name__} must be between "
                    f"{self.lower_bound} and {self.upper_bound}, "
                    f"inclusive"
                )
            f(wrapped_self, value)

        return wrapper

