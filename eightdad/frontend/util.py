from pathlib import Path
from eightdad.core import Chip8VirtualMachine as VM
from typing import Union


PathOrStr = Union[Path, str]


def load_rom_to_vm(path: PathOrStr, vm: VM, location: int = 0x200) -> None:
    """
    Utility function to load a rom to a VM's memory space.

    Raises an error if it's too big for the allotted VM.
    """
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


def exit_with_error(msg: str, error_code: int=1) -> None:
    """
    Display an error message and exit loudly with error code

    :param msg: message to display
    :param error_code: return error code to give to the shell
    :return:
    """
    print(f"ERROR: {msg}", file=sys.stderr)
    exit(error_code)

