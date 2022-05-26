import sys
from abc import ABC, abstractmethod

from eightdad.core import Chip8VirtualMachine
from eightdad.core.vm import VMState, upper_hex
from eightdad.frontend.keymap import build_hexkey_mapping
from eightdad.frontend.util import clean_path, load_rom_to_vm


def exit_with_error(msg: str, error_code: int = 1) -> None:
    """
    Display an error message and exit loudly with error code

    :param msg: message to display
    :param error_code: return error code to give to the shell
    :return:
    """
    print(f"ERROR: {msg}", file=sys.stderr)
    exit(error_code)


class Frontend(ABC):
        """
        Common base to wrap other frontend systems.

        Inherit from it to set up your own frontends.
        """
        def __init__(self):
            self.rom_path = None
            self._vm: Chip8VirtualMachine = self.load_vm()
            self._display_filename = None

            self.breakpoints = None
            self._tick_rate = 1.0 / 30
            self._key_mapping = build_hexkey_mapping()

            self.load_vm()

        def load_vm(self) -> Chip8VirtualMachine:
            path = clean_path(sys.argv[1])

            try:
                self._vm = load_rom_to_vm(path)
            except IOError as e:
                exit_with_error(f"Could not read file {path!r} : {e!r}")
            except IndexError as e:
                exit_with_error(f"Could not load rom: {e!r}")

            self._display_filename = path.stem + ''.join(path.suffixes)
            self.breakpoints = set()

        @abstractmethod
        def run(self):
            raise NotImplementedError()

        @property
        def tick_rate(self) -> float:
            return self._tick_rate

        @tick_rate.setter
        def tick_rate(self, new_rate):
            self._tick_rate = new_rate

FRONTENDS = {}