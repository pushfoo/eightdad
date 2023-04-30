import pytest

from typing import Generator, Tuple
from itertools import product

from eightdad.core import VideoRam

ALLOW_SKIP_WHEN_DEBUGGER_ENABLED = True


def should_skip_because_debugger_active() -> bool:
    """
    Skip if a debugger is believed to be active.

    C-backed functions which allocate RAM are not guaranteed to return zeroed
    RAM on all systems. In some cases, Some functions, specifically ones which
    allocate C-backed RAM, will pre-zero RAM when called from within a debugger.
    This means any test for zeroing RAM will always pass inside such a debugger.
    :return:
    """
    return ALLOW_SKIP_WHEN_DEBUGGER_ENABLED and pytest.helpers.debugger_active()


def all_coordinates(vram: VideoRam) -> Generator[Tuple[int, int], None, None]:
    """
    Syntactic sugar abstracting iteration over all pixels

    :param vram: the video ram to get width and height from
    """
    width, height = vram.width, vram.height
    for coord in product(range(width), range(height)):
        yield coord


VALID_SINGLE_DIM_VALUES = (1, 3, 20)
INVALID_SINGLE_DIM_VALUES = (0, -1, 3)
INVALID_DIM_PAIRS = tuple(filter(
    lambda pair: pair[0] <= 0 or pair[1] <= 0,
    product(INVALID_SINGLE_DIM_VALUES, INVALID_SINGLE_DIM_VALUES)
))


@pytest.mark.parametrize("wrap", [True, False])
class TestInitArgumentHandling:

    @pytest.mark.parametrize("height", VALID_SINGLE_DIM_VALUES)
    @pytest.mark.parametrize("width", VALID_SINGLE_DIM_VALUES)
    def test_vram_init_sets_valid_values_from_arguments(self, height, width, wrap):
        """Constructor accepts legal values, including edge cases"""
        v = VideoRam(width, height, wrap)

        assert v.width == width
        assert v.height == height
        assert v.wrap == wrap

    @pytest.mark.parametrize("height,width", INVALID_DIM_PAIRS)
    def test_vram_init_rejects_bad_values(self, height, width, wrap):
        """Negative and zero dimensions raise ValueErrors regardless of wrap"""
        if height < 1 or width < 1:
            with pytest.raises(ValueError):
                VideoRam(height, width, wrap)


@pytest.mark.skipif(
    should_skip_because_debugger_active(),
    reason="Debugger believed to zero RAM is active, test is meaningless"
)
def test_vram_zeroes_on_creation():
    """
    *Attempt* to check whether coordinates are cleared on creation.

    IMPORTANT: This assumes the code isn't being run in a debugger!

    Doing so may cause the test to pass erroneously because running c
    extensions with a python debugger may cause allocated memory to
    always be pre-zeroed rather than possibly containing arbitrary data.

    This test also currently assumes 400x400 vram is enough to have a
    reasonable chance of being allocated non-zeroed memory.
    """

    # not sure how big a space is needed to ensure we get unzeroed ram
    v = VideoRam(400, 400)
    for x, y in all_coordinates(v):
        assert not v.pixels[y * v.width + x]


class TestSizeProperty:

    def test_gets_correctly(self):
        """Test that property decorator works for compound property"""
        v = VideoRam(4, 4)
        assert v.size == (4, 4)


class TestXorPixel:

    def test_xor_pixel_sets_correct_values(self):
        """Xoring a pixel draws correctly for both on and off pixels """
        v = VideoRam(3, 5)

        v.xor_pixel(2, 4, True)
        assert v.pixels[14]

        v.xor_pixel(2, 4, True)
        assert not v.pixels[14]

    def test_xor_pixel_signals_switchoffs(self):
        """Xoring a pixel returns correct switch-off signals"""
        v = VideoRam(2, 4)
        assert not v.xor_pixel(1, 3, True)
        assert v.xor_pixel(1, 3, True)

    def test_wrapping_when_set(self):
        """Coordinates exceeding dimensions wrap when wrapping is on"""
        v = VideoRam(2, 2, wrap=True)
        assert v.wrap

        assert not v.xor_pixel(2, 2, True)

        assert v[0, 0]
        assert not v[1, 0]
        assert not v[0, 1]
        assert not v[1, 1]

    def test_wrapping_unset(self):
        """Coordinates exceeding dimensions don't wrap if wrapping is off"""
        v = VideoRam(1, 1)
        assert not v.xor_pixel(1, 1, True)
        assert not v[0, 0]


class TestClear:
    """
    Ensure screen-clearing method works correctly.
    """

    def test_clear_turns_off_pixels(self):
        """Pixels turned on are switched off"""
        v = VideoRam(21, 21)

        for pixel_index in range(len(v.pixels)):
            if pixel_index % 2:
                v.pixels[pixel_index] = True

        v.clear_screen()
        for x, y in all_coordinates(v):
            assert not v[x, y]

    def test_clear_does_not_turn_on_pixels(self):
        """Clearing does not activate any pixels that were already off"""
        v = VideoRam(20, 20)

        v.clear_screen()

        for x, y in all_coordinates(v):
            assert not v.pixels[y * v.width + x]


class TestDraw:
    """
    Test draw function handling basic sprites, aka up to 8x15
    """

    def test_multiple_lines(self):
        """Multi-line sprites are drawn correctly"""
        v = VideoRam(8, 16)

        v.draw_sprite(0, 0, b"\xAA\x55" * 8)  # checkerboard

        # verify integrity of checkerboard
        for x, y in all_coordinates(v):
            if not y % 2:
                assert v[x, y] != bool(x % 2)
            else:
                assert v[x, y] == bool(x % 2)

    def test_drawing_blank_doesnt_unset_pixels(self):
        """Drawing a blank sprite doesn't unset pixels"""
        v = VideoRam(8, 8)

        # fill pixels
        for i in range(len(v.pixels)):
            v.pixels[i] = True

        # blit a blank sprite
        v.draw_sprite(0, 0, b"\0" * v.height)

        # ensure all pixels are still on
        for pixel_value in v.pixels:
            assert pixel_value

    def test_drawing_blank_sprite_doesnt_report_unsetting_pixels(self):
        """Drawing a blank sprite doesn't unset pixels in the affected area"""
        v = VideoRam(8, 4)

        # Turn all pixels on
        for i in range(len(v.pixels)):
            v.pixels[i] = True

        assert not v.draw_sprite(0, 0, b"\0" * v.height)

    def test_offset_works(self):
        """Offset from start of byte source works"""
        data = b"\0\xD0\0"
        v = VideoRam(8, 1)
        v.draw_sprite(0, 0, data, offset=1)

        assert v.pixels.tobytes() == b"\xD0"

    def test_num_bytes_works(self):
        """Ensure num_bytes limits how many bytes are drawn"""
        data = bytearray(b"\xA0\xFF")

        v = VideoRam(8, 3)
        v.draw_sprite(0, 1, data, num_bytes=1)
        assert b"\0\xA0\0" == v.pixels.tobytes()
