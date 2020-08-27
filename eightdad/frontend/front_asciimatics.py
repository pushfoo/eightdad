import sys
import time  # not sure if I'll actually need this...
from typing import List
from random import randint
from pathlib import Path

from asciimatics.screen import Screen
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.frontend.util import load_rom_to_vm, exit_with_error

def render_screen(screen: Screen, vm: VM, chars: List[str]=[' ', '#']) -> None:
    """
    Helper to render the screen using standard ascii chars.

    Not very fancy, but it's compatible and good enough for basic use.

    :param screen: asciimatics screen to draw to
    :param vm: the Chip 8 VM to source vram from
    :param chars: what tile set to use.
    """
    vram = vm.video_ram
    for x in range(0, vram.width):
        for y in range(0, vram.height):
            # this uses a coercion hack, False = 0, True = 1.
            screen.print_at(chars[vram[x,y]], x, y)

def run_emu(screen: Screen) -> None:
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

        render_screen(screen, vm)
        screen.refresh()

Screen.wrapper(run_emu)
