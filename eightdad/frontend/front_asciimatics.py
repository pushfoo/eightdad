"""
Rough console-capable emulator frontend.

This probably won't be as good as running on a GL-backed frontend, but
it will run in places it won't. I'm mostly writing this as a way to
improve my vim skills. It also doesn't use pure ncurses but that is
neither easy or cross-platform.

This may not be the final terminal frontend as asciimatics seems to
have its own issuse that I am not yet certain of the best way to
work around.

Implemented so far:
    [x] rough non-square pixel rendering system
    [x] half-height rendering to fake square pixels
    [ ] braille unicode rendering
    [ ] optimizations for only drawing changed pixels

"""
import sys
from typing import List
from random import randint
from pathlib import Path

from asciimatics.screen import Screen
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.frontend.util import (
        load_rom_to_vm, exit_with_error, screen_coordinates
)


FULL = "\u2588"
HALF_TOP = "\u2580"
HALF_LOW = "\u2584"


DEFAULT_COLORS = [
    Screen.COLOUR_BLACK,
    Screen.COLOUR_WHITE
]


def render_fullchars(
        screen: Screen,
        vm: VM,
        x_start: int = 0, y_start: int = 1,
        colours=DEFAULT_COLORS,
        block_char: str = FULL) -> None:
    """
    Helper to render the screen using full-height ascii chars.

    Not very fancy, but it's probably compatible with everything.

    :param screen: asciimatics screen to draw to
    :param vm: the Chip 8 VM to source vram from
    :param x_start: where to start drawing the display area
    :param y_start: where to to start drawing the display area
    :param colours: a list of asciimatics colors to draw in
    :param chars: what tile set to use.
    """
    vram=vm.video_ram
    for x,y in screen_coordinates(vm):
        screen.print_at(
            block_char if vram[x,y] else ' ',
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
    
    :param scren: which screen to draw to
    :param vm: a chip 8 VM to render the screen of
    :param x_start: where to start drawing the display area
    :param y_start: where to to start drawing the display area
    :param colours: a list of asciimatics colors to draw in
    """
    vram=vm.video_ram
    for x,y in screen_coordinates(vm, y_step = 2):
        screen.print_at(
                HALF_TOP,
                x_start + x,y_start + y // 2,
                colour=colours[vram[x,y]],
                bg=colours[vram[x,y+1]]
        )


def run_emu(screen: Screen, render_method=render_halfchars) -> None:
    """
    Asciimatics runner function to wrap, render the screen

    """
    rom_filename = Path(sys.argv[1]).resolve().expanduser()
    screen.print_at(f"Got rom {rom_filename!r}, press any key to continue...", 0, 0)
    ev = screen.get_key()
    
    vm = VM()
    try:
        load_rom_to_vm(rom_filename, vm)
    except IOError as e:
        exit_with_error(f"Could not read {rom_filename!r}: {e!r}")
    except IndexError as e:
        exit_with_error(f"Rom size appears incorrect: {e!r}")

    paused = False

    while True:
        
        ev = screen.get_key()
        if ev in (ord('Q'), ord('q')):
            return
        
        if ev == ord(' '):
            paused = not paused

        if not paused:
            vm.tick(1/20.0)

        render_method(screen, vm)
        screen.refresh()



Screen.wrapper(run_emu)
