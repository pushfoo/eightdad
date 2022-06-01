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

from asciimatics.screen import Screen
from eightdad.core import Chip8VirtualMachine
from eightdad.frontend import Frontend
from eightdad.frontend.common.util import screen_coordinates


# unicode escape codes for full block and half block characters. the
# half-block characters allow a console to emulate square pixels by
# assigning a single character to display two pixels and then filling
# it with the appropriate characters.
FULL = "\u2588"
HALF_TOP = "\u2580"
HALF_LOW = "\u2584"


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
        colours=DEFAULT_COLORS
) -> None:
    """
    Render the screen with half-height block characters.

    :param screen: which screen to draw to
    :param vm: a chip 8 VM to render the screen of
    :param x_start: where to start drawing the display area
    :param y_start: where  to start drawing the display area
    :param colours: a list of asciimatics colors to draw with.
    """
    vram = vm.video_ram
    for x, y in screen_coordinates(vm, y_step=2):
        screen.print_at(
            HALF_TOP,
            x_start + x, y_start + y // 2,
            colour=colours[vram[x, y]],
            bg=colours[vram[x, y + 1]]
        )


class AsciimaticsFrontend(Frontend):

    def __init__(self, render_method=render_halfchars):
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
            ev = screen.get_key()
            if ev in (ord('H'), ord('h')):
                return

            if ev == ord('p'):
                self.paused = not self.paused

            if not self.paused:
                if ev in self.key_mapping:
                    self._vm.press(self.key_mapping[ev])

                for i in range(self._vm.ticks_per_frame):
                    self._vm.tick()

                if ev in self.key_mapping:
                    self._vm.release(self.key_mapping[ev])

            self.render_method(screen, self._vm)
            screen.refresh()


def main() -> None:
    # keeping these separate prevents Screen from swallowing argparse errors
    front = AsciimaticsFrontend()
    Screen.wrapper(front.run)


if __name__ == "__main__":
    main()
