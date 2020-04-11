"""

Video Ram and default sprite data

No user-facing rendering code should be stored in this module.

"""
from typing import Tuple
from itertools import islice
from bitarray import util as ba_util

DEFAULT_DIGITS = [
    b'\xf0\x90\x90\x90\xf0',
    b'\x20\x60\x20\x20\x70',
    b'\xf0\x10\xf0\x80\xf0',
    b'\xf0\x10\xf0\x10\xf0',
    b'\x90\x90\xf0\x10\x10',
    b'\xf0\x80\xf0\x10\xf0',
    b'\xf0\x80\xf0\x90\xf0',
    b'\xf0\x10\x20\x40\x40',
    b'\xf0\x90\xf0\x90\xf0',
    b'\xf0\x90\xf0\x10\xf0',
    b'\xf0\x90\xf0\x90\x90',
    b'\xe0\x90\xe0\x90\xe0',
    b'\xf0\x80\x80\x80\xf0',
    b'\xe0\x90\x90\x90\xe0',
    b'\xf0\x80\xf0\x80\xf0',
    b'\xf0\x80\xf0\x80\x80'
]

class VideoRam:
    """
    A 1-bit display memory that abstracts drawing chip-8 sprite data.

    It is intended for both implementing a Chip-8 VM and writing prototypes of
    Chip-8 programs in python.

    """
    def __init__(self, width: int = 64, height: int = 32, wrap: bool = False):
        """
        Create a VideoRam instance.

        If wrap is true, any pixels drawn off the edge of the screen will get
        wrapped to the start of the screen.

        :param width: video display size in pixels
        :param height: video display size in pixels
        :param wrap: whether to wrap out-of-bounds drawing to the other side
        """
        if width < 1 or height < 1:
            raise ValueError("Video memory dimensions must be at least 1px")

        self.width = width
        self.height = height
        self.wrap = wrap

        # Note that the endian argument here is *bit* endianness specifying
        # bit order, not the byte endianess you normally see. See the bitarray
        # documentation for more details.
        self.pixels = ba_util.zeros(width * height, endian='big')

    @property
    def size(self) -> Tuple[int, int]:
        """
        Return the size as a tuple
        :return: Tuple[int, int] of width and height
        """
        return self.width, self.height

    def __getitem__(self, coordinates: Tuple[int, int]) -> bool:
        """
        Convenient access to pixels in the form video_ram[x,y]

        :param coordinates: the tuple of integers passed
        :return: the pixel state at the given coordinate
        """
        x, y = coordinates
        return self.pixels[y * self.width + x]

    def xor_pixel(self, x: int, y: int, value: bool) -> bool:
        """
        Set (x,y) to current_value ^ value, return True if turned (x,y) off.

        if (x,y) is out of bounds, return false unless wrap is set. If it is
        set, wrap the dimensions that exceed the video ram size.

        :param x: x position to draw at
        :param y: y position to draw at
        :param value: the value to xor the pixel with
        :return: true only if the call unset a pixel
        """

        if x >= self.width:
            if not self.wrap:
                return False
            x = x % self.width

        if y >= self.height:
            if not self.wrap:
                return False
            y = y % self.height

        pixels = self.pixels

        # stores pixel index rather than using get/setitem because it's faster
        pixel_index = (y * self.width) + x

        old_value = pixels[pixel_index]
        pixels[pixel_index] = old_value ^ value
        return old_value & value

    def clear_screen(self):
        """
        Clear the screen, setting it to blank.

        :return:
        """
        self.pixels.setall(False)

    def draw_sprite(
            self,
            x: int,
            y: int,
            source_bytes,
            num_bytes: int = 0,
            offset: int = 0) -> bool:
        """

        Draw an 8-pixel-wide sprite from the passed source to video memory.
        Returns true if any pixels were turned off by the operation.

        Assumes all bytes should be drawn unless an offset or number of bytes
        are specified.

        If an offset is specified, skip that many bytes before drawing begins.
        If num_bytes is specified, only draw that many bytes, starting after
        the offset if it was specified.

        :param x: the x-position to start drawing at
        :param y: the y-position to start drawing at
        :param source_bytes: the source object to use for bytes
        :param num_bytes: length of the draw to use in bytes, aka height
        :param offset: the offset from the start to draw from
        :return: whether or any pixels were unset by this draw operation
        """

        bits_were_unset = False
        num_bytes = num_bytes or len(source_bytes) - offset

        source_iterator = islice(source_bytes, offset, offset + num_bytes)

        for current_y in range(y, y + num_bytes):
            current_byte = next(source_iterator)
            for current_x in range(x, x + 8):
                # get the current pixel
                current_bit = bool(0b10000000 & current_byte)

                # only draw if pixel isn't blank
                if current_bit:
                    bits_were_unset |= self.xor_pixel(
                        current_x,
                        current_y,
                        current_bit
                    )

                # next bit
                current_byte <<= 1

        return bits_were_unset


def print_vram(
        vram: VideoRam,
        pixel_on: str = "#",
        pixel_off: str = " ") -> None:
    """
    Debug method to visualize current state, useful to call from debugger

    :param pixel_on: character to draw on pixels with
    :param pixel_off: character to draw off pixels with
    """

    characters = []

    pixel_pos = 0

    for y in range(vram.height):
        for x in range(vram.width):
            if vram.pixels[pixel_pos]:
                characters.append(pixel_on)
            else:
                characters.append(pixel_off)
            pixel_pos += 1
        characters.append("\n")

    print("".join(characters))
