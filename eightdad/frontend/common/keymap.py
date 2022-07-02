import enum
from typing import Dict, TypeVar


@enum.unique
class ControlButton(enum.Enum):
    HEX_0 = 0x0
    HEX_1 = 0x1
    HEX_2 = 0x2
    HEX_3 = 0x3
    HEX_4 = 0x4
    HEX_5 = 0x5
    HEX_6 = 0x6
    HEX_7 = 0x7
    HEX_8 = 0x8
    HEX_9 = 0x9
    HEX_A = 0xA
    HEX_B = 0xB
    HEX_C = 0xC
    HEX_D = 0xD
    HEX_E = 0xE
    HEX_F = 0xF
    QUIT = enum.auto()
    PAUSE = enum.auto()
    STEP = enum.auto()


# default mapping
DEFAULT = (
    (ControlButton.HEX_1, '1'),
    (ControlButton.HEX_2, '2'),
    (ControlButton.HEX_3, '3'),
    (ControlButton.HEX_C, '4'),
    (ControlButton.HEX_4, 'q'),
    (ControlButton.HEX_5, 'w'),
    (ControlButton.HEX_6, 'e'),
    (ControlButton.HEX_D, 'r'),
    (ControlButton.HEX_7, 'a'),
    (ControlButton.HEX_8, 's'),
    (ControlButton.HEX_9, 'd'),
    (ControlButton.HEX_E, 'f'),
    (ControlButton.HEX_A, 'z'),
    (ControlButton.HEX_0, 'x'),
    (ControlButton.HEX_B, 'c'),
    (ControlButton.HEX_F, 'f'),
    (ControlButton.PAUSE, ' '),
    (ControlButton.QUIT, 'h'),
    (ControlButton.STEP, 'i')
)


def to_lower(key_code: int) -> int:
    """
    Transform any upper case key codes to their lower case versions.

    This is mostly useful for TUI but there may be frameworks which do
    not pre-process key codes.

    :param key_code: a key scan code
    :return: the lower case version of it, if it was an upper case letter
    """

    if 65 <= key_code <= 90:
        key_code += 32

    return key_code


EnumType = TypeVar('EnumType', bound=enum.Enum)
KeyMap = Dict[int, EnumType]


def finalize_key_map(config: Dict[EnumType, str]) -> KeyMap:
    """
    Convert from a config to a mapping of key codes to Enum values.

    This works for both asciimatics and arcade since they both use
    the ordinal unicode value for keys in their key press
    representations.

    :param config: a dict object
    :return:
    """
    return {to_lower(ord(char)): action for action, char in config.items()}


def load_key_map() -> KeyMap:
    """
    Return a usable key map regardless of whether a file was found.

    For now, this only returns the default key map.

    :return:
    """
    return finalize_key_map(dict(DEFAULT))
