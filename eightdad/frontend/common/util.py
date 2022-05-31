import sys
from pathlib import Path
from eightdad.core import Chip8VirtualMachine as VM
from typing import Union, Iterator, Tuple


PathOrStr = Union[Path, str]


def screen_coordinates(
        vm: VM,
        x_step: int = 1,
        y_step: int = 1
    ) -> Iterator[Tuple[int, int]]:
    """
    Sugar method for generating all screen coordinates for a VM's vram.

    :param vm: the VM to access the video ram for
    :param x_step: how much to step x by each time
    :param y_step: how much to step y by each time
    """
    vram = vm.video_ram
    for x in range(0, vram.width, x_step):
        for y in range(0, vram.height, y_step):
            yield (x, y)


def clean_path(raw_path: PathOrStr) -> Path:
    """
    Clean a given path into an expanded system path.

    :param raw_path: the possible string to ensure is a path
    :return:
    """
    return Path(raw_path).resolve().expanduser()


def load_rom_to_vm(
        path: PathOrStr,
        vm: VM = None,
        location: int = 0x200
) -> VM:
    """
    Utility function to load a rom to a VM's memory space.

    If the VM isn't provided, one is created.

    Raises an error if it's too big for the allotted VM.
    """
    path = clean_path(path)

    vm = vm or VM()

    with open(path, "rb") as rom_file:
        rom_data = rom_file.read()
        rom_size = len(rom_data)
        mem_size = len(vm.memory)

        if rom_size > mem_size - vm.program_counter:
            raise IndexError(
                    f"Rom file too big!"
                    f"{rom_size} > {mem_size - vm.program_counter}"
            )
    vm.load_to_memory(rom_data, location)
    return vm

