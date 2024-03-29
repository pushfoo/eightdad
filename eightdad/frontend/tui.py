"""
Rough cross-platform console mode emulator frontend.

It will work on Windows, but relies on a third party library to do so.

It will never support key-up events due to the way the unix terminal
evolved. See the following blog post for more info:
https://blog.robertelder.org/detect-keyup-event-linux-terminal/

Implemented so far:
    [x] rough non-square pixel rendering system
    [x] half-height rendering to fake square pixels
    [ ] braille unicode rendering
    [ ] optimizations for only drawing changed pixels

"""
from typing import Tuple

from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from eightdad.core import Chip8VirtualMachine
from eightdad.frontend import Frontend
from eightdad.frontend.common.util import screen_coordinates
from eightdad.frontend.common.keymap import ControlButton, to_lower

# unicode escape codes for full block and half block characters. the
# half-block characters allow a console to emulate square pixels by
# assigning a single character to display two pixels and then filling
# it with the appropriate characters.
FULL = "\u2588"
HALF_TOP = "\u2580"
HALF_LOW = "\u2584"


# Default characters for displaying squarish pixels using half-height
# characters. Implemented as a tuple with arithmetic selection to
# reduce dependencies and avoid mutable default args.
HALF_CHAR_TABLE = (
    ' ',
    HALF_TOP,
    HALF_LOW,
    FULL
)


DEFAULT_COLORS = (
    Screen.COLOUR_BLACK,
    Screen.COLOUR_WHITE
)


def render_fullchars(
        screen: Screen,
        vm: Chip8VirtualMachine,
        x_start: int = 0, y_start: int = 1,
        colours=DEFAULT_COLORS,
        block_char: str = FULL) -> None:
    """
    Helper to render the screen using full-height characters.

    Unless the user has set up a square font for their console, this
    will likely show up as non-square pixels in the terminal.

    Not very fancy, but it's probably compatible with everything. If
    for some reason you are using this on a system that doesn't support
    unicode characters or background colors, you can set block_char to
    something like '#' and the display should still work.

    :param screen: asciimatics screen to draw to
    :param vm: the Chip 8 Chip8VirtualMachine to source vram from
    :param x_start: where to start drawing the display area
    :param y_start: where to to start drawing the display area
    :param colours: a list of asciimatics colors to draw in
    :param block_char: what tile to use for showing a full pixel.
    """
    vram = vm.video_ram
    for x, y in screen_coordinates(vm):
        screen.print_at(
            block_char if vram[x, y] else ' ',
            x + x_start, y + y_start,
            colour=colours[1],
            bg=colours[0]
        )


def render_halfchars(
        screen: Screen,
        vm: Chip8VirtualMachine,
        x_start: int = 0, y_start: int = 1,
        colours=DEFAULT_COLORS,
        char_table: Tuple[str] = HALF_CHAR_TABLE,
) -> None:
    """
    Render the screen with half-height block characters.

    :param screen: which screen to draw to
    :param vm: a chip 8 VM to render the screen of
    :param x_start: where to start drawing the display area
    :param y_start: where  to start drawing the display area
    :param colours: a list of asciimatics colors to draw with.
    :param char_table:
    """
    vram = vm.video_ram
    for x, y in screen_coordinates(vm, y_step=2):
        char_selection = 0

        # Use the current pixel and the one below it to choose the
        # character for the current tile
        if vram[x, y]:
            char_selection += 1
        if vram[x, y + 1]:
            char_selection += 2

        screen.print_at(
            char_table[char_selection],
            x_start + x, y_start + y // 2,
            colour=colours[1],
            bg=colours[0]
        )

BRAILLE_TABLE = (
    (0, 0, 1),
    (0, 1, 2),
    (0, 2, 4),
    (1, 0, 8),
    (1, 1, 16),
    (1, 2, 32),
    (0, 3, 64),
    (1, 3, 128)
)

def render_braille(
        screen: Screen,
        vm: Chip8VirtualMachine,
        draw_x_start: int = 0, draw_y_start: int = 1,
        colours=DEFAULT_COLORS,
        char_table: Tuple[int, int, int] = BRAILLE_TABLE,
) -> None:
    vram = vm.video_ram
    for x, y in screen_coordinates(vm, x_step=2, y_step=4):
        char_base_codepoint = 0x2800

        for offset_x, offset_y, bit_mask in char_table:
            if vram[x + offset_x, y + offset_y]:
                char_base_codepoint += bit_mask

        screen.print_at(
            chr(char_base_codepoint),
            draw_x_start + (x // 2), draw_y_start + (y // 4),
            colour=colours[1],
            bg=colours[0]
        )


class AsciimaticsFrontend(Frontend):

    def __init__(self, render_method=render_braille):
        super().__init__()
        self.screen = None
        self.render_method = render_method
        self._paused = self.launch_args['start_paused']

    @property
    def paused(self) -> bool:
        return self._paused

    @paused.setter
    def paused(self, pause: bool):
        self._paused = pause

    def run(self, screen: Screen = None) -> None:
        """
        Asciimatics helper function to drive the emulator.
        """
        screen = screen or self.screen

        while True:
            ev = screen.get_event()

            # handle debug & app keys
            key_pressed = isinstance(ev, KeyboardEvent)

            mapped_button = None
            if key_pressed:
                mapped_button = self.key_mapping.get(
                    to_lower(ev.key_code), None)

            if key_pressed:
                screen.print_at(f"Pressed: {mapped_button}", x=0, y=0)
                if mapped_button is ControlButton.QUIT:
                    return

                if mapped_button is ControlButton.PAUSE:
                    self.paused = not self.paused

            # run the frame
            if not self.paused:

                hex_value = None
                if mapped_button and mapped_button.name.startswith('HEX_'):
                    hex_value = mapped_button.value

                if hex_value is not None:
                    self._vm.press(hex_value)

                for i in range(self._vm.ticks_per_frame):
                    self._vm.tick()

                # an ugly way to emulate key-up events in the terminal
                if hex_value is not None:
                    self._vm.release(hex_value)

            self.render_method(screen, self._vm)
            screen.refresh()


def main() -> None:
    # keeping these separate prevents Screen
    # from swallowing important argparse errors.
    front = AsciimaticsFrontend()
    Screen.wrapper(front.run)


if __name__ == "__main__":
    main()
