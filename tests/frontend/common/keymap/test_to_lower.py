import pytest
from eightdad.frontend.common.keymap import to_lower


@pytest.mark.parametrize(
    'key_code_in, expected',
    (
        # check transformation of upper case
        (ord('A'), ord('a')),  # edge case: lower boundary
        (ord('Z'), ord('z')),  # edge case: upper boundary
        (ord('Q'), ord('q')),
        # check idempotency for lower case & non-alpha key codes
        (ord('a'), ord('a')),
        (ord('z'), ord('z')),
        (ord('q'), ord('q')),
        (ord('@'), ord('@'))
    )
)
def test_to_lower(key_code_in, expected):
    assert to_lower(key_code_in) == expected
