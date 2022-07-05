from array import array
from collections.abc import ByteString
from typing import Union
from bitarray import bitarray


# Buffer protocol implementations likely to be used in this project
Buffer = Union[ByteString, memoryview, array, bitarray]


class DigitFormatException(ValueError):
    pass


class DigitTooTall(DigitFormatException):
    pass


class DigitTooWide(DigitFormatException):
    pass
