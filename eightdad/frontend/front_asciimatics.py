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
import sys

from asciimatics.screen import Screen
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.frontend.keymap import build_hexkey_mapping
from eightdad.frontend.util import (
    load_rom_to_vm, exit_with_error, screen_coordinates, clean_path)

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
        vm: VM,
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
    :param vm: the Chip 8 VM to source vram from
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
        vm: VM,
        x_start: int = 0, y_start: int = 1,
        colours=DEFAULT_COLORS
) -> None:
    """
    Render the screen with half-height block characters.
    
    :param screen: which screen to draw to
    :param vm: a chip 8 VM to render the screen of
    :param x_start: where to start drawing the display area
    :param y_start: where to to start drawing the display area
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


def run_emu(screen: Screen, render_method=render_halfchars) -> None:
    """
    Asciimatics runner function to wrap, render the screen

    """
    path = clean_path(sys.argv[1])
    try:
        vm = load_rom_to_vm(path)
    except IOError as e:
        exit_with_error(f"Could not read {path!r} : {e!r}")
    except IndexError as e:
        exit_with_error(f"Rom size appears incorrect: {e!r}")

    paused = False

    # load keymap in an ugly but functional way
    # later versions of this should be a function that
    # takes a converter function to map between keys and
    # their frontend-specific representation. this will
    # make loading generic while still retaining compatibility
    # with various frontends.
    final_keymap = build_hexkey_mapping()

    while True:

        ev = screen.get_key()
        if ev in (ord('H'), ord('h')):
            return

        if ev == ord('p'):
            paused = not paused

        if not paused:
            if ev in final_keymap:
                vm.press(final_keymap[ev])

            for i in range(vm.ticks_per_frame):
                vm.tick()

            if ev in final_keymap:
                vm.release(final_keymap[ev])

        render_method(screen, vm)
        screen.refresh()


Screen.wrapper(run_emu)
