import enum
from eightdad.frontend.common.keymap import finalize_key_map


class Example(enum.Enum):
    A = 1
    B = 2


EXAMPLE_MAPPING = (
    (Example.A, 'A'),
    (Example.B, 'B')
)


def test_finalize_key_map():
    m = finalize_key_map(dict(EXAMPLE_MAPPING))
    # these should be lower case
    assert m == {
        97: Example.A,
        98: Example.B
    }
